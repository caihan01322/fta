# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from django.db.transaction import atomic
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import View

from common.log import logger
from common.mymako import render_mako_context
from fta_solutions_app.cache_utils import get_module_id_by_name, get_set_id_by_name
from fta_solutions_app.models import AlarmApplication, OutOfScopeArchive, AlarmDef


def fta_helper(request, cc_biz_id):
    """
    自愈小助手
    """
    # 判断业务下是否已有启用的告警源
    enable_source_list = AlarmApplication.get_enabled_list_by_biz_id(cc_biz_id)
    enable_source_count = enable_source_list.count()
    if enable_source_count == 0:
        return render_mako_context(request, '/fta_helper/no_alram_source.html', {'cc_biz_id': cc_biz_id})

    # 业务下分析出的待用户确认的方案列表
    suggest_list = OutOfScopeArchive.get_suggest_list(cc_biz_id)
    suggest_count = suggest_list.count()
    # 用户已启用的方案
    enable_list = OutOfScopeArchive.get_enabled_list(cc_biz_id)
    enable_count = enable_list.count()
    if not suggest_count:
        return render_mako_context(request, '/fta_helper/no_tips.html', {
            'cc_biz_id': cc_biz_id,
            'suggest_count': suggest_count,
            'enable_count': enable_count
        })
    return render_mako_context(request, '/fta_helper/suggest_list.html', {
        'cc_biz_id': cc_biz_id,
        'suggest_list': suggest_list,
        'suggest_count': suggest_count,
    })


class OutOfScopeArchiveSource(View):
    """自愈未接入告警分析"""
    default_notity = '''{
        "begin_notify_wechat":true,
        "begin_notify_mail":true,
        "begin_notify_sms":false,
        "begin_notify_im":false,
        "begin_notify_phone":false,
        "success_notify_wechat":true,
        "success_notify_mail":true,
        "success_notify_sms":false,
        "success_notify_im":false,
        "success_notify_phone":false,
        "failure_notify_wechat":true,
        "failure_notify_mail":true,
        "failure_notify_sms":false,
        "failure_notify_im":false,
        "failure_notify_phone":false,
        "to_extra":false,
        "to_role":true
    }'''

    def post(self, request, cc_biz_id, suggest_id):
        """启用自愈方案
        1）将方案添加到 AlarmDef 表中
        2）OutOfScopeArchive 的 status 字段设置为 enabled
        2）将 alarm_def_id 添加到 OutOfScopeArchive 的 extra 字段中
        """
        if not suggest_id.isdigit():
            return HttpResponse(json.dumps({'result': False, 'message': u"id error"}))

        try:
            _archive = OutOfScopeArchive.objects.get(id=suggest_id)
        except Exception as e:
            logger.error(u"OutOfScopeArchive [id:%s] 记录不存在:%s" % (suggest_id, e))
            return HttpResponse(json.dumps({'result': False, 'message': u"id error"}))

        try:
            with atomic():
                # 判断业务下的告警源是否已启用
                enable_source_list = AlarmApplication.get_enabled_list_by_biz_id(cc_biz_id)
                _source_type_list = enable_source_list.values_list('source_type', flat=True)
                is_alarm_def_enbaled = True if _archive.source_type in _source_type_list else False

                user_name = request.user.username
                # 根据set、module 名称获取id信息
                set_id = get_set_id_by_name(_archive.cc_set_name, cc_biz_id, user_name)
                module_id = get_module_id_by_name(_archive.cc_module, cc_biz_id, user_name)
                # 将方案添加到 AlarmDef 表中
                alarm_def = AlarmDef.objects.create(
                    cc_biz_id=cc_biz_id,
                    alarm_type=_archive.alarm_type,
                    description='%s_%s' % (_archive.alarm_def_description, _archive.id),
                    source_type=_archive.source_type,
                    solution_id=_archive.solution_id,
                    set_names=_archive.cc_set_name,
                    module_names=_archive.cc_module,
                    topo_set=set_id,
                    module=module_id,
                    create_user=user_name,
                    update_user=user_name,
                    is_enabled=is_alarm_def_enbaled,
                    notify=self.default_notity,
                    add_from='sys',
                )
                alarm_def_id = alarm_def.id

                # 更新 OutOfScopeArchive
                extra_data = _archive.extra_data
                extra_data['alarm_def_id'] = alarm_def_id
                _archive.status = 'enabled'
                _archive.extra = json.dumps(extra_data)
                _archive.save()
        except Exception, e:
            return HttpResponse(json.dumps({'success': False, 'message': str(e)}))
        return HttpResponse(json.dumps({'result': True, 'message': _(u"自愈方案已启用")}))

    def delete(self, request, cc_biz_id, suggest_id):
        """忽略自愈方案
        """
        if not suggest_id.isdigit():
            return HttpResponse(json.dumps({'result': False, 'message': u"id error"}))

        try:
            _archive = OutOfScopeArchive.objects.get(id=suggest_id)
        except Exception as e:
            logger.error(u"OutOfScopeArchive [id:%s] 记录不存在:%s" % (suggest_id, e))
            return HttpResponse(json.dumps({'result': False, 'message': u"id error"}))

        _archive.status = 'ignore'
        _archive.save()
        return HttpResponse(json.dumps({'result': True, 'message': _(u"自愈方案已忽略")}))
