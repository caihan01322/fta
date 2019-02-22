# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
管理员入口：操作对所有业务生效
权限：只验证用户权限（管理员）
"""
import json

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import View
from jsonschema import Draft4Validator

from account.decorators import is_superuser, is_superuser_cls
from common.log import logger
from common.mymako import render_mako_context
from fta_solutions_app import cache_utils as cash
from fta_solutions_app import fta_std
from fta_solutions_app.models import AlarmType, AlarmDef, Solution, AlarmApplication


@is_superuser
def alarm_defs(request):
    """
    全业务自愈接入列表
    """
    alarm_type_dict = AlarmType.get_description_mappings(0, is_enabled=None)
    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    alarm_list = AlarmDef.objects.filter(cc_biz_id=0)
    context = {
        'alarm_type_dict': alarm_type_dict,
        'source_type_dict': source_type_dict,
        'alarm_list': alarm_list
    }
    return render_mako_context(request, '/fta_admin/alarm_defs.html', context)


@is_superuser
def show_alarm_def(request, alarm_def_id):
    """
    接入详情页
    """
    username = request.user.username

    alarm_type_dict = AlarmType.get_description_mappings(0, is_enabled=None)

    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    src_type_group = AlarmType.get_source_type_mappings(0, is_enabled=None)

    if alarm_def_id == '0':
        edit = False
        alarm_def = None
        responsible_list = []
    else:
        edit = True
        alarm_def = AlarmDef.objects.get(cc_biz_id=0, id=alarm_def_id)
        responsible_list = alarm_def.responsible.split(';') if alarm_def.responsible else []

    # 开发商下所有用户
    all_user_info = cash.get_all_user_info(0, username)

    solution_list = Solution.objects.filter(
        cc_biz_id__in=[0],
    ).order_by('cc_biz_id', 'title')

    return render_mako_context(request, '/fta_admin/alarm_def.html', dict(
        alarm_def_id=alarm_def_id,
        edit=edit,
        alarm_def=alarm_def,
        alarm_type_dict=alarm_type_dict,
        src_type_group=src_type_group,
        solution_list=solution_list,
        source_type_dict=source_type_dict,
        all_user_info=all_user_info,
        responsible_list=responsible_list,
    ))


class AlarmDefSource(View):
    """全业务接入自愈"""
    # AlarmDef 表的参数验证格式
    validator = Draft4Validator({
        "type": "object",
        "required": [
            "alarm_type",
            "description",
            "timeout"
        ],
        "properties": {
            "is_enabled": {
                "type": "boolean",
            },
            "alarm_type": {
                "type": "string",
                "minLength": 1,
            },
            "description": {
                "type": "string",
                "minimum": 1,
            },
            "timeout": {
                "type": "string",
            },
            "responsible": {
                "type": "string",
            },
            "reg": {
                "type": "string",
            },
            "notify": {
                "type": "string",
            },
            "source_type": {
                "type": "string",
            },
            "solution_id": {
                "type": "string",
            },
            "create_user": {
                "type": "string",
            },
            "update_user": {
                "type": "string",
            },
        },
    })

    @is_superuser_cls
    def create(self, request, alarm_def_id, params):
        user_name = request.user.username
        source_type = params.get('source_type')
        # 如果有业务未启用该告警源，则将该业务加入到排除列表中
        exclue_list = []
        alarm_apps = AlarmApplication.objects.filter(source_type=source_type)
        for _apps in alarm_apps:
            # 全业务生效的告警源
            if _apps.cc_biz_id == 0:
                # 未开启时，提示用户先开启告警源
                if not _apps.is_enabled:
                    message = _(u"请先到[管理告警源]中启用%s") % _apps.source_name
                    return HttpResponse(json.dumps({'result': False, 'message': message}))
                else:
                    exclue_list = _apps.exclude.split(',') if _apps.exclude else []
                break
            elif not _apps.is_enabled:
                exclue_list.append(str(_apps.cc_biz_id))
        try:
            exclude = ','.join(exclue_list)
            AlarmDef.objects.create(
                cc_biz_id=0,
                alarm_type=params.get('alarm_type'),
                reg=params.get('reg'),
                timeout=params.get('timeout'),
                description=params.get('description'),
                responsible=params.get('responsible'),
                notify=params.get('notify'),
                source_type=source_type,
                solution_id=params.get('solution_id'),
                create_user=user_name,
                update_user=user_name,
                is_enabled=True,
                tnm_attr_id=exclude,
                add_from='admin',
            )
        except Exception as e:
            logger.error(u"create alarm_def error:%s" % e)
            return HttpResponse(json.dumps({'result': False, 'message': unicode(e)}))
        return HttpResponse(json.dumps({'result': True}))

    @is_superuser_cls
    def update(self, request, alarm_def_id, params):
        user_name = request.user.username
        try:
            AlarmDef.objects.filter(cc_biz_id=0, id=alarm_def_id).update(
                alarm_type=params.get('alarm_type'),
                reg=params.get('reg'),
                timeout=params.get('timeout'),
                description=params.get('description'),
                responsible=params.get('responsible'),
                notify=params.get('notify'),
                source_type=params.get('source_type'),
                solution_id=params.get('solution_id'),
                create_user=user_name,
                update_user=user_name,
            )
        except Exception as e:
            logger.error(u"create alarm_def Error:%s" % e)
            return HttpResponse(json.dumps({'result': False, 'message': unicode(e)}))
        return HttpResponse(json.dumps({'result': True}))

    @is_superuser_cls
    def post(self, request, alarm_def_id):
        if not alarm_def_id.isdigit():
            return HttpResponse(json.dumps({'result': False, 'message': u"id error"}))

        alarm_def_id = int(alarm_def_id)
        try:
            params = json.loads(request.body)
            self.validator.validate(params)
        except Exception as error:
            print error
            return HttpResponse(json.dumps({'result': False, 'message': u"param error"}))

        description = params.get('description')
        is_exists = AlarmDef.objects.filter(
            description=description).exclude(
            id=alarm_def_id).exists()

        if is_exists:
            message = _(u"自愈方案名称[%s]已存在") % description
            return HttpResponse(json.dumps({'result': False, 'message': message}))

        if not alarm_def_id:
            return self.create(request, alarm_def_id, params)
        else:
            return self.update(request, alarm_def_id, params)

    @is_superuser_cls
    def delete(self, request, alarm_def_id):
        result = {'result': True}
        try:
            AlarmDef.objects.filter(cc_biz_id=0, id=alarm_def_id).delete()
        except Exception, e:
            result = {'result': False, 'message': unicode(e)}
        return HttpResponse(json.dumps(result))
