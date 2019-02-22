# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""添加9个默认策略cpu/内存默认接入策略
"""
import traceback

from fta_solutions_app.models import AlarmDef, Solution


def get_solution_by_codename(solution_code_name):
    s = Solution.objects.filter(codename=solution_code_name)
    if s:
        return s.first().id
    return None


MODEL = AlarmDef


def RUNNER(apps, schema_editor, module, silent):  # noqa
    for item in module.DATA:
        try:
            solution_code_name = item.pop('solution_code_name')
            solution_id = get_solution_by_codename(solution_code_name)
            item['solution_id'] = solution_id
            module.MODEL.objects.create(**item)
        except Exception:
            if not silent:
                raise
            print(traceback.format_exc())


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

SOLUTION_CODENAME_CPU_DEFAULT = "cpu_proc_top10"
SOLUTION_CODENAME_MEM_DEFAULT = "mem_proc_top10"
DATA = [
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "mem_60",
        "description": "%s默认套餐" % "可用物理内存",
        "solution_code_name": SOLUTION_CODENAME_MEM_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "mem_63",
        "description": "%s默认套餐" % "交换分区使用量",
        "solution_code_name": SOLUTION_CODENAME_MEM_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "mem_64",
        "description": "%s默认套餐" % "物理内存使用率",
        "solution_code_name": SOLUTION_CODENAME_MEM_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "mem_97",
        "description": "%s默认套餐" % "物理内存使用量",
        "solution_code_name": SOLUTION_CODENAME_MEM_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "mem_98",
        "description": "%s默认套餐" % "应用内存使用量",
        "solution_code_name": SOLUTION_CODENAME_MEM_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "mem_99",
        "description": "%s默认套餐" % "应用内存使用率",
        "solution_code_name": SOLUTION_CODENAME_MEM_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "cpu_3",
        "description": "%s默认套餐" % "5分钟平均负载",
        "solution_code_name": SOLUTION_CODENAME_CPU_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "cpu_7",
        "description": "%s默认套餐" % "CPU总使用率",
        "solution_code_name": SOLUTION_CODENAME_CPU_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
    {
        "is_enabled": False,
        "is_deleted": False,
        "category": "sys",
        "cc_biz_id": 0,
        "alarm_type": "cpu_8",
        "description": "%s默认套餐" % "CPU单核使用率",
        "solution_code_name": SOLUTION_CODENAME_CPU_DEFAULT,
        "ok_notify": True,
        "notify": default_notity,
        "timeout": 40,
        "source_type": "ALERT",
        "create_user": "admin",
        "add_from": "sys"
    },
]
