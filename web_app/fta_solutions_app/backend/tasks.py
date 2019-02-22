# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
这里只放前端用户手动触发的异步任务
"""

from django.conf import settings
from django.utils.translation import ugettext as _

from fta_solutions_app.backend.utils import get_fta_admin_str
from fta_solutions_app.models import AlarmDef, Conf
from fta_utils.cc import CCBiz
from project.component import send
from project.conf.user import get_full_name

ENV = _(u' (Test环境)') if settings.RUN_MODE in ('DEVELOP', 'TEST') else ''

TITLE = _(u'【自愈通知】%s 业务接入变动通知') % ENV


# 基于业务的通知
# 业务第一个告警启用， 和业务最后一个告警禁用
# 由于接口性能很好，为了减少 celery 的使用，改为同步任务
# @task(ignore_result=True)
def send_update_to_ifix(updated_alarm_def, enable_count, operator):
    added = updated_alarm_def.is_enabled and enable_count == 1
    removed = not updated_alarm_def.is_enabled and enable_count == 0

    if added or removed:
        action = _(u'接入') if added else _(u'去除')
        cc_biz = CCBiz(username=operator).items("ApplicationID", "ApplicationName")
        show_name = get_full_name(operator)
        brief = _(u'变动项：%s［%s］了［%s］业务') % (
            show_name,
            action,
            cc_biz.get(str(updated_alarm_def.cc_biz_id), updated_alarm_def.cc_biz_id),
        )

        biz_list = AlarmDef.objects.filter(
            is_enabled=True, category='default'
        ).distinct().values_list('cc_biz_id', flat=True)

        content = _(u'<hr>当前已启用自愈的业务汇总： ［')
        content += u'， '.join([u'%s' % cc_biz.get(str(biz), biz) for biz in biz_list])
        content += u'］'

        try:
            receiver = Conf.objects.get(name='IFIX_UPDATE_RECEIVER').value
        except Exception:
            receiver = get_fta_admin_str()

        send.wechat(receiver, TITLE + '\r\n' + brief)
        send.mail(receiver, '<h3>' + brief + '</h3>' + content, TITLE)
