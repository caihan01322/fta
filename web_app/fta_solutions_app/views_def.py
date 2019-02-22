# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

import arrow
from django.conf import settings
from django.db.transaction import atomic
from django.http import (
    HttpResponse, HttpResponseNotFound, JsonResponse,
    HttpResponseNotAllowed,
)
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext as _
from django.views.generic import View
from jsonschema import Draft4Validator

from account.decorators import is_superuser
from common.log import logger
from common.mymako import render_mako_context, render_mako_tostring_context
from fta_solutions_app import fta_std
from fta_solutions_app import models
from fta_solutions_app.backend.tasks import send_update_to_ifix
from fta_solutions_app.cache_utils import get_alert_alarm_type_api
from fta_utils import cipher
from fta_utils.view_toolkit import ResponseToolkit
from project.conf.decorators import login_exempt
from project.conf.user import get_show_name
from .models import (
    AlarmDef, Solution,
    AlarmApplication, gen_app_secret,
    AlarmType,
)

SENDING_UPDATE_ENVS = ('TEST', 'PRODUCT')


def check_perm(request, cc_biz_id):
    """
    权限检查
    """
    result = AlarmDef.objects.filter(cc_biz_id=cc_biz_id).count()
    return HttpResponse(json.dumps(result))


def add_alarm_def(request, cc_biz_id):
    """
    添加告警接入定义
    """
    user_name = get_show_name(request)
    result = {'result': True}

    alarm_type = request.POST['alarm_type']
    if not alarm_type:
        result = {'result': False, 'message': _(u"请选择告警类型")}
        return HttpResponse(json.dumps(result))

    timeout = request.POST['timeout']
    try:
        timeout = int(timeout)
    except Exception:
        result = {'result': False, 'message': _(u"超时时间请填写正整数")}
        return HttpResponse(json.dumps(result))
    if timeout < 5:
        result = {'result': False, 'message': _(u"超时时间请填写大于5的整数")}
        return HttpResponse(json.dumps(result))

    description = request.POST.get('description')
    _is_desciption, _msg = AlarmDef.check_description(cc_biz_id, description)
    if not _is_desciption:
        result = {'result': False, 'message': _msg}
        return HttpResponse(json.dumps(result))

    is_enabled = 'true' == request.POST['is_enabled']
    source_type = request.POST['source_type']
    # 蓝鲸监控启用时，需要判断告警源中蓝鲸监控是否已经启用
    if is_enabled and source_type == 'ALERT':
        is_alert_enabled = AlarmDef.is_alert_enabled(cc_biz_id)
        if not is_alert_enabled:
            result = {'result': False, 'message': _(u"请先在[管理告警源]功能中启用[蓝鲸监控]")}
            return HttpResponse(json.dumps(result))
    try:
        if not request.POST.get('alarm_type'):
            raise Exception(_(u"请选择告警类型！"))
        if request.POST.get('alarm_type') == "customized" and not request.POST.get('tnm_attr_id'):
            raise Exception(_(u"自定义告警特性请选择告警特性ID！"))
        responsible = request.POST['responsible']  # 注意;换成,
        new_def = AlarmDef(
            is_enabled=is_enabled,
            alarm_type=alarm_type,
            tnm_attr_id=request.POST['tnm_attr_id'],
            reg=request.POST['reg'],
            process=request.POST['process'],
            timeout=timeout,
            description=description,
            cc_biz_id=request.POST['cc_biz_id'],
            responsible=responsible,
            module=request.POST['module'],
            topo_set=request.POST['topo_set'],
            module_names=request.POST['module_names'],
            set_names=request.POST['set_names'],
            set_attr=request.POST['set_attr'],
            notify=request.POST['notify'],
            alarm_attr_id=request.POST['alarm_attr_id'],
            source_type=source_type,
            create_user=user_name,
            update_user=user_name,
        )

        if request.POST.get('solution'):
            new_def.solution_id = request.POST.get('solution')

        new_def.save()

        result['def_id'] = new_def.id

        if new_def.is_enabled:
            enable_count = AlarmDef.objects.filter(
                is_enabled=True, category='default',
                cc_biz_id=new_def.cc_biz_id).count()
            if settings.RUN_MODE in SENDING_UPDATE_ENVS:
                send_update_to_ifix(new_def, enable_count, request.user.username)
            elif settings.RUN_MODE == 'DEVELOP':
                send_update_to_ifix(new_def, enable_count, request.user.username)
    except Exception, e:
        result = {'result': False, 'message': unicode(e)}
    return HttpResponse(json.dumps(result))


def edit_alarm_def(request, cc_biz_id):
    """
    修改告警接入定义
    """
    user_name = get_show_name(request)
    result = {'result': True}
    try:
        func_id = request.POST['func_id']
        responsible = request.POST['responsible']  # 注意;换成,
        old_def = AlarmDef.objects.get(id=func_id, cc_biz_id=cc_biz_id)
        new_is_enabled = 'true' == request.POST['is_enabled']

        timeout = request.POST['timeout']
        try:
            timeout = int(timeout)
        except Exception:
            result = {'result': False, 'message': _(u"超时时间请填写正整数")}
            return HttpResponse(json.dumps(result))
        if timeout < 1:
            result = {'result': False, 'message': _(u"超时时间请填写正整数")}
            return HttpResponse(json.dumps(result))

        description = request.POST.get('description')
        _is_desciption, _msg = AlarmDef.check_description(
            cc_biz_id, description, func_id)
        if not _is_desciption:
            result = {'result': False, 'message': _msg}
            return HttpResponse(json.dumps(result))

        source_type = old_def.source_type
        # 蓝鲸监控启用时，需要判断告警源中蓝鲸监控是否已经启用
        if new_is_enabled and source_type == 'ALERT':
            is_alert_enabled = AlarmDef.is_alert_enabled(cc_biz_id)
            if not is_alert_enabled:
                result = {'result': False, 'message': _(u"请先在[管理告警源]功能中启用[蓝鲸监控]")}
                return HttpResponse(json.dumps(result))

        old_def.is_enabled_changed = new_is_enabled != old_def.is_enabled
        old_def.is_enabled = new_is_enabled
        # type不能再改动了
        # old_def.alarm_type=request.POST['alarm_type']
        if request.POST.get('solution'):
            old_def.solution_id = request.POST.get('solution')
        else:
            old_def.solution_id = None
        old_def.tnm_attr_id = request.POST['tnm_attr_id']
        old_def.reg = request.POST['reg']
        old_def.process = request.POST['process']
        old_def.timeout = timeout
        old_def.description = description
        old_def.cc_biz_id = request.POST['cc_biz_id']
        old_def.responsible = responsible
        old_def.module = request.POST['module']
        old_def.topo_set = request.POST['topo_set']
        old_def.set_attr = request.POST['set_attr']
        old_def.notify = request.POST['notify']
        old_def.alarm_attr_id = request.POST['alarm_attr_id']
        old_def.module_names = request.POST['module_names']
        old_def.set_names = request.POST['set_names']
        old_def.update_user = user_name

        old_def.save()

        if old_def.is_enabled_changed:
            enable_count = AlarmDef.objects.filter(
                is_enabled=True, category='default',
                cc_biz_id=old_def.cc_biz_id).count()
            send_update_to_ifix(old_def, enable_count, request.user.username)
    except Exception, e:
        result = {'result': False, 'message': unicode(e)}
    return HttpResponse(json.dumps(result))


def del_def(request, cc_biz_id, func_type):
    """目前同时支持AlarmDef和Solution, 后续拆掉"""
    result = {'result': True}
    model_class = AlarmDef if func_type == 'alarm' else Solution
    try:
        to_del = model_class.objects.get(id=request.POST['id'], cc_biz_id=cc_biz_id, )
        if func_type == 'alarm':
            enable_count = AlarmDef.objects.filter(
                is_enabled=True, category='default',
                cc_biz_id=to_del.cc_biz_id).count()
            send_update_to_ifix(to_del, enable_count, request.user.username)

        if func_type == 'solution':
            if to_del.alarm_def_list.filter(is_deleted=False).count():
                raise Exception(_(u"该套餐正被使用，如需删除请在接入策略中去除对本套餐的使用。"))

        to_del.delete()

    except Exception, e:
        result = {'result': False, 'message': unicode(e)}
    return HttpResponse(json.dumps(result))


def block_alarm_def(request, cc_biz_id):
    """
    屏蔽全业务自愈方案
    """
    if request.method != 'POST':
        raise HttpResponseNotAllowed
    try:
        with atomic():
            _def = AlarmDef.objects.get(id=request.POST['id'], cc_biz_id=0, )
            block_list = (_def.tnm_attr_id or '').split(',')
            if cc_biz_id in block_list:
                block_list.remove(cc_biz_id)
            else:
                block_list.append(cc_biz_id)
            _def.tnm_attr_id = ','.join(block_list)
            _def.save()
    except Exception, e:
        return HttpResponse(json.dumps({'success': False, 'message': str(e)}))
    return HttpResponse(json.dumps({'success': True}))


@is_superuser
def del_alarm_type(request, cc_biz_id):
    '''删除告警类型
    '''
    alarm_type_id = request.POST["id"]
    cc_biz_id = int(cc_biz_id)
    result = {"message": "", "result": False}
    if alarm_type_id is None:
        result["message"] = "field id is required"
        return JsonResponse(result)
    with atomic():
        for i in AlarmType.get_by_cc_biz_id(cc_biz_id, is_enabled=None, id=alarm_type_id, ):
            i.delete()
    result["result"] = True
    return JsonResponse(result)


def get_alert_alarm_types(request, cc_biz_id):
    """获取蓝鲸监控的告警类型列表
    """
    alarm_type_list = AlarmType.get_by_cc_biz_id(cc_biz_id, source_type='ALERT', )
    # 按分类排序
    alarm_type_list = sorted(alarm_type_list, key=lambda x: x.scenario)
    ctx = {'alarm_type_list': list(alarm_type_list)}
    alarm_type_page = render_mako_tostring_context(
        request, '/fta_solutions/alarm_source/alarm_source_type_alert_list.part', ctx)
    return HttpResponse(alarm_type_page)


def refresh_alert_alarm_types(request, cc_biz_id):
    """从监控的API中获取告警类型并刷新
    """
    # 从蓝鲸监控的API中获取告警类型
    alert_alarm_types = get_alert_alarm_type_api()
    # 先删除所有的蓝鲸监控告警类型
    AlarmType.objects.filter(source_type='ALERT').delete()
    for _data in alert_alarm_types:
        if _data.get('scenario') == u"主机监控":
            _type = "%s_%s" % (_data.get('monitor_type'), _data.get('monitor_target'))
        else:
            _type = _data.get('monitor_type')
        item = {
            'alarm_type': _type,
            'scenario': _data.get('scenario'),
            'description': _data.get('description'),
            'pattern': _type,
            'cc_biz_id': 0,
            'exclude': '',
            'is_enabled': True,
            'is_hidden': False,
            'match_mode': 0,
            'source_type': 'ALERT'
        }
        AlarmType.objects.create(**item)
    ctx = {'result': True, 'message': ''}
    return JsonResponse(ctx)


def alarm_source_list(request, cc_biz_id):
    """
    告警源列表页面
    """
    # 获取所有的告警源
    source_keys = [s[0] for s in fta_std.SOURCE_TYPE_CHOICES]

    # 已启用监控产品
    enable_source_list = AlarmApplication.get_enabled_list_by_biz_id(cc_biz_id)
    enable_source_key_list = enable_source_list.values_list('source_type', flat=True)
    enable_source_key_list = set(enable_source_key_list)
    # 未启用监控产品
    unable_source_key_list = [skey for skey in source_keys if (
        skey != 'QCLOUD' and skey not in enable_source_key_list)]
    page_type_dict = dict((k, v) for v, k in fta_std.SOURCE_TYPE_PAGES_CHOICES.items())
    source_type_msg1 = fta_std.SOURCE_TYPE_MSG1
    context = {
        'cc_biz_id': cc_biz_id,
        'enable_source_list': enable_source_list,
        'unable_source_key_list': unable_source_key_list,
        'page_type_dict': page_type_dict,
        'source_type_msg1': source_type_msg1,
    }
    return render_mako_context(
        request,
        '/fta_solutions/alarm_source/alarm_source_list.html',
        context
    )


def add_alarm_source(request, cc_biz_id, page_type, source_id):
    """
    新增告警源页面
    """
    source_type = fta_std.SOURCE_TYPE_PAGES_CHOICES.get(page_type, 'ZABBIX')
    is_edit = True if source_id != '0' else False
    if source_id == '0':
        # 切换监控产品时，如果已经配置，直接拉出配置信息
        alarm_apps = AlarmApplication.objects.filter(source_type=source_type)
        if alarm_apps.exists():
            alarm_apps.update(is_enabled=True)
            alarm_app = alarm_apps.first()
            _c = False
        else:
            alarm_app = AlarmApplication.objects.create(cc_biz_id=0, source_type=source_type, is_enabled=True)
            _c = True

        if _c and source_type == 'CUSTOM':
            alarm_app.exception_max_num = 5
        source_id = alarm_app.id
        # block_list = alarm_app.exclude_biz_list
        # if cc_biz_id in block_list:
        #     block_list.remove(cc_biz_id)
        # alarm_app.exclude = ','.join(block_list)
        alarm_app.save()

        # 需要用户手动配置的告警：邮件，自定义 不默认开启
        if source_type in ['EMAIL', 'CUSTOM']:
            alarm_app.is_enabled = False
            # 异常阈值初始化为：5
            if _c:
                alarm_app.exception_max_num = 5
            alarm_app.save()
    else:
        alarm_app = AlarmApplication.objects.get(id=source_id, )
    app_name = alarm_app.app_name
    app_url = alarm_app.app_url
    app_method = alarm_app.app_method
    is_enabled = alarm_app.is_enabled
    exception_max_num = alarm_app.exception_max_num
    source_type_name = alarm_app.get_source_type_display()
    source_types = dict(fta_std.SOURCE_TYPE_CHOICES).keys()
    source_type_msg2 = fta_std.SOURCE_TYPE_MSG2
    context = {
        'is_edit': is_edit,
        'cc_biz_id': cc_biz_id,
        'source_type': source_type,
        'source_type_name': source_type_name,
        'source_id': source_id,
        'page_type': page_type,
        'app_name': app_name,
        'app_url': app_url,
        'app_method': app_method,
        'source_types': source_types,
        'is_enabled': is_enabled,
        'source_type_msg2': source_type_msg2,
        'exception_max_num': exception_max_num,
    }
    return render_mako_context(
        request,
        '/fta_solutions/alarm_source/alarm_source_def.html',
        context)


def get_alarm_source(request, cc_biz_id, source_type, source_id):
    """
    获取告警源的配置信息
    """
    try:
        alarm_app = AlarmApplication.objects.get(id=source_id, )
    except Exception:
        result = {'result': False, 'message': _(u"告警源[id:%s]不存在") % source_id}
        return HttpResponse(json.dumps(result))
    context = {
        'source_id': source_id,
        'source_type': alarm_app.source_type,
        'cc_biz_id': cc_biz_id,
        'alarm_app': alarm_app,
    }
    # 蓝鲸监控只能刷新告警类型
    if source_type in ['ALERT']:
        page_name = '/fta_solutions/alarm_source/alarm_source_type_alert.part'
    else:
        page_name = '/fta_solutions/alarm_source/alarm_source_config.part'
    config_html = render_mako_tostring_context(request, page_name, context)
    result = {'result': True, 'message': config_html}
    return HttpResponse(json.dumps(result))


def config_alarm_source(request, cc_biz_id, source_id):
    """
    生成/获取告警源的配置信息
    """
    app_name = request.POST.get('app_name')
    source_type = request.POST.get('source_type')
    if not app_name:
        result = {'result': False, 'message': _(u"请填写告警源名称")}
        return HttpResponse(json.dumps(result))

    source_id = int(source_id)
    if not source_id:
        # 判断改类型的告警源是否已经添加
        is_add, _app = AlarmApplication.is_alarm_app_exist(
            source_type=source_type,
            cc_biz_id=cc_biz_id,
        )
        if is_add:
            exist_id = _app.id
            exist_page_type = _app.page_type
            exist_url = '%s/alarm_source/add/%s/%s/' % (cc_biz_id, exist_page_type, exist_id)
            result = {
                'result': False,
                'message': _(u'''告警源已存在，<a href="javascript:include_open('%s')">点击跳转</a>''') % exist_url
            }
            return HttpResponse(json.dumps(result))

        alarm_app = AlarmApplication.objects.create(
            source_type=source_type,
            cc_biz_id=0,
        )
        alarm_app.create_user = request.user.username
    else:
        alarm_app = AlarmApplication.objects.get(
            source_type=source_type,
            id=source_id,
        )
        alarm_app.update_user = request.user.username

    alarm_app.app_name = app_name
    alarm_app.save()
    source_id = alarm_app.id
    return get_alarm_source(request, cc_biz_id, source_type, source_id)


class ConfigEmailAlarmSource(View):
    SOURCE_TYPE = "EMAIL"
    validator = Draft4Validator({
        "type": "object",
        "required": [
            "username", "password", "exception_max_num",
            "server_host", "server_port", "is_secure",
        ],
        "properties": {
            "app_name": {
                "type": "string",
            },
            "username": {
                "type": "string",
                "minLength": 1,
            },
            "password": {
                "type": "string",
                "minLength": 1,
            },
            "server_host": {
                "type": "string",
                "minLength": 1,
            },
            "server_port": {
                "type": "integer",
                "minimum": 1,
            },
            "is_secure": {
                "type": "boolean",
            },
            "exception_max_num": {
                "type": "integer",
                "minimum": 0,
            },
            "items": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["value", "type"],
                    "properties": {
                        "type": {
                            "enum": [
                                "regex", "xpath", "css-selector",
                                "constant", "template"
                            ],
                        },
                        "value": {
                            "type": "string",
                        },
                        "input": {
                            "type": "string",
                        },
                        "default": {
                            "type": "string",
                        }
                    }
                }
            }
        },
    })

    def check_email_params(self, cc_biz_id, params):
        from fta_utils.component import bk

        now = arrow.get()
        request_params = {
            "app_id": cc_biz_id,
            "email": params.get("username"),
            "password": params.get("password"),
            "imap_host": params.get("server_host"),
            "imap_port": params.get("server_port"),
            "secure": params.get("is_secure"),
            "exception_max_num": params.get("exception_max_num"),
            "uin": "100",  # 腾讯云版校验
            "username": "admin",  # 社区版校验
            "limit": 0,
            "since": now.replace(minutes=-10).isoformat(),
            "before": now.isoformat(),
        }
        try:
            data = bk.fta.imap_relay(**request_params)
        except Exception as error:
            logger.exception(error)
            return False, str(error)
        if data.get("result"):
            return True, "ok"

        message = data.get("message", "unknown")
        if message.startswith("LOGIN"):
            message = _(u"登录失败")
        elif message.endswith("Name or service not known"):
            message = _(u"地址错误或网络不通")
        elif message.endswith("Connection timed out"):
            message = _(u"连接超时或网络不通")
        return False, message

    def create(self, request, cc_biz_id, params, source_id):
        # unused var
        # exception_max_num = params.pop("exception_max_num")

        # 异常阈值初始为5
        app = AlarmApplication.objects.create(
            source_type=self.SOURCE_TYPE,
            cc_biz_id=0,
            is_enabled=True,
            is_deleted=False,
            create_user=request.user.username,
            update_user=request.user.username,
            extra=json.dumps(params),
            exception_max_num=5,
        )
        return get_alarm_source(request, cc_biz_id, self.SOURCE_TYPE, app.id)

    def update(self, request, cc_biz_id, params, source_id):
        exception_max_num = params.pop("exception_max_num")
        AlarmApplication.objects.filter(
            source_type=self.SOURCE_TYPE,
            is_deleted=False,
        ).update(
            exception_max_num=exception_max_num,
            update_user=request.user.username,
            extra=json.dumps(params),
        )

        return get_alarm_source(request, cc_biz_id, self.SOURCE_TYPE, source_id)

    def post(self, request, cc_biz_id, source_id):
        if not request.user.is_superuser:
            return HttpResponse(json.dumps({
                'result': False,
                'message': _(u"请使用管理员身份管理告警源<br>注: 对告警源操作会应用所有业务")
            }))
        if not source_id.isdigit():
            return ResponseToolkit.make_json_response(
                message=_(u"id错误"),
                status_code=403,
            )
        source_id = int(source_id)
        try:
            params = json.loads(request.body)
            self.validator.validate(params)
        except Exception:
            return ResponseToolkit.make_json_response(message=_(u"参数错误"), status_code=400, )

        app = AlarmApplication.objects.filter(
            source_type=self.SOURCE_TYPE,
            is_deleted=False,
        ).last()
        if app and app.id != source_id:
            return ResponseToolkit.make_json_response(message=_(u"名称冲突"), status_code=400, )

        ok, message = self.check_email_params(cc_biz_id, params)
        if not ok:
            return ResponseToolkit.make_json_response(
                message=_(u"配置错误: %s") % message,
                status_code=400,
            )
        cp = cipher.AESCipher.default_cipher()
        password = params["password"].encode("utf-8")
        params["password"] = cp.decrypt(password) if cp else password
        if not source_id:
            return self.create(request, cc_biz_id, params, source_id)
        else:
            return self.update(request, cc_biz_id, params, source_id)


@is_superuser
def config_custom_alarm_source(request, cc_biz_id, source_id):
    """
    生成/获取告警源的配置信息
    自定义告警与业务无关
    """
    app_name = request.POST.get('app_name')
    app_url = request.POST.get('app_url')
    app_method = request.POST.get('app_method')
    exception_max_num = request.POST.get('exception_max_num')

    source_type = request.POST.get('source_type')
    if not (app_name and app_url and app_method):
        logger.error(
            u"config_custom_alarm_source param error，app_name:%s, app_url:%s, app_method:%s" % (
                app_name, app_url, app_method
            )
        )
        result = {'result': False, 'message': _(u"请填写告警源信息")}
        return HttpResponse(json.dumps(result))

    source_id = int(source_id)
    if not source_id:
        # 判断改类型的告警源是否已经添加
        is_add, _app = AlarmApplication.is_alarm_app_exist(
            source_type=source_type,
            cc_biz_id=0,
        )
        if is_add:
            exist_id = _app.id
            exist_page_type = _app.page_type
            exist_url = '%s/alarm_source/add/%s/%s/' % (cc_biz_id, exist_page_type, exist_id)
            result = {
                'result': False,
                'message': _(u'''告警源已存在，<a href="javascript:include_open('%s')">点击跳转</a>''') % exist_url
            }
            return HttpResponse(json.dumps(result))
        alarm_app = AlarmApplication.objects.create(
            source_type=source_type,
            cc_biz_id=0,
        )
        alarm_app.create_user = request.user.username
    else:
        alarm_app = AlarmApplication.objects.get(
            source_type=source_type,
            id=source_id,
        )
        alarm_app.update_user = request.user.username

    alarm_app.app_name = app_name
    alarm_app.app_url = app_url
    alarm_app.app_method = app_method
    if exception_max_num:
        alarm_app.exception_max_num = exception_max_num
    alarm_app.save()
    source_id = alarm_app.id
    return get_alarm_source(request, cc_biz_id, source_type, source_id)


@is_superuser
def reset_alarm_source(request, cc_biz_id, source_id):
    """
    重置告警源信息
    """
    alarms = AlarmApplication.objects.filter(id=source_id)
    alarms.update(app_secret=gen_app_secret())
    source_type = alarms[0].source_type if alarms else ''
    return get_alarm_source(request, cc_biz_id, source_type, source_id)


@is_superuser
def switch_alarm_source(request, cc_biz_id):
    """
    开启、禁用告警源信息(全局操作，只有管理员可以操作)
    """
    try:
        source_type = request.POST.get('source_type')
        enable = request.POST.get('enable')
        if not source_type:
            return HttpResponse(json.dumps({
                'result': False,
                'message': u"请选择告警源"
            }))
        enable = True if enable == '1' else False
        def_sets = AlarmApplication.objects.filter(source_type=source_type)
        def_sets.update(is_enabled=enable)
        # 重新开启告警源信息时，重置异常信息
        if enable:
            def_sets.update(
                exception_num=0,
                exception_data='',
                exception_begin_time=None,
                empty_num=0,
                empty_begin_time=None,
            )
        else:
            # 禁用相关的接入自愈策略
            AlarmDef.block_by_source_type(cc_biz_id, source_type)
    except Exception as e:
        logger.exception(u"switch_alarm_source error :%s" % e)
        # result = {'result': False, 'message': _(u"开启/禁用警源出错")}
    result = {'result': True, 'message': ''}
    return HttpResponse(json.dumps(result))


@is_superuser
def block_alarm_source(request, cc_biz_id):
    """
    开启、关闭 蓝鲸监控告警源（已经废弃）
    """
    try:
        blocked = False
        with atomic():
            _def = AlarmApplication.objects.get(
                id=request.POST['id']
            )
            block_list = (_def.exclude or '').split(',')
            if cc_biz_id in block_list:
                block_list.remove(cc_biz_id)
            else:
                blocked = True
                block_list.append(cc_biz_id)
            _def.exclude = ','.join(block_list)
            _def.save()
        if blocked:
            # 同时禁用相关的AlarmDef
            AlarmDef.block_by_source_type(cc_biz_id, _def.source_type)
    except Exception as e:
        return HttpResponse(json.dumps({'result': False, 'message': str(e)}))
    return HttpResponse(json.dumps({'result': True}))


@login_exempt
def download_alarm_source_script(request, cc_biz_id, script_name):
    script_name = script_name.replace("/", "_")
    fta_application_id = request.GET.get("fta_application_id")
    fta_application_secret = request.GET.get("fta_application_secret")
    if (
        not (fta_application_id and fta_application_secret) or
        not models.AlarmApplication.objects.filter(
            app_id=fta_application_id,
            app_secret=fta_application_secret,
        ).exists()
    ):
        return HttpResponseNotFound()

    context = {
        "cc_biz_id": cc_biz_id,
        "script_name": script_name,
        "fta_application_id": fta_application_id,
        "fta_application_secret": fta_application_secret,
        "endpoint": settings.FTA_API_PREFIX,
        "fotmat": getattr(settings, "ALARM_SOURCE_REQUEST_FORMAT", "base64"),
    }
    context.update({k: v for k, v in request.GET.items() if not k.startswith("_")})

    try:
        response = render(
            request, "fta_solutions/alarm_scripts/%s" % script_name,
            context, content_type="text/plain",
        )
    except TemplateDoesNotExist:
        return HttpResponseNotFound()

    response['Content-Disposition'] = 'attachment; filename=%s' % script_name
    return response
