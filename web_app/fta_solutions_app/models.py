# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import json
import re
import urllib
import uuid
from collections import OrderedDict, defaultdict

from django.conf import settings
from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

from common.django_utils import strftime_local
from fta_solutions_app import fta_std
from fta_utils import fsm_client
from project.conf.user import get_short_name


# migrate AlarmApplication 数据会使用到，请勿修改位置
def gen_app_secret():
    """生成app_secret方法
    """
    # chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return get_random_string(32)


def gen_app_id():
    """生成app_id的方法
    """
    return str(uuid.uuid4())


class SolutionManager(models.Manager):

    def get_queryset(self):
        return super(SolutionManager, self).get_queryset().exclude(codename='non-display')


class Solution(models.Model):
    """自愈套餐"""
    objects = SolutionManager()
    default_objects = models.Manager()

    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    solution_type = models.CharField(
        _(u'套餐类型'), max_length=128,
        default='customized',
        choices=fta_std.SOLUTION_TYPE_CHOICES
    )
    codename = models.CharField(
        _(u'英文名称代号'), max_length=128,
        blank=True, null=True
    )
    title = models.CharField(_(u'全名'), max_length=512)
    config = models.TextField(_(u'配置(JSON)'), null=True, blank=True)

    # 待弃用
    creator = models.CharField(_(u'创建者'), max_length=255)

    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    create_user = models.CharField(_(u"创建人"), max_length=32)
    update_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    update_user = models.CharField(_(u"修改人"), max_length=32)
    is_deleted = models.BooleanField(_(u"是否删除"), default=False)

    def save(self, *args, **kwargs):
        # 需要翻译的词标记
        # A_WORD = [_(u"空闲机"), _(u"故障机")]
        # 获取故障备机时，cc的英文转为中文存储
        if self.solution_type == 'get_bak_ip':
            _config = json.loads(self.config)
            moudle_name = _config['module_name']
            _moudle_name_list = moudle_name.split(',')
            new_moudle_name_list = []
            for _moudle_name in _moudle_name_list:
                if _moudle_name == 'Idle machine':
                    new_moudle_name_list.append(u"空闲机")
                elif _moudle_name == 'Fault machine':
                    new_moudle_name_list.append(u"故障机")
                else:
                    new_moudle_name_list.append(_moudle_name)
            new_moudle_name = ','.join(new_moudle_name_list)
            _config['module_name'] = new_moudle_name
            self.config = json.dumps(_config)

        super(Solution, self).save(*args, **kwargs)

    @property
    def title_display(self):
        if not self.title:
            return self.title
        return _(self.title)

    @property
    def get_module_name(self):
        _m = self.config.get('module_name', '')
        if _m:
            m_list = _m.split(',')
            new_list = [_(_n) for _n in m_list]
            return ','.join(new_list)
        return ''

    @classmethod
    def check_title(cls, cc_biz_id, title, solution_id=None):
        """
        同一个业务下的 套餐名称 不可以重复
        """
        if not title:
            return False, _(u"套餐名不能为空")

        if solution_id and str(solution_id) != '0':
            is_exists = Solution.objects.filter(
                cc_biz_id=cc_biz_id, title=title).exclude(
                id=solution_id).exists()
        else:
            is_exists = Solution.objects.filter(
                cc_biz_id=cc_biz_id,
                title=title
            )
        if is_exists:
            return False, _(u"套餐名[%s]已存在") % title
        return True, _(u"校验通过")

    @property
    def creat_uin(self):
        uin = get_short_name(self.creator)
        return uin

    @property
    def alarm_def_list(self):
        """
        关联到AlarmDef的快速写法
        :return QuerySet: AlarmDef
        """
        return AlarmDef.objects.filter(
            solution_id=self.id, cc_biz_id=self.cc_biz_id,
        )

    @property
    def graph(self):
        """
        获取组合套餐的 graph_json 描述
        :return graph_json: [({}, solution_id), ]
        """
        return fsm_client.convert_solution2graph(self)

    def __unicode__(self):
        return unicode('%s-%s' % (self.title, self.codename))


class AlarmDefManager(models.Manager):

    def all(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(AlarmDefManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(AlarmDefManager, self) \
            .filter(*args, **kwargs).filter(is_deleted=False)


class AlarmDef(models.Model):
    """告警定义"""
    ADD_FROM_CHOICES = (
        ('user', _(u"人工配置")),
        ('admin', _(u"管理员配置")),
        ('sys', _(u"系统推荐")),
    )

    objects = AlarmDefManager()

    is_enabled = models.BooleanField(_(u'是否启用'), default=False)
    is_deleted = models.BooleanField(_(u'是否删除'), default=False)
    category = models.CharField(_(u'告警类型'), max_length=32, default='default', choices=fta_std.ALARM_CATEGORY_CHOICES)
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    alarm_type = models.CharField(_(u'告警类型'), max_length=128)
    reg = models.CharField(_(u'正则过滤'), max_length=255, default='', blank=True, null=True)
    process = models.CharField(_(u'进程名称'), max_length=255, default='', blank=True, null=True)
    module = models.TextField(u'Module', default='', blank=True, help_text=_(u"冗余字段"))
    topo_set = models.TextField(u'Set', default='', blank=True, help_text=_(u"冗余字段"))
    set_attr = models.TextField(_(u'Set属性'), default='', blank=True, )
    idc = models.TextField(u'IDC', default='', blank=True, )
    device_class = models.TextField(u'DeviceClass', default='', blank=True)
    responsible = models.CharField(_(u'额外通知人'), max_length=255,
                                   blank=True, null=True)
    title = models.CharField(_(u'全名'), max_length=128, blank=True, null=True)
    description = models.TextField(_(u'备注'), blank=True, null=True)
    ok_notify = models.BooleanField(_(u'成功后是否通知'), default=True)
    notify = models.TextField(_(u'通知配置'), default="{}")
    solution_id = models.IntegerField(null=True, blank=True, db_index=True)
    timeout = models.IntegerField(_(u'超时时长'), default=40)

    # 新告警源的字段
    source_type = models.CharField(
        _(u'告警源'), max_length=32, blank=True, null=True, default='ALERT', choices=fta_std.SOURCE_TYPE_CHOICES
    )
    alarm_attr_id = models.CharField(_(u"告警在来源系统的特征ID"), max_length=128, null=True, blank=True)
    # 保存 cc 相关属性的名称，页面显示时不用再调用接口查询
    set_names = models.TextField(_(u"Set名称"), default='', blank=True)
    module_names = models.TextField(_(u"Module名称"), default='', blank=True)

    # 运营数据添加字段
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    update_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    create_user = models.CharField(_(u"创建人"), max_length=32, default='')
    update_user = models.CharField(_(u"修改人"), max_length=32, default='')
    tnm_attr_id = models.TextField(_(u'排除业务'), default='', blank=True, null=True)
    add_from = models.CharField(_(u"方案来源"), max_length=10, choices=ADD_FROM_CHOICES, default='user')

    @property
    def description_display(self):
        if not self.description:
            return self.description
        return _(self.description)

    @property
    def get_show_name(self):
        if self.description.endswith(u"默认套餐"):
            return "%s%s" % (_(self.description.rstrip(u"默认套餐")), _(u"默认套餐"))
        return self.description

    @property
    def add_from_display(self):
        if not self.add_from:
            return self.get_add_from_display()
        return _(self.get_add_from_display())

    @classmethod
    def default_sort_order(cls, obj):
        return (
            obj.is_enabled, obj.update_time,
            obj.source_type, obj.alarm_type,
        )

    @classmethod
    def is_alert_enabled(cls, cc_biz_id):
        """
        业务下的蓝鲸监控是否已经启用
        未启用则不能接入蓝鲸监控的告警源
        """
        alert_app = AlarmApplication.objects.filter(
            source_type="ALERT",
        ).first()
        if alert_app:
            exclude_biz_list = alert_app.exclude_biz_list
            if cc_biz_id in exclude_biz_list:
                return False
        return True

    @classmethod
    def is_custom_enabled(cls, cc_biz_id=0):
        """
        企业是否已经添加自定义监控
        """
        is_custom_exist = AlarmApplication.objects.filter(
            source_type='CUSTOM',
        ).exists()
        return is_custom_exist

    @classmethod
    def block_by_source_type(cls, cc_biz_id, source_type):
        cls.objects.filter(
            cc_biz_id=cc_biz_id,
            source_type=source_type,
        ).update(
            is_enabled=False,

        )
        # 全业务自愈方案中，将业务id添加到排除列表中
        all_biz_defs = cls.objects.filter(
            cc_biz_id=0,
            source_type=source_type,
        )
        for _def in all_biz_defs:
            block_list = (_def.tnm_attr_id or '').split(',')
            if cc_biz_id not in block_list:
                block_list.append(cc_biz_id)
            _def.tnm_attr_id = ','.join(block_list)
            _def.save()

    @classmethod
    def check_description(cls, cc_biz_id, description, alarm_def_id=None):
        """
        同一个业务下的 description 不可以重复
        """
        if not description:
            return False, _(u"自愈方案名称不能为空")

        if alarm_def_id:
            is_exists = AlarmDef.objects.filter(
                cc_biz_id=cc_biz_id, description=description).exclude(
                id=alarm_def_id).exists()
        else:
            is_exists = AlarmDef.objects.filter(
                cc_biz_id=cc_biz_id,
                description=description
            )
        if is_exists:
            return False, _(u"自愈方案名称[%s]已存在") % description
        return True, _(u"校验通过")

    @property
    def is_real_enabled(self, cc_biz_id):
        """兼容全业务场景
        """
        if self.cc_biz_id:
            return self.is_enabled
        return self.is_enabled and (cc_biz_id not in self.exclude_list)

    @property
    def exclude_list(self):
        return self.tnm_attr_id.split(',') if self.tnm_attr_id else []

    @property
    def get_set_names(self):
        return self.set_names

    @property
    def get_module_names(self):
        return self.module_names

    @property
    def solution(self):
        """
        关联到Solution的快速写法
        :return QuerySet: Solution
        """
        if self.solution_id:
            return Solution.objects.get(id=self.solution_id)

    @property
    def instances(self):
        """
        关联到AlarmInstance的快速写法
        :return QuerySet: AlarmInstance
        """
        return AlarmInstance.objects.filter(alarm_def_id=self.id)

    @property
    def include_url(self):
        """
        获取 AlarmDef URL
        :return include_url: 非绝对路径
        """
        return '%s/alarm_def/%s/' % (self.cc_biz_id, self.id)

    @property
    def include_solution_url(self):
        """
        获取 Solution URL
        :return include_url: 非绝对路径
        """
        if self.solution:
            return '%s/solution/%s/' % (self.cc_biz_id, self.solution.id)

    @property
    def notify_conf(self):
        """
        获取通知的字典配置
        """
        return json.loads(self.notify)

    @property
    def set_attr_show(self):
        """
        获取 SET 属性的展示名称
        """
        NAME_DICT = {
            'service_state-1': u'[服务状态]开放',
            'service_state-2': u'[服务状态]关闭',
            'service_state-3': u'[服务状态]维护',
            'envi_type-1': u'[环境类型]测试',
            'envi_type-2': u'[环境类型]体验',
            'envi_type-3': u'[环境类型]正式',
            'category-0': u'[Set类型]普通集群',
            'category-1': u'[Set类型]游戏集群'
        }
        return ','.join([NAME_DICT.get(set_attr) for set_attr in self.set_attr.split(',')])

    def delete(self, *args, **kwargs):
        """
        删除方法，不会删除数据
        而是通过标记删除字段 is_deleted 来软删除
        """
        self.is_deleted = True
        self.is_enabled = False
        self.solution_id = None
        self.save()

    def __unicode__(self):
        return unicode('%s-%s' % (self.cc_biz_id, self.alarm_type))


class AlarmType(models.Model):
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    is_enabled = models.BooleanField(_(u'是否启用'), default=True)
    is_hidden = models.BooleanField(_(u'是否隐藏'), default=False)
    source_type = models.CharField(_(u"告警来源"), max_length=128, db_index=True)
    alarm_type = models.CharField(_(u"告警类型"), max_length=128, db_index=True)
    pattern = models.CharField(_(u"匹配模式"), max_length=128)
    description = models.TextField(_(u"描述"), blank=True)
    match_mode = models.IntegerField(
        _(u"匹配类型"), default=0,
        choices=(
            (0, _(u"字符串")),
            (1, _(u"正则表达式")),
            (2, _(u"通配符")),
        ),
    )
    exclude = models.TextField(_(u'排除业务'), default='', blank=True)
    scenario = models.CharField(u"告警类型分类", max_length=128, default='', blank=True)

    @property
    def description_display(self):
        if not self.description:
            return self.description
        return _(self.description)

    @property
    def scenario_display(self):
        if not self.scenario:
            return self.scenario
        return _(self.scenario)

    def save(self, *args, **kwargs):
        # 所有的告警类型都设置为全业务
        self.cc_biz_id = 0

        if not self.alarm_type:
            self.alarm_type = uuid.uuid4().hex

        super(AlarmType, self).save(*args, **kwargs)

    @cached_property
    def regex_pattern(self):
        if self.match_mode != 1:
            return None
        return re.compile(self.pattern)

    @property
    def excluded_set(self):
        return set(i.strip() for i in self.exclude.split(",") if i)

    def __unicode__(self):
        return self.description_display

    @property
    def match_mode_desc(self):
        match_mode = self.match_mode
        if match_mode == 0:
            return _(u"字符串")
        elif match_mode == 1:
            return _(u"正则表达式")
        elif match_mode == 2:
            return _(u"通配符")
        else:
            return _(u"其他")

    def exclude_biz(self, cc_biz_id):
        excluded_set = self.excluded_set
        excluded_set.add(str(cc_biz_id))
        self.exclude = ",".join(excluded_set)

    def match(self, value):
        if self.match_mode == 0:
            return self.pattern == value
        elif self.match_mode == 1:
            return self.regex_pattern.match(value) is not None
        elif self.match_mode == 2:
            from fnmatch import fnmatch
            return fnmatch(value, self.pattern)
        return False

    @classmethod
    def get_by_cc_biz_id(cls, cc_biz_id, is_handle_alert=False, with_template=True, is_enabled=True, **kwargs):
        if is_enabled is not None:
            kwargs["is_enabled"] = is_enabled
        effective_types = cls.objects.filter(**kwargs)

        if is_handle_alert:
            applications = AlarmApplication.get_by_cc_biz_id(cc_biz_id, with_template=with_template, )
            valid_source_type = [app.source_type for app in applications]
            # 腾讯云默认开启
            valid_source_type.extend(settings.DEFAULT_OPEN_SOURCE_TYPE)
            effective_types = effective_types.filter(source_type__in=valid_source_type)

        for i in effective_types:
            if cc_biz_id not in i.excluded_set:
                yield i

    @classmethod
    def get_description_mappings(cls, cc_biz_id, is_handle_alert=False, **kwargs):
        return OrderedDict(
            (i.alarm_type, i.description_display)
            for i in cls.get_by_cc_biz_id(cc_biz_id, is_handle_alert, **kwargs)
        )

    @classmethod
    def get_source_type_mappings(cls, cc_biz_id, is_handle_alert=False, **kwargs):
        result = defaultdict(list)
        for i in cls.get_by_cc_biz_id(cc_biz_id, is_handle_alert, **kwargs):
            if i.scenario:
                show_name = '[%s] %s' % (
                    i.scenario_display, i.description_display)
            else:
                show_name = i.description_display
            result[i.source_type].append((i.alarm_type, show_name))
        return result


class World(models.Model):
    """游戏集群"""
    is_enabled = models.BooleanField(_(u'是否启用'), default=True)
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    cc_set_name = models.CharField(_(u"集群 名"), max_length=30)
    cc_set_chn_name = models.CharField(_(u"集群 中文名"), max_length=30)
    world_id = models.CharField(_(u"集群ID"), max_length=30)
    tnm_attr_id = models.CharField(u'attr id', max_length=30, blank=True, null=True)
    tnm_attr_name = models.CharField(u'attr name', max_length=255, blank=True, null=True)
    comment = models.TextField(_(u'备注'), blank=True, null=True)
    online_data_source_host = models.IPAddressField(blank=True, null=True)

    def __unicode__(self):
        if self.comment:
            return unicode('[%s-%s] %s -- %s' % (
                self.cc_biz_id, self.world_id,
                self.cc_set_chn_name or self.cc_set_name, self.comment))
        else:
            return unicode('[%s-%s] %s' % (
                self.cc_biz_id, self.world_id,
                self.cc_set_chn_name or self.cc_set_name))

    def html_format(self, chart_time=None):
        return ('<a href="###">{}</a>').format(self.cc_set_chn_name)


class AlarmInstance(models.Model):
    """
    An instance of a alarminstance
    """
    source_type_tuple = fta_std.SOURCE_TYPE_CHOICES + (('FTA', _(u"故障自愈")),)

    alarm_def_id = models.IntegerField(null=False, blank=False, db_index=True)
    source_type = models.CharField(_(u'告警源'), max_length=32, null=True, choices=source_type_tuple, db_index=True)
    source_id = models.CharField(_(u"告警源系统内id"), max_length=255, db_index=True, null=True)
    event_id = models.CharField(_(u"告警唯一id"), null=True, db_index=True, max_length=255, unique=True)
    ip = models.CharField(_(u'ip, 可空的'), null=True, blank=True, max_length=30)
    raw = models.TextField(_(u'原始告警信息'))
    status = models.CharField(
        _(u'告警处理状态'), null=True, blank=True, max_length=30, default='received', choices=fta_std.STATUS_CHOICES,
        db_index=True
    )
    failure_type = models.CharField(
        _(u'失败原因'), max_length=30, null=True, blank=True, choices=fta_std.FAILURE_TYPE_CHOICES
    )

    bpm_task_id = models.CharField(_(u'handle_alarm或者solution的task id'), max_length=30, null=True, blank=True)
    comment = models.TextField(_(u'备注'), null=True, blank=True)
    source_time = models.DateTimeField(_(u'告警生成时间'), null=True, blank=True, db_index=True)
    finish_time = models.DateTimeField(_(u'告警结束时间'), null=True, blank=True)
    begin_time = models.DateTimeField(_(u'自愈建单时间'), auto_now_add=True)
    end_time = models.DateTimeField(_(u'自愈结束处理时间'), null=True, blank=True)
    level = models.IntegerField(_(u'告警重要级别'), default=1, db_index=True)
    priority = models.IntegerField(_(u'告警处理队列优先级'), default=1, db_index=True)

    # -------------Snapshot(冗余的定义数据): 加快加载速度, 并防止原定义的改动删除-------------
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    alarm_type = models.CharField(_(u'告警类型'), max_length=128, db_index=True)
    solution_type = models.CharField(
        _(u'套餐类型'), max_length=128, choices=fta_std.SOLUTION_TYPE_CHOICES, null=True, db_index=True
    )
    snap_alarm_def = models.TextField(_(u'json, alarm_def的完整数据快照'), null=True, blank=True)
    snap_solution = models.TextField(_(u'json, solution的完整数据快照'), null=True, blank=True)
    origin_alarm = models.TextField(_(u"告警的原始内容"), null=True)

    # -----额外信息
    cc_topo_set = models.CharField(_(u'CC大区'), max_length=128, blank=True, db_index=True)
    cc_app_module = models.CharField(_(u'CC模块'), max_length=128, blank=True, db_index=True)
    inc_alarm_id = models.CharField(_(u'inc告警ID'), null=True, blank=True, max_length=30)
    uwork_id = models.CharField(_(u'uwork告警ID'), null=True, blank=True, max_length=30)

    # -----审批相关
    approved_time = models.DateTimeField(_(u'审批批示时间'), null=True, blank=True)
    approved_user = models.CharField(_(u'流程审批人'), max_length=128, null=True, blank=True)
    approved_comment = models.CharField(_(u'审批备注'), max_length=128, null=True, blank=True)

    tnm_alarm = models.TextField(_(u'上下文'), null=True, blank=True)
    tnm_alarm_id = models.CharField(_(u'tnm告警ID'), null=True, blank=True, unique=True, max_length=30, db_index=True)

    @property
    def source_time_show(self):
        return strftime_local(self.source_time)

    @property
    def alarm_log_list(self):
        """
        关联到AlarmInstanceLog的快速写法
        :return QuerySet: AlarmInstanceLog
        """
        return AlarmInstanceLog.objects.filter(alarm_instance_id=self.id)

    @property
    def incidentalarm_list(self):
        """
        关联到IncidentAlarm的快速写法
        :return QuerySet: IncidentAlarm
        """
        return IncidentAlarm.objects.filter(alarm_id=self.id)

    @property
    def alarm_def(self):
        """
        关联到AlarmDef的快速写法
        :return QuerySet: AlarmDef
        """
        try:
            if self.alarm_def_id:
                return AlarmDef.objects.get(id=self.alarm_def_id)
        except AlarmDef.DoesNotExist:
            return ""

    @property
    def solution__snapshot(self):
        """
        获取 Solution 快照
        """
        if self.snap_solution:
            return json.loads(self.snap_solution)

    @property
    def alarm_def__snapshot(self):
        """
        获取 AlarmDef 快照
        """
        if self.snap_alarm_def:
            return json.loads(self.snap_alarm_def)

    @property
    def include_solution_url(self):
        """
        获取 Solution URL
        :return include_url: 非绝对路径
        """
        if self.solution__snapshot:
            return '%s/solution/%s/' % (self.cc_biz_id, self.solution__snapshot['id'])

    @property
    def failure_type_description(self):
        """
        获取失败原因的中文描述
        """
        return dict(fta_std.FAILURE_TYPE_CHOICES).get(self.failure_type, u'**unknown**')

    @property
    def consumed(self):
        """
        获取耗时的中文描述
        """
        consumed = 0
        if self.end_time:  # 结束状态
            consumed = (self.end_time - self.begin_time).total_seconds()
        elif self.status in ('for_reference', 'for_notice', 'success', 'almost_success', 'failure', 'skipped'):
            return u"未记录"
        else:
            now = timezone.now()
            consumed = (now - self.begin_time).total_seconds()

        if consumed < 60:
            return _(u"%s秒") % int(consumed)
        elif consumed < 3600:
            return _(u"%d分钟") % (consumed / 60)
        else:
            return _(u"%d小时") % (consumed / 3600)

    def __unicode__(self):
        return unicode('%s --> %s' % (
            self.alarm_def, strftime_local(self.begin_time, '%m-%d %H:%M:%S') if self.begin_time else ''))


class AlarmInstanceBackup(models.Model):
    """
    An instance of a alarminstancebackup
    """
    alarm_def_id = models.IntegerField(null=False, blank=False, db_index=True)
    source_type = models.CharField(_(u'告警源'), max_length=32, null=True, choices=fta_std.SOURCE_TYPE_CHOICES)
    source_id = models.CharField(_(u"告警源系统id"), max_length=255, db_index=True, null=True)
    event_id = models.CharField(_(u"告警唯一id"), null=True, db_index=True, max_length=255, unique=True)
    ip = models.CharField(_(u'ip, 可空的'), null=True, blank=True, max_length=30)
    raw = models.TextField(_(u'原始告警信息'))
    status = models.CharField(
        _(u'告警处理状态'), null=True, blank=True, max_length=30,
        default='received', choices=fta_std.STATUS_CHOICES, db_index=True
    )
    failure_type = models.CharField(
        _(u'失败原因'), max_length=30, null=True, blank=True, choices=fta_std.FAILURE_TYPE_CHOICES
    )

    bpm_task_id = models.CharField(_(u'handle_alarm或者solution的task id'), max_length=30, null=True, blank=True)
    comment = models.TextField(_(u'备注'), null=True, blank=True)
    source_time = models.DateTimeField(_(u'告警生成时间'), null=True, blank=True, db_index=True)
    finish_time = models.DateTimeField(_(u'告警结束时间'), null=True, blank=True)
    begin_time = models.DateTimeField(_(u'自愈建单时间'), auto_now_add=True)
    end_time = models.DateTimeField(_(u'自愈结束处理时间'), null=True, blank=True)
    level = models.IntegerField(_(u'告警重要级别'), default=1, db_index=True)
    priority = models.IntegerField(_(u'告警处理队列优先级'), default=1, db_index=True)

    # -------------Snapshot(冗余的定义数据): 加快加载速度, 并防止原定义的改动删除-------------
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    alarm_type = models.CharField(_(u'告警类型'), max_length=128, db_index=True)
    solution_type = models.CharField(
        _(u'套餐类型'), max_length=128, choices=fta_std.SOLUTION_TYPE_CHOICES, null=True, db_index=True
    )
    snap_alarm_def = models.TextField(_(u'json, alarm_def的完整数据快照'), null=True, blank=True)
    snap_solution = models.TextField(_(u'json, solution的完整数据快照'), null=True, blank=True)
    origin_alarm = models.TextField(_(u"告警的原始内容"), null=True)

    # -----额外信息
    cc_topo_set = models.CharField(_(u'CC集群'), max_length=128, blank=True, db_index=True)
    cc_app_module = models.CharField(_(u'CC模块'), max_length=128, blank=True, db_index=True)
    inc_alarm_id = models.CharField(_(u'inc告警ID'), null=True, blank=True, max_length=30)
    uwork_id = models.CharField(_(u'uwork告警ID'), null=True, blank=True, max_length=30)

    # -----审批相关
    approved_time = models.DateTimeField(_(u'审批批示时间'), null=True, blank=True)
    approved_user = models.CharField(_(u'流程审批人'), max_length=128, null=True, blank=True)
    approved_comment = models.CharField(_(u'审批备注'), max_length=128, null=True, blank=True)

    tnm_alarm = models.TextField(_(u'上下文'), null=True, blank=True)
    tnm_alarm_id = models.CharField(_(u'tnm告警ID'), null=True, blank=True, unique=True, max_length=30, db_index=True)

    @property
    def alarm_log_list(self):
        """
        关联到AlarmInstanceLog的快速写法
        :return QuerySet: AlarmInstanceLog
        """
        return AlarmInstanceLog.objects.filter(alarm_instance_id=self.id)

    @property
    def incidentalarm_list(self):
        """
        关联到IncidentAlarm的快速写法
        :return QuerySet: IncidentAlarm
        """
        return IncidentAlarm.objects.filter(alarm_id=self.id)

    @property
    def alarm_def(self):
        """
        关联到AlarmDef的快速写法
        :return QuerySet: AlarmDef
        """
        try:
            if self.alarm_def_id:
                return AlarmDef.objects.get(id=self.alarm_def_id)
        except AlarmDef.DoesNotExist:
            return ""

    @property
    def solution__snapshot(self):
        """
        获取 Solution 快照
        """
        if self.snap_solution:
            return json.loads(self.snap_solution)

    @property
    def alarm_def__snapshot(self):
        """
        获取 AlarmDef 快照
        """
        if self.snap_alarm_def:
            return json.loads(self.snap_alarm_def)

    @property
    def include_solution_url(self):
        """
        获取 Solution URL
        :return include_url: 非绝对路径
        """
        if self.solution__snapshot:
            return '%s/solution/%s/' % (self.cc_biz_id, self.solution__snapshot['id'])

    @property
    def failure_type_description(self):
        """
        获取失败原因的中文描述
        """
        return dict(fta_std.FAILURE_TYPE_CHOICES).get(self.failure_type, u'**unknown**')

    @property
    def consumed(self):
        """
        获取耗时的中文描述
        """
        if self.end_time:  # 结束状态
            consumed = (self.end_time - self.begin_time).total_seconds() / 60
            return _(u"%d分钟") % consumed
        elif self.status in ('for_reference', 'for_notice', 'success', 'almost_success', 'failure', 'skipped'):
            return _(u"未记录")
        else:
            consumed = (
                timezone.now() - self.begin_time).total_seconds() / 60
            if consumed > 60 * 24:
                return _(u"%d天") % (consumed / 60 / 24)
            else:
                return _(u"%d分钟 +") % consumed

    def __unicode__(self):
        return unicode('%s --> %s' % (
            self.alarm_def, strftime_local(self.begin_time, '%m-%d %H:%M:%S')))


class IncidentDef(models.Model):
    """收敛定义"""
    is_enabled = models.BooleanField(_(u'是否启用'), default=False)
    cc_biz_id = models.IntegerField(_(u'业务编码'))  # use 0 for builtin incident def
    codename = models.CharField(_(u'英文名称代号'), max_length=128)
    rule = models.TextField(_(u'收敛规则(JSON)'), default='{}')
    description = models.TextField(_(u'规则简介'))
    exclude = models.TextField(_(u'排除的业务'), blank=True, null=True)
    priority = models.IntegerField(_(u'优先级'), default=100)

    @property
    def exclude_list(self):
        return self.exclude.split(',') if self.exclude else []

    @property
    def description_display(self):
        if not self.description:
            return self.description
        return _(self.description)

    class Meta:
        unique_together = ('cc_biz_id', 'codename')

    def __unicode__(self):
        return unicode('[%s] -- %s' % (self.cc_biz_id, self.codename))


class AdviceDef(models.Model):
    """
    健康度报告的定义
    """

    # 优化规则的定义。
    # 将老版本置为不可用
    # 这样Advice就不需要存储快照数据了

    # 优化规则的考察对象的类型
    SUBJECT_TYPE_CHOICES = (
        ('host', _(u'主机')),
        ('world', _(u'集群')),
        # ('idc', u'同一IDC'),
        # ...
    )
    # 待优化项分类
    ADVICE_TYPE_CHOICES = (
        # 反复Ping，agent，硬盘只读，时间同步，机房，IDC多次故障 --》 建议迁移机房，切换机器...
        ('hardware', _(u'硬件待优化')),
        ('ops', _(u'运维待优化')),  # 磁盘经常满 --》 建议联系开发
        ('biz', _(u'业务待优化')),  # 进程端口 --》 建议调查
        ('suspicious', _(u'可疑待优化')),  # 反复其他告警 --》 建议调查
        # ...
    )

    codename = models.CharField(_(u'英文名称代号'), max_length=128)
    description = models.TextField(_(u'描述'))
    is_enabled = models.BooleanField(_(u'是否启用'), default=False)
    cc_biz_id = models.IntegerField(_(u'业务编码'))  # use 0 for builtin incident def

    subject_type = models.CharField(_(u'考察对象'), max_length=64, choices=SUBJECT_TYPE_CHOICES)
    check_type = models.CharField(
        _(u'考察数据'), max_length=64, choices=(('alarm', _(u"告警")), ('incident', _(u"收敛事件")))
    )
    check_sub_type = models.CharField(_(u'详细数据类型'), max_length=128)  # ping,agent
    interval = models.IntegerField(_(u'考察时长(天)'))
    threshold = models.IntegerField(_(u'考察阀值'))

    advice_type = models.CharField(_(u'建议类型'), choices=ADVICE_TYPE_CHOICES, max_length=64)
    advice = models.TextField(_(u'具体建议'))

    create_time = models.DateTimeField(_(u'创建时间'), auto_now_add=True)

    @property
    def advices(self):
        """
        关联到Advice的快速写法
        :return QuerySet: Advice
        """
        return Advice.objects.filter(advice_def_id=self.id)

    @property
    def check_sub_type_desc(self):
        """
        获取详细数据类型的描述
        """
        check_sub_type = self.check_sub_type
        # ugly implemention
        for at, at_str in AlarmType.get_description_mappings(
                self.cc_biz_id,
        ).items():
            if at in check_sub_type:
                check_sub_type = check_sub_type.replace(at, at_str)
        check_sub_type = check_sub_type.replace(',', '/')
        return check_sub_type

    def __unicode__(self):
        return unicode(_(u'[%s]%s-%s天') % (
            self.codename, self.check_sub_type, self.interval))


SUBJECT_TYPE_DICT = dict(AdviceDef.SUBJECT_TYPE_CHOICES)
ADVICE_TYPE_DICT = dict(AdviceDef.ADVICE_TYPE_CHOICES)


class Advice(models.Model):
    """
    健康度报告的建议实例
    冗余了一些AdviceDef的字段用于快速查询
    """
    ADVICE_STATUS_CHOICES = (
        ('fresh', _(u'新生成的，等待运维确认')),
        ('followup', _(u'运维认可，开始跟进')),
        ('deny', _(u'运维吐槽规则，觉得不是个事儿')),
        ('finish', _(u'已经完成')),
    )
    OFFLINE_STATUS_CHOICES = (
        ('ok', _(u'已经线下处理该风险')),
        ('no', _(u'未处理')),
    )

    ADVICE_SHOW_STATUS = (
        ('not_handle', _(u'未处理')),
        ('failure', _(u'失败')),
        ('success', _(u'成功')),
    )

    # 暂时先不用冗余字段来加快查询，等试运行一段时间看看需求
    advice_def_id = models.IntegerField(null=False, blank=False, db_index=True)

    cc_biz_id = models.IntegerField(_(u'业务编码'))
    subject = models.CharField(_(u'考察对象'), max_length=128)
    alarm_num = models.IntegerField(_(u'考察发现了多少条告警'))
    alarm_start_time = models.DateField(_(u'考察的起始时间'))
    alarm_end_time = models.DateField(_(u'考察的结束时间'))

    status = models.CharField(_(u'优化项状态'), max_length=32)
    comment = models.TextField(_(u'优化项的备注'), null=True, blank=True)

    create_time = models.DateTimeField(_(u'建议生成时间'), auto_now_add=True, db_index=True)

    operator = models.CharField(_(u'最后修改人'), max_length=128, null=True, blank=True)
    modify_time = models.DateTimeField(_(u'最后修改时间'), auto_now=True, null=True, blank=True)
    # 关联的预警自愈信息
    advice_fta_def_id = models.IntegerField(_(u"预警自愈方案id"), null=True, blank=True, default=0)
    # 关联的告警信息，由告警来触发预警处理流程
    alarminstance_id = models.IntegerField(_(u"告警详情id"), null=True, blank=True, default=0)
    # 是否已经线下处理
    offline_handle = models.CharField(_(u'线下处理'), max_length=32, choices=OFFLINE_STATUS_CHOICES, default='no')
    offline_user = models.CharField(_(u"线下处理人"), max_length=100, default='')
    offline_time = models.DateTimeField(_(u"线下处理时间"))

    @property
    def advice_status(self):
        """
        建议的当前的处理状态
        """
        # 未处理
        if (self.advice_fta_handle_type == 'advice' and self.offline_handle == 'no'):
            return 'not_handle'
        # 失败
        elif (
            self.advice_fta_handle_type == 'solution' and
            self.alarminstance and
            self.alarminstance.status == 'failure'
        ):
            return 'failure'
        # 成功
        elif (
            (self.advice_fta_handle_type == 'advice' and self.offline_handle == 'ok') or
            (
                self.advice_fta_handle_type == 'solution' and self.alarminstance and
                self.alarminstance.status == 'success'
            )
        ):
            return 'success'
        return ''

    # 预警自愈相关的信息，健康诊断页面需要
    @property
    def advice_fta_def(self):
        if self.advice_fta_def_id:
            try:
                return AdviceFtaDef.objects.get(id=self.advice_fta_def_id)
            except Exception:
                return None
        return None

    @property
    def advice_fta_handle_type(self):
        if self.advice_fta_def:
            return self.advice_fta_def.handle_type
        # 没有关联预警定义，则处理类型为建议
        return 'advice'

    @property
    def advice_fta_handle_type_name(self):
        handle_type_dict = dict(AdviceFtaDef.HANDLE_TYPE_CHOICES)
        return handle_type_dict.get(self.advice_fta_handle_type, self.advice_fta_handle_type)

    @property
    def advice_fta_solution_id(self):
        if self.advice_fta_def:
            return self.advice_fta_def.solution_id
        return ''

    @property
    def advice_fta_solution(self):
        if self.advice_fta_solution_id:
            try:
                return Solution.objects.get(id=self.advice_fta_solution_id)
            except Exception:
                return None
        return None

    @property
    def advice_fta_solution_name(self):
        if self.advice_fta_def:
            return self.advice_fta_def.solution_name
        return ''

    # 自愈详情相关的信息，健康诊断页面需要
    @property
    def alarminstance(self):
        if self.alarminstance_id:
            try:
                return AlarmInstance.objects.get(id=self.alarminstance_id)
            except Exception:
                return None
        return None

    @property
    def alarminstance_set_names(self):
        if self.alarminstance:
            return self.alarminstance.cc_topo_set
        else:
            try:
                comment = json.loads(self.comment)
                return comment.get('set_name', '')
            except Exception:
                pass
        return ''

    @property
    def alarminstance_module_name(self):
        if self.alarminstance:
            return self.alarminstance.cc_app_module
        else:
            try:
                comment = json.loads(self.comment)
                return comment.get('module_name', '')
            except Exception:
                pass
        return ''

    @property
    def advice_def(self):
        if self.advice_def_id:
            try:
                return AdviceDef.objects.get(id=self.advice_def_id)
            except Exception:
                return None
        return None

    # 从现象到本质的过程
    @property
    def phenomenon(self):
        return u'%s %s' % (self.alarm_detail_description,
                           self.alarm_detail_href)

    @property
    def subject_info(self):
        """健康度的详情的对象"""
        adv_def = self.advice_def
        t_subject = self.subject
        if adv_def.subject_type == 'world':
            t_subject = _(u"集群({})").format(str(self.subject))

        return t_subject

    @property
    def alarm_detail_description(self):
        """健康度的详情 描述"""
        adv_def = self.advice_def
        return _(u'{} <u>{}</u>天内 出现 <u>{}</u> 条 <u>{}</u>告警').format(
            self.subject_info,
            adv_def.interval,
            self.alarm_num,
            adv_def.check_sub_type,
        )

    @property
    def alarm_detail_href(self):
        """健康度的详情 URL"""
        url_base = "%s/alarm_instance_list/" % self.cc_biz_id
        # 18time 时间
        stime = datetime.datetime.strftime(self.alarm_start_time, "%Y-%m-%d")
        etime = datetime.datetime.strftime(self.alarm_end_time, "%Y-%m-%d")
        date_param = stime + " to " + etime
        param = {'alarm_type': self.advice_def.check_sub_type.split(",")[0],
                 'date': date_param}
        if self.advice_def.subject_type == 'host':
            param.update({'ip': unicode(self.subject).encode('utf-8')})
        elif self.advice_def.subject_type == 'world':
            pass
        url = url_base + "?" + urllib.urlencode(param)
        href = (u"""<a href="javascript:include_open('%s');">""" + _(u"查看详情") + "</a>") % url
        return href


class AdviceFtaDefManager(models.Manager):

    def all(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(AdviceFtaDefManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(AdviceFtaDefManager, self) \
            .filter(*args, **kwargs).filter(is_deleted=False)


class AdviceFtaDef(models.Model):
    """预警定义"""
    HANDLE_TYPE_CHOICES = (
        ('solution', _(u'套餐')),
        ('advice', _(u'建议')),
    )

    objects = AdviceFtaDefManager()

    # 关联的建议定义
    advice_def_id = models.IntegerField(null=False, blank=False, db_index=True)

    is_enabled = models.BooleanField(_(u'是否启用'), default=False)
    is_deleted = models.BooleanField(_(u'是否删除'), default=False)
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True, help_text=_(u"0表示全业务"))

    module = models.TextField(u'Module ID', default='', blank=True, help_text=_(u"冗余字段"))
    topo_set = models.TextField(u'Set ID', default='', blank=True, help_text=_(u"冗余字段"))

    set_names = models.TextField(_(u"Set名称"), default='', blank=True)
    module_names = models.TextField(_(u"Module名称"), default='', blank=True)

    responsible = models.CharField(_(u'额外通知人'), max_length=255, blank=True, null=True)
    title = models.CharField(_(u'全名'), max_length=128, blank=True, null=True)
    description = models.TextField(_(u'备注'), blank=True, null=True)
    notify = models.TextField(_(u'通知配置'), default="{}")
    solution_id = models.IntegerField(null=True, blank=True, db_index=True)
    timeout = models.IntegerField(_(u'超时时长'), default=40)

    handle_type = models.CharField(_(u'处理类型'), max_length=10, choices=HANDLE_TYPE_CHOICES, default='solution')

    exclude = models.TextField(_(u'排除的业务'), blank=True, null=True, default='')

    @classmethod
    def get_related_instance(cls, cc_biz_id):
        """
        获取跟预警自愈相关联的告警信息，目前只统计数量
        """
        all_fta_ins = AlarmInstance.objects.filter(alarm_def_id=0, alarm_type='fta_advice', cc_biz_id=cc_biz_id)
        fta_ins_dict = {}
        for fta_ins in all_fta_ins:
            # 解析告警信息相关联的预警定义
            snap_alarm_def = fta_ins.snap_alarm_def
            try:
                snap_alarm_def = json.loads(snap_alarm_def)
                advice_fta_id = snap_alarm_def.get('id')
            except Exception:
                advice_fta_id = None
            if advice_fta_id:
                if fta_ins_dict.get(advice_fta_id):
                    fta_ins_list = fta_ins_dict[advice_fta_id]
                    fta_ins_list.append(fta_ins.id)
                    fta_ins_dict[advice_fta_id] = fta_ins_list
                else:
                    fta_ins_dict[advice_fta_id] = [fta_ins.id]
        return fta_ins_dict

    @property
    def handel_type_name(self):
        AdviceFtaDef.HANDLE_TYPE_CHOICES = (
            ('solution', _(u'套餐')),
            ('advice', _(u'建议')),
        )
        handle_type_dict = dict(AdviceFtaDef.HANDLE_TYPE_CHOICES)
        return handle_type_dict.get(self.handle_type, self.handle_type)

    @property
    def solution(self):
        """
        关联到Solution的快速写法
        :return QuerySet: Solution
        """
        if self.solution_id:
            try:
                return Solution.objects.get(id=self.solution_id)
            except Exception:
                return None
        return None

    @property
    def solution_name(self):
        return self.solution.title_display if self.solution else _(u"(不处理)")

    @property
    def advice_def(self):
        if self.advice_def_id:
            return AdviceDef.objects.get(id=self.advice_def_id)
        return None

    @property
    def notify_conf(self):
        """
        获取通知的字典配置
        """
        return json.loads(self.notify)

    @property
    def exclude_biz_list(self):
        """
        全业务策略中，未启用的业务列表
        """
        return self.exclude.split(',')

    class Meta:
        # 全业务优先级最高
        ordering = ('cc_biz_id',)


class Incident(models.Model):
    INCIDENT_TYPE_CHOICES = (
        ("skip", _(u"成功跳过")),
        ("skip_approve", _(u"审批跳过")),
        ("pass", _(u"执行跳过")),
        ("wait", _(u"执行中等待")),
        ("defense", _(u"异常防御")),
        ("relevance", _(u"事件汇集")),
        ("trigger", _(u"收敛触发")),
        ('collect_alarm', _(u'汇总通知')),
        ("collect", _(u"超出后汇总")),
        ("notify", _(u"触发通知")),
        ('convergence', _(u'告警收敛')),

        ('network-attack', _(u'网络攻击')),
        ('network-quality', _(u'网络故障')),
        ('host-quality', _(u'单机故障')),
        ('analyze', _(u'预诊断')),
        ("universality", _(u"共性分析")),
    )

    INCIDENT_TYPE_COLORS = (
        ('network-attack', 'success'),
        ('network-quality', 'success'),
        ('host-quality', 'success'),
        ('analyze', u'success'),
        ('collect_alarm', u'success'),
        ('defence', u'danger'),
        ('convergence', u'primary'),  # 优先显示主告警的状态
    )

    NOTIFY_STATUSES = (
        ('sent', _(u'已发送')),
        ('new', _(u'尚未发送')),
        ('', _(u'无内容')),
    )

    is_visible = models.BooleanField(_(u'是否可见'), default=True)
    # incident_def = models.ForeignKey(IncidentDef)
    incident_def_id = models.IntegerField(null=False, blank=False, db_index=True)
    incident_type = models.CharField(
        _(u'事件类型'), choices=INCIDENT_TYPE_CHOICES, max_length=128, null=True, blank=True, db_index=True
    )
    # incident def will share between biz
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    dimension = models.CharField(_(u'收敛维度'), max_length=128, unique=True, db_index=True)
    description = models.TextField(_(u'描述'))
    content = models.TextField(_(u'内容'))
    detail = models.TextField(_(u'详情'), blank=True, null=True)
    last_check_time = models.DateTimeField(_(u'最近一次检查时间'), auto_now_add=True)
    begin_time = models.DateTimeField(_(u'事件开始时间'), auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(_(u'事件结束时间'), blank=True, null=True)
    notify_status = models.CharField(_(u'消息提醒状态'), blank=True, null=True, choices=NOTIFY_STATUSES, max_length=4)

    @property
    def incident_def(self):
        if self.incident_def_id:
            return IncidentDef.objects.get(id=self.incident_def_id)

    @property
    def related_alarms(self):
        return IncidentAlarm.objects.filter(incident_id=self.id)

    @property
    def description_display(self):
        if not self.description:
            return self.description
        return _(self.description)

    # @property
    # def primary_alarm(self):
    #     if self.related_alarms.filter(is_primary=True).count():
    #         return self.related_alarms.filter(is_primary=True)[0].alarm
    #     return self.related_alarms.order_by('-id')[0].alarm
    #
    # @property
    # def incident_type_info(self):
    #     return dict(Incident.INCIDENT_TYPE_CHOICES)[self.incident_type]
    #
    # @property
    # def incident_type_color(self):
    #     return dict(Incident.INCIDENT_TYPE_COLORS)[self.incident_type]
    #
    # @property
    # def source_time(self):
    #     return self.related_alarms.all().order_by('-id')[0].alarm.source_time

    def __unicode__(self):
        return unicode('[%s ~ %s] -- %s' % (self.begin_time, self.end_time, self.description_display))


class IncidentAlarm(models.Model):
    """
    AlarmInstance 与 Incident 的 many_to_many 关联
    """
    incident_id = models.IntegerField(null=False, blank=False, db_index=True)
    alarm_id = models.IntegerField(null=False, blank=False, db_index=True)
    is_primary = models.BooleanField(_(u'主要告警'), default=False)

    class Meta:
        unique_together = ('incident_id', 'alarm_id')

    @property
    def incident(self):
        """
        关联到Incident的快速写法
        :return QuerySet: Incident
        """
        if self.incident_id:
            return Incident.objects.get(id=self.incident_id)

    @property
    def alarm(self):
        """
        关联到AlarmInstance的快速写法
        :return QuerySet: AlarmInstance
        """
        if self.alarm_id:
            return AlarmInstance.objects.get(id=self.alarm_id)

    def __unicode__(self):
        return 'Inc-%s | Alarm-%s(%s)' % (self.incident.id, self.alarm.id, self.alarm)


class Context(models.Model):
    """
    由于存放告警处理时的全局变量
    """
    key = models.CharField(u"KEY", max_length=128, db_index=True)
    field = models.CharField(_(u"变量名"), max_length=128)
    value = models.TextField(_(u"值"))
    created_on = models.DateTimeField(_(u"创建时间"), auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(_(u"更新时间"), auto_now=True, db_index=True, null=True, blank=True)

    class Meta:
        unique_together = ("key", "field")


class UserBiz(models.Model):
    """
    用户上一次使用的业务
    """
    username = models.CharField(_(u'用户'), max_length=255, unique=True)
    cc_biz_id = models.IntegerField(_(u'业务编码'))

    def __unicode__(self):
        return '%s => %s' % (self.username, self.cc_biz_id)


class BizConf(models.Model):
    """
    业务级的配置
    """
    cc_biz_id = models.IntegerField(_(u'业务编码'), unique=True, db_index=True)

    responsible = models.CharField(_(u'责任人'), max_length=512, blank=True, null=True)

    tnm_servicegroup_id = models.IntegerField(_(u'TNM业务组ID'), unique=True, null=True)
    online_data_source_host = models.IPAddressField(default=None, blank=True, null=True)

    def __unicode__(self):
        return unicode('[%s] -- %s' % (self.cc_biz_id, self.responsible))


class Conf(models.Model):
    """
    重要配置项  (加入数据保护计划)
    用来存放一些自愈的全局配置
    """
    name = models.CharField(_(u"配置项名"), max_length=100, unique=True, help_text=_(u"切勿随意修改此项"))
    value = models.TextField(u"配置项参数值", help_text=_(u"数据内容"))
    description = models.TextField(_(u"说明"), default='')

    @classmethod
    def get(cls, key):
        _conf, _c = cls.objects.get_or_create(name=key)
        return _conf.value or ''

    @classmethod
    def set(cls, key, value):
        _conf, _c = cls.objects.get_or_create(name=key)
        _conf.value = value
        _conf.save()
        return True

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'配置项')
        verbose_name_plural = _(u'配置项')


class DataChanglog(models.Model):
    """
    数据项的更改日志

    所有重要配置表的所有修改都会记录在这个表里。

    注意：
    只对 app 生效，app 外触发的数据修改无法记录
    所以不要在 app 外提供修改配置数据的方法
    """
    change_model = models.CharField(u"修改的数据表", max_length=100)
    change_id = models.IntegerField(u"修改的数据项id")
    change_time = models.DateTimeField(u'修改时间', auto_now_add=True)
    CHANGE_TYPE = (
        ('create', u'创建'),
        ('delete', u'删除'),
        ('update', u'更新'),
    )
    change_type = models.CharField(u"修改类型", choices=CHANGE_TYPE, max_length=20)
    new = models.TextField(u"新数据", null=True, blank=True, help_text=u"更改后的数据内容")
    username = models.CharField(u'修改人', max_length=100)

    def __unicode__(self):
        return self.change_model

    class Meta:
        verbose_name = u'数据修改日志'
        verbose_name_plural = u'数据修改日志'


class AlarmInstanceLog(models.Model):
    """
    告警的处理 log 表
    用来记录处理步骤

    INFO 级别以上的会在界面展示
    DEBUG 级别及以下的信息用作内部数据
    """
    LEVEL_CHOICES = (
        (0, 'NOTSET'),
        (10, 'DEBUG'),
        (20, 'INFO'),
        (30, 'WARNING'),
        (40, 'ERROR'),
        (50, 'CRITICAL'),
    )
    # alarm_instance = models.ForeignKey(AlarmInstance)
    alarm_instance_id = models.IntegerField(null=False, blank=False, db_index=True)
    content = models.TextField(_(u'步骤记录'))
    time = models.DateTimeField(_(u'备注时间'), auto_now=True)
    step_name = models.CharField(_(u"步骤名"), max_length=32, default=None, null=True)
    level = models.SmallIntegerField(
        _(u"信息等级"), choices=LEVEL_CHOICES, help_text=_("同python logging level定义"), default=None, null=True
    )

    @property
    def show_time(self):
        return strftime_local(self.time, "%H:%M:%S")

    @property
    def alarm_instance(self):
        if self.alarm_instance_id:
            return AlarmInstance.objects.get(id=self.alarm_instance_id)


class OutOfScopeArchive(models.Model):
    """
    未接入告警的统计表
    """
    STATUS_CHOICES = (
        ('new', _(u'新生成的，未分析出建议')),
        ('suggest', _(u'新生成的，等待用户确认建议')),
        ('enabled', _(u'用户已启用采纳, 已添加到AlarmDef表中')),
        ('ignore', _(u'用户忽略的,自愈小助手页面不再显示')),
    )
    created_on = models.DateTimeField(_(u'统计归档时间'), auto_now_add=True)
    updated_on = models.DateTimeField(_(u'统计更新时间'), auto_now=True)

    status = models.CharField(_(u'状态'), max_length=10, choices=STATUS_CHOICES, default='new')
    # 垂直列搜索维度
    cc_biz_id = models.IntegerField(_(u'CC业务'), db_index=True)
    alarm_type = models.CharField(_(u'告警类型'), db_index=True, max_length=255)
    cc_module = models.CharField(_(u'告警模块'), db_index=True,
                                 null=True, max_length=128)
    cc_set_name = models.CharField(_(u'告警集群'), db_index=True, null=True, max_length=128)
    # 统计量
    sub_count = models.PositiveIntegerField(_(u'归总数'), default=0)
    extra = models.TextField(_(u'扩展'), max_length=255, blank=False, null=True)

    class Meta:
        unique_together = (
            "cc_biz_id", "alarm_type", "cc_module", "cc_set_name",
        )

    def save(self, *args, **kwargs):
        if not self.extra:
            self.extra = "{}"
        super(OutOfScopeArchive, self).save(*args, **kwargs)

    @classmethod
    def get_suggest_list(cls, cc_biz_id):
        """待用户确认的方案列表
        """
        return cls.objects.filter(cc_biz_id=cc_biz_id, status='suggest')

    @classmethod
    def get_enabled_list(cls, cc_biz_id):
        return cls.objects.filter(cc_biz_id=cc_biz_id, status='enabled')

    @classmethod
    def get_suggest_count(cls, cc_biz_id):
        """待用户确认的方案列表
        """
        suggest_list = cls.get_suggest_list(cc_biz_id)
        return suggest_list.count()

    @property
    def source_type(self):
        try:
            source_type = AlarmType.objects.get(alarm_type=self.alarm_type).source_type
        except Exception:
            return ''
        return source_type

    @property
    def source_name(self):
        source_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
        return source_dict.get(self.source_type, self.source_type)

    @property
    def alarm_type_name(self):
        try:
            source_type = AlarmType.objects.get(alarm_type=self.alarm_type).description_display
        except Exception:
            return ''
        return source_type

    @cached_property
    def extra_data(self):
        return json.loads(self.extra or "{}")

    @property
    def alarm_def_description(self):
        """自愈方案名称
        """
        alarm_def_description = self.extra_data.get("alarm_def_description")
        if alarm_def_description:
            return _(alarm_def_description)
        return ''

    @property
    def alarm_def(self):
        alarm_def_id = self.extra_data.get("alarm_def_id")
        if alarm_def_id is None:
            return None
        return AlarmDef.objects.filter(id=alarm_def_id, cc_biz_id=self.cc_biz_id, ).last()

    @property
    def solution_id(self):
        return self.extra_data.get("solution_id")

    @property
    def solution(self):
        solution_id = self.solution_id
        if solution_id is None:
            return None
        return Solution.objects.filter(id=solution_id).last()


class IgnoreAlarm(models.Model):
    """
    不纳入未接入统计的告警白名单
    """
    cc_biz_id = models.IntegerField(_(u'业务编码(0表示全业务)'))
    alarm_type = models.CharField(_(u'告警类型'), max_length=255, blank=True, null=True)
    attr_id = models.CharField(_(u'特性ID'), max_length=512, blank=True, null=True)
    cc_module = models.CharField(_(u'告警模块， 多个可使用,分割'), max_length=512, blank=True, null=True)
    note = models.TextField(_(u"备注"), help_text=_(u"不关注的原因说明"))

    def __unicode__(self):
        return unicode('[%s] -- %s' % (self.cc_biz_id, self.attr_id))


class KPICache(models.Model):
    """
    KPI数据的统计表
    """

    KPI_TYPE_CHOISES = (
        (30, _(u'一个月浮动')),
        (15, _(u'半个月浮动')),
        (7, _(u'一周浮动')),
        (1, _(u'一天浮动')))

    # 自愈指数按月缓存
    date = models.DateField(_(u'KPI的日期'), db_index=True)

    cc_biz_id = models.IntegerField(_(u'CC业务'), db_index=True)

    kpi_type = models.PositiveIntegerField(_(u'KPI浮动时间段区间'), default=30, choices=KPI_TYPE_CHOISES)

    tnm_total = models.PositiveIntegerField(_(_(u'告警总数')), default=0)
    tnm_covered = models.PositiveIntegerField(_(u'接入数'), default=0)
    tnm_success = models.PositiveIntegerField(_(u'接入中成功的个数'), default=0)

    class Meta:
        unique_together = ("date", "cc_biz_id", "kpi_type")


class AlarmInstanceArchive(models.Model):
    """
    告警数据的统计表
    """

    # 归档索引
    date = models.DateField(_(u'归总日期'), db_index=True)

    # 垂直列搜索维度
    cc_biz_id = models.IntegerField(_(u'CC业务'), db_index=True)
    biz_team = models.CharField(_(u'CC业务组'), db_index=True, max_length=128)
    is_success = models.BooleanField(_(u'是否成功处理'), db_index=True)
    alarm_type = models.CharField(_(u'告警类型'), db_index=True, max_length=128)
    failure_type = models.CharField(
        _(u'失败类型'), choices=fta_std.FAILURE_TYPE_CHOICES, db_index=True, max_length=32, null=True
    )
    solution_type = models.CharField(
        _(u'套餐类型'), choices=fta_std.SOLUTION_TYPE_CHOICES, db_index=True, max_length=32, null=True
    )
    source_type = models.CharField(
        _(u'告警源头'), choices=fta_std.SOURCE_TYPE_CHOICES, db_index=True, max_length=32, null=True
    )
    is_off_time = models.BooleanField(_(u'是否在非工作时间段'), db_index=True)

    # 统计量
    sub_count = models.PositiveIntegerField(_(u'归总数'), default=0)
    sub_consumed = models.PositiveIntegerField(_(u'归总耗时'), default=0)  # 以秒为单位
    sub_profit = models.IntegerField(_(u'归总收益'), default=0)

    # 自动记录时间
    created_on = models.DateTimeField(_(u'统计归档时间'), auto_now_add=True)
    updated_on = models.DateTimeField(_(u'统计更新时间'), auto_now=True)

    dimensions = (
        "cc_biz_id", "biz_team", "is_success", "alarm_type",
        "failure_type", "solution_type", 'source_type',
        'is_off_time'
    )

    class Meta:
        unique_together = (
            "date", "cc_biz_id", "biz_team", "is_success",
            "alarm_type", "failure_type",
            "solution_type", 'source_type', 'is_off_time'
        )

    MONTH = '%Y-%m'
    WEEK = '%Y-%W'  # 以00周星期一作为开始. 数据库对应的格式化符号位%u
    DAY = '%Y-%m-%d'

    @classmethod
    def query(cls, filters=None, group_by=None):
        q = cls.objects
        if filters:
            q = q.filter(**filters)

        _extras = ['month', 'week', 'day']
        stardards = list(set(group_by) - set(_extras))
        extras = list(set(group_by) & set(_extras)) or []
        # 不考虑多个时间维度的group by
        if extras:
            field = extras.pop()
            if field == 'week':
                q = q.extra(select={"date_index": "date_format(date, '%%Y-%%u')"})
            elif field == 'day':
                q = q.extra(select={"date_index": "date_format(date, '%%Y-%%m-%%d')"})
            elif field == 'month':
                q = q.extra(select={"date_index": "date_format(date, '%%Y-%%m')"})
            stardards.append('date_index')
        q = q.values(*stardards)

        return q

    @classmethod
    def stat(cls, filters=None, group_by=None):
        return cls.query(
            filters=filters, group_by=group_by
        ).annotate(sub_count=Sum('sub_count'), sub_consumed=Sum('sub_consumed'))


class EagleEye(models.Model):
    incident_id = models.IntegerField(_(u'自愈事件id'), null=False, blank=False, db_index=True)
    eagle_eye_orderno = models.CharField(_(u'鹰眼告警单号'), max_length=128, db_index=True)
    data_type = models.CharField(_(u'数据类型'), max_length=32, null=True)


class IncRelatedAlarm(models.Model):
    STATUS_CHOICES = (
        (0, _(u'待确认')),
        (1, _(u'已确认')),
    )
    """推送到鹰眼的告警"""
    orderno = models.CharField(_(u'鹰眼单号'), max_length=255, unique=True)
    trigger_orderno = models.CharField(_(u'数据源预警单单号'), max_length=255)
    # 多业务用分号分隔
    product_id = models.CharField(_(u'受影响的业务ID'), max_length=255)
    server_ip = models.CharField(_(u'告警服务器IP，如无则为空'), max_length=255, null=True, default="")
    category_id = models.IntegerField(_(u'在鹰眼上的分类'), default=3)
    archive = models.CharField(_(u'二级分类:告警源自定义的分类'), max_length=255, db_index=True)
    # 告警级别[1-5，值越高越严重]，默认为1
    level = models.IntegerField(_(u'告警级别'), default=1)
    trigger_start_time = models.DateTimeField(_(u'告警触发时间'), db_index=True)
    trigger_end_time = models.DateTimeField(_(u'告警解除时间'), null=True, default='')
    content = models.CharField(_(u'告警内容'), max_length=512, null=True, default='')
    affect = models.CharField(_(u'影响范围'), max_length=512, null=True, default='')
    strategy = models.CharField(_(u'响应策略'), max_length=512, null=True, default='')
    remark = models.CharField(_(u'备注'), max_length=512, null=True, default='')
    url = models.CharField(_(u'告警详情url'), max_length=512, null=True, default='')
    responsible_people = models.CharField(_(u'负责人员'), max_length=512, default='')
    # 是否直接转故障[0：否(默认)；1：是]
    trigger_fault = models.IntegerField(_(u'是否直接转故障'), default=0)
    trigger_description = models.CharField(_(u'转故障描述'), max_length=512, null=True, default='')
    ticket_type = models.IntegerField(_(u'事件单类型ID'), null=True, default=0)
    ticket_name = models.CharField(_(u'事件单类型'), max_length=255, null=True, default='')
    ticket_no = models.CharField(_(u'事件单号'), max_length=512, null=True, default='')
    ticket_url = models.CharField(_(u'事件单URL'), max_length=512, null=True, default='')
    ticket_description = models.CharField(_(u'事件单描述'), null=True, max_length=512, default='')
    ticket_reason = models.CharField(_(u'事件单原因'), null=True, max_length=512, default='')
    ticket_summary = models.CharField(_(u'事件单总结'), null=True, max_length=512, default='')
    status = models.IntegerField(_(u"状态"), choices=STATUS_CHOICES, default=0, null=True)


class IncOrder(models.Model):
    PUSH_TYPE = (
        ('single', _(u'单条告警')),
        ('universality', _(u'共性告警')),
    )
    inc_orderno = models.CharField(_(u'单号'), null=False, unique=True, max_length=255)
    alarm_id = models.IntegerField(_(u'告警ID'), null=False)
    push_type = models.CharField(_(u'推送到的类型'), max_length=255, choices=PUSH_TYPE)

    class Meta:
        unique_together = ('alarm_id', 'push_type')


class QcloudOwnerInfo(models.Model):
    owner_uin = models.CharField(max_length=50, unique=True)
    qcloud_app_id = models.CharField(max_length=50, null=False)


class ApproveCallback(models.Model):
    """审批回调"""

    APPROVAL_STATUS = (
        (0, _(u'未通过')),
        (1, _(u'通过')),
    )
    obj_id = models.CharField(_(u'对象惟一ID'), db_index=True, max_length=255, unique=True)
    alarm_id = models.IntegerField(_(u'告警ID'), db_index=True)
    node_idx = models.IntegerField(_(u'节点ID'), db_index=True)
    approval = models.IntegerField(_(u'审批状态1通过,0未通过'), choices=APPROVAL_STATUS)
    reason = models.CharField(_(u'通过或未通过的原因'), null=True, blank=True, max_length=255)
    approver = models.CharField(_(u'执行审批的操作人'), null=True, blank=True, max_length=255)


class UserAction(models.Model):
    username = models.CharField(_(u'用户'), max_length=255, unique=True)
    is_guide = models.BooleanField(_(u"是否显示接入指引"), default=False)


class AlarmApplicationManager(models.Manager):

    def all(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(AlarmApplicationManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(AlarmApplicationManager, self) \
            .filter(*args, **kwargs).filter(is_deleted=False)


class AlarmApplication(models.Model):
    """第三方告警接入表，如Zabbix，Nagios, Open-Falcon
    """
    SOURCE_TYPE_CHOICE = fta_std.SOURCE_TYPE_CHOICES

    METHOD_CHOICE = (
        ('get', 'GET'),
        ('post', 'POST'),
    )

    objects = AlarmApplicationManager()

    # 应用ID，密钥
    source_type = models.CharField(_(u"告警源标识"), max_length=64, choices=SOURCE_TYPE_CHOICE)
    cc_biz_id = models.IntegerField(_(u'业务编码'), db_index=True)
    app_name = models.CharField(_(u"应用名称"), max_length=255)

    # ID默认生成UUID
    app_id = models.CharField(_(u"应用ID"), max_length=255, unique=True, default=gen_app_id)
    # 生成Secret
    app_secret = models.CharField(_(u"应用密钥"), max_length=255, unique=True, default=gen_app_secret)

    # 创建时间，人
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    create_user = models.CharField(_(u"创建人"), max_length=128)

    # 修改时间，人
    update_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    update_user = models.CharField(_(u"修改人"), max_length=128)

    # 上报时间
    activate_time = models.DateTimeField(_(u"上报时间"), default=None, null=True)

    # 开关项
    is_enabled = models.BooleanField(_(u'是否启用'), default=True)
    is_deleted = models.BooleanField(_(u'是否删除'), default=False)

    extra = models.TextField(_(u"其他"), blank=True, null=True)
    exclude = models.TextField(_(u'排除业务'), default='', blank=True, help_text=_(u"蓝鲸监控设置为全局告警源的默认开启"))

    # 自定义监控配置项
    app_url = models.TextField(_(u"拉取告警地址"), blank=True, null=True, default='')
    app_method = models.CharField(
        _(u"请求类型"), max_length=10, blank=True, null=True, choices=METHOD_CHOICE, default='get'
    )

    # 记录监控源异常信息
    exception_max_num = models.IntegerField(
        _(u"异常阈值"), blank=True, null=True, default=0,
        help_text=_('异常次数超过该阈值时，禁用改监控源,为0则表示不设阈值')
    )
    exception_num = models.IntegerField(_(u"异常次数"), blank=True, null=True, default=0)
    exception_data = models.TextField(_(u"异常信息"), blank=True, null=True, default='')
    exception_begin_time = models.DateTimeField(_(u"异常起始时间"), blank=True, null=True)
    empty_num = models.IntegerField(_(u"空告警次数"), blank=True, null=True, default=0)
    empty_begin_time = models.DateTimeField(_(u"空告警起始时间"), blank=True, null=True)

    @classmethod
    def get_enabled_list_by_biz_id(cls, cc_biz_id):
        """
        获取业务下已启用的告警源列表
        """
        enable_source_list = AlarmApplication.objects.filter(
            (Q(is_enabled=True) | Q(is_enabled=False, exception_num__gt=0))
        )
        # 每类告警源只返回第一条数据
        enable_source_key_list = enable_source_list.values_list('source_type', flat=True)
        enable_source_key_list = set(enable_source_key_list)
        show_list_id = []
        for _s in enable_source_key_list:
            show_list_id.append(enable_source_list.filter(source_type=_s).first().id)
        show_list = enable_source_list.filter(id__in=show_list_id)
        # 蓝鲸监控需要判断，当前业务id是否在 exclude_biz_list 中
        # alert_source = AlarmApplication.objects.filter(source_type='ALERT')
        # if alert_source and cc_biz_id in alert_source[0].exclude_biz_list:
        #     enable_source_list = enable_source_list.exclude(source_type='ALERT')
        return show_list

    @property
    def alarm_count(self):
        """告警量
        """
        ad_list = AlarmInstanceArchive.objects.filter(source_type=self.source_type)
        if self.cc_biz_id:
            ad_list = ad_list.filter(cc_biz_id=self.cc_biz_id)
        return sum([ad.sub_count for ad in ad_list])

    @property
    def get_exception_msg(self):
        """展示给用户看的异常信息
        """
        if not self.exception_num:
            return ''
        # 蓝鲸监控
        if self.source_type == 'ALERT':
            return _(
                u"""从【{start_time}】时间起，连续【{exception_num}】次从【{source_name}】告警源拉取告警异常，
                请关注！异常信息为：{exception_data}""").format(
                start_time=strftime_local(self.exception_begin_time) if self.exception_begin_time else '--',
                exception_num=self.exception_num,
                source_name=self.source_name,
                exception_data=self.exception_data
            )
        else:
            return _(
                u"""从【{start_time}】时间起，连续【{exception_num}】次从【{source_name}】告警源拉取告警异常，
                请检查您的配置项是否正确！异常信息为：{exception_data}""").format(
                start_time=strftime_local(self.exception_begin_time) if self.exception_begin_time else '--',
                exception_num=self.exception_num,
                source_name=self.source_name,
                exception_data=self.exception_data
            )

    @classmethod
    def get_by_cc_biz_id(cls, cc_biz_id, is_enabled=True, is_deleted=False, with_template=True, **kwargs):
        if is_deleted is not None:
            kwargs["is_deleted"] = is_deleted
        if is_enabled is not None:
            kwargs["is_enabled"] = is_enabled

        for app in cls.objects.filter(**kwargs):
            yield app

    @classmethod
    def is_alarm_app_exist(cls, cc_biz_id, source_type, **kwargs):
        """
        限制每类告警源只添加一个
        @note: 不要 unique_together 来限制是为了防止后续接入方案变动时，不方便处理历史数据
            目前按业务添加，所以是按业务粒度进行限制；
            后续按开发商添加，需要要开发商粒度进行限制
        """
        alarm = AlarmApplication.objects.filter(source_type=source_type).first()
        if alarm:
            return True, alarm
        return False, None

    def activate_and_save(self, activate_time=None):
        self.activate_time = activate_time or timezone.now()
        self.save()

    def last_alarm_time_str(self, cc_biz_id=None):
        if cc_biz_id and not self.cc_biz_id:
            alarm_instance = AlarmInstance.objects.filter(cc_biz_id=cc_biz_id, source_type=self.source_type, ).last()
            if alarm_instance is None:
                return ""
            else:
                return strftime_local(alarm_instance.begin_time, '%y/%m/%d %H:%M:%S')

        if not self.activate_time:
            return ""

        return strftime_local(self.activate_time, '%y/%m/%d %H:%M:%S')

    @property
    def exclude_biz_list(self):
        """
        全业务策略中，未启用的业务列表
        """
        return self.exclude.split(',')

    @property
    def source_tip(self):
        return fta_std.SOURCE_TYPE_TIPS.get(self.source_type, '')

    @property
    def source_name(self):
        """
        告警源的显示名
        """
        source_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
        return source_dict.get(self.source_type, self.source_type)

    @property
    def create_time_str(self):
        return strftime_local(self.create_time)

    @property
    def update_time_str(self):
        return strftime_local(self.update_time)

    @property
    def page_type(self):
        type_dict = dict((k, v) for v, k in fta_std.SOURCE_TYPE_PAGES_CHOICES.items())
        page_type = type_dict.get(self.source_type)
        return page_type

    @property
    def callback_url(self):
        page_type = self.page_type
        # 社区版 ESB 默认接入时确认 ZABBIX 带版本号
        if self.source_type == 'ZABBIX':
            return '%s%s/v3.0/%s/' % (settings.FTA_API_PREFIX, page_type, self.app_id)
        return '%s%s/%s/' % (settings.FTA_API_PREFIX, page_type, self.app_id)

    @property
    def callback_url_prefix(self):
        return '%s%s/' % (settings.FTA_API_PREFIX, self.page_type)

    class Meta:
        verbose_name = _(u'添加告警应用')
        verbose_name_plural = _(u'添加告警应用')
        # 倒序排列
        ordering = ('-id',)

    def __unicode__(self):
        return '<%s,%s(%s)>' % (self.app_name, self.app_id, self.cc_biz_id)
