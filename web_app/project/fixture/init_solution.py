# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.conf import settings
from django.utils.translation import ugettext as _

from fta_solutions_app.models import Solution

OPERATOR = "100"

MODEL = Solution
DATA = [{
    'cc_biz_id': 0L,
    'codename': u'diy_only',
    'config': u' {}',
    'creator': u'admin',
    'id': 4L,
    'solution_type': u'switch_ip',
    'title': _(u'『快捷』后续处理对象故障机与备机互换')
}, {
    'cc_biz_id': 0L,
    'codename': u'diy_only',
    'config':
        u'{"module_name":"bk.cc","task_name":"clone_host_property","task_kwargs":"{\\n    \\"uin\\": \\"' + OPERATOR +
        u'\\",\\n    \\"operator\\": \\"${operator}\\",\\n \\"app_id\\": \\"${cc_biz_id}\\",'
        u'\\n    \\"plat_id\\":\\"${cc|plat_id}\\",\\n    \\"org_ip\\":\\"${bpm_context|alarm_ci_name}\\" ,'
        u'\\n    \\"dst_ip\\":\\"${bpm_context|ip_bak}\\"   \\n}"}',
    'creator': u'admin',
    'id': 5L,
    'solution_type': u'bk_component',
    'title': _(u'『快捷』CC拷贝故障机属性到备机')
}, {
    'cc_biz_id': 0L,
    'codename': u'diy_only',
    'config':
        u'{"module_name":"bk.cc","task_name":"update_host_module","task_kwargs":"{\\n    \\"uin\\": \\"' + OPERATOR +
        u'\\",\\n    \\"operator\\": \\"${operator}\\",\\n\\"app_id\\": \\"${cc_biz_id}\\", \\n    \\"plat_id\\": '
        u'\\"${cc|plat_id}\\",\\n    \\"dst_module_id\\": \\"${cc|idle_module_id}\\",\\n    \\"ip\\": \\"${'
        u'ip}\\"\\n}"}',
    'creator': u'admin',
    'id': 6L,
    'solution_type': u'bk_component',
    'title': _(u'『快捷』CC移到“空闲机”模块')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"app_id":"' +
        settings.ALL_BIZ_APP_ID +
        u'","task_id":"' +
        settings.TOP_MEM_TASK_ID +
        u'",'
        u'"ijobs_taski_name":"\u300e\u5feb\u6377\u300f\u83b7\u53d6\u5185\u5b58\u4f7f\u7528\u7387TOP10\u7684\u8fdb'
        u'\u7a0b","parms":"","parms0":"","argv":"on","retry_time":"10","retry_count":"2","steps":"1","operator":"' +
        OPERATOR + u'"}',
    'creator': u'admin',
    'id': 7L,
    'solution_type': u'ijobs',
    'title': _(u'『Non-Display』获取内存使用率TOP10的进程')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"app_id":"' +
        settings.ALL_BIZ_APP_ID +
        u'","task_id":"' +
        settings.TOP_CPU_TASK_ID +
        u'",'
        u'"ijobs_taski_name":"\u300e\u5feb\u6377\u300f\u83b7\u53d6CPU\u4f7f\u7528\u7387TOP10\u7684\u8fdb\u7a0b",'
        u'"parms":"","parms0":"","argv":"on","retry_time":"10","retry_count":"2","steps":"1","operator":"' + OPERATOR +
        u'"}',
    'creator': u'admin',
    'id': 8L,
    'solution_type': u'ijobs',
    'title': _(u'『Non-Display』获取CPU使用率TOP10的进程')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"message":"\u3010\u6545\u969c\u81ea\u6108\u3011CPU\u4f7f\u7528\u7387TOP10\u5217\u8868\uff1a\\n\u4e1a\u52a1'
        u'\uff1a\\"${cc|ApplicationName}\\"\\n\u6a21\u5757\uff1a\\"${cc|ModuleName}\\"\\n\u4e3b\u673a\uff1a${'
        u'ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_cpu}","extra_people":"",'
        u'"extra_people_select":null,"wechat":"on"}',
    'creator': u'admin',
    'id': 9L,
    'solution_type': u'notice',
    'title': _(u'『Non-Display』发送CPU使用率TOP10的进程(微信)')
}, {
    'cc_biz_id': 0L,
    'codename': u'cpu_proc_top10',
    'config': u'{"real_solutions":"[[{\\"1\\": [\\"success\\"]}, \\"8\\"], [{}, \\"9\\"]]"}',
    'creator': u'admin',
    'id': 10L,
    'solution_type': u'graph',
    'title': _(u'『快捷』发送CPU使用率TOP10的进程(微信)')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"message":"\u3010\u6545\u969c\u81ea\u6108\u3011\u5185\u5b58\u4f7f\u7528\u7387TOP10\u5217\u8868\uff1a\\n'
        u'\u4e1a\u52a1\uff1a\\"${cc|ApplicationName}\\"\\n\u6a21\u5757\uff1a\\"${'
        u'cc|ModuleName}\\"\\n\u4e3b\u673a\uff1a${ip}\\n---------------------------------------\\n${'
        u'bpm_context|ijobs_return_mem}","extra_people":"","extra_people_select":null,"wechat":"on"}',
    'creator': u'admin',
    'id': 24L,
    'solution_type': u'notice',
    'title': _(u'『Non-Display』发送内存使用率TOP10的进程(微信)')
}, {
    'cc_biz_id': 0L,
    'codename': u'mem_proc_top10',
    'config': u'{"real_solutions":"[[{\\"1\\": [\\"success\\"]}, \\"7\\"], [{}, \\"24\\"]]"}',
    'creator': u'admin',
    'id': 25L,
    'solution_type': u'graph',
    'title': _(u'『快捷』发送内存使用率TOP10的进程(微信)')
}, {
    'cc_biz_id': 0L,
    'codename': u'cc_to_fault_module',
    'config':
        u'{"module_name":"bk.cc","task_name":"update_host_module","task_kwargs":"{\\n    \\"uin\\": \\"' + OPERATOR +
        u'\\",\\n    \\"operator\\": \\"${operator}\\",\\n\\"app_id\\": \\"${cc_biz_id}\\", \\n    \\"plat_id\\": '
        u'\\"${cc|plat_id}\\",\\n    \\"dst_module_id\\": \\"${cc|fault_module_id}\\",\\n    \\"ip\\": \\"${ip}\\" '
        u'\\n}"}',
    'creator': u'admin',
    'id': 36L,
    'solution_type': u'bk_component',
    'title': _(u'『快捷』CC移到“故障机”模块')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"message":"\u3010\u6545\u969c\u81ea\u6108\u3011CPU\u4f7f\u7528\u7387TOP10\u5217\u8868\uff1a\\n\u4e1a\u52a1'
        u'\uff1a\\"${cc|ApplicationName}\\"\\n\u6a21\u5757\uff1a\\"${cc|ModuleName}\\"\\n\u4e3b\u673a\uff1a${'
        u'ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_cpu}","extra_people":"",'
        u'"extra_people_select":null,"sms":"on"}',
    'creator': u'admin',
    'id': 37L,
    'solution_type': u'notice',
    'title': _(u'『Non-Display』发送CPU使用率TOP10的进程(短信)')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"message":"\u3010\u6545\u969c\u81ea\u6108\u3011CPU\u4f7f\u7528\u7387TOP10\u5217\u8868\uff1a\\n\u4e1a\u52a1'
        u'\uff1a\\"${cc|ApplicationName}\\"\\n\u6a21\u5757\uff1a\\"${cc|ModuleName}\\"\\n\u4e3b\u673a\uff1a${'
        u'ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_cpu}","extra_people":"",'
        u'"extra_people_select":null,"email":"on"}',
    'creator': u'admin',
    'id': 38L,
    'solution_type': u'notice',
    'title': _(u'『Non-Display』发送CPU使用率TOP10的进程(邮件)')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"message":"\u3010\u6545\u969c\u81ea\u6108\u3011\u5185\u5b58\u4f7f\u7528\u7387TOP10\u5217\u8868\uff1a\\n'
        u'\u4e1a\u52a1\uff1a\\"${cc|ApplicationName}\\"\\n\u6a21\u5757\uff1a\\"${'
        u'cc|ModuleName}\\"\\n\u4e3b\u673a\uff1a${ip}\\n---------------------------------------\\n${'
        u'bpm_context|ijobs_return_mem}","extra_people":"","extra_people_select":null,"sms":"on"}',
    'creator': u'admin',
    'id': 39L,
    'solution_type': u'notice',
    'title': _(u'『Non-Display』发送内存使用率TOP10的进程(短信)')
}, {
    'cc_biz_id': 0L,
    'codename': u'non-display',
    'config':
        u'{"message":"\u3010\u6545\u969c\u81ea\u6108\u3011\u5185\u5b58\u4f7f\u7528\u7387TOP10\u5217\u8868\uff1a\\n'
        u'\u4e1a\u52a1\uff1a\\"${cc|ApplicationName}\\"\\n\u6a21\u5757\uff1a\\"${'
        u'cc|ModuleName}\\"\\n\u4e3b\u673a\uff1a${ip}\\n---------------------------------------\\n${'
        u'bpm_context|ijobs_return_mem}","extra_people":"","extra_people_select":null,"email":"on"}',
    'creator': u'admin',
    'id': 40L,
    'solution_type': u'notice',
    'title': _(u'『Non-Display』发送内存使用率TOP10的进程(邮件)')
}]
