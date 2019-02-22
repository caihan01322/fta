# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from fta.utils.i18n import _

"""
CONSTANTS for business logic, no need to change for any deployment env.
If it needs to change for different deployment env,
it should be put into settings.
"""

ALARM_BASE_KEY = [
    "host",
    "source_type",
    "source_id",
    "category",
    "alarm_type",
    "alarm_time",
    "alarm_desc",
    "alarm_attr_id",
    "alarm_process",
    "alarm_port",
    "alarm_responsible",
    "cc_company_id",
    "cc_plat_id",
    "cc_biz_id",
    "cc_topo_set",
    "cc_app_module",
    "cc_set_category",
    "cc_set_envi_type",
    "cc_set_service_state",
    "cc_idc_unit",
    "cc_equipment",
    "cc_link_net_device",
    "alarm_def_id",
    "alarm_context"
]

ALARM_MATCH_KEY = {
    # value can be "&&" "<=" "==" "re"
    "source_type": "==",
    "alarm_type": "&&",
    "alarm_desc": "re",
    "alarm_attr_id": "<=",
    "alarm_process": "<=",
    "alarm_responsible": "<=",
    "cc_biz_id": "==",
    "cc_plat_id": "==",
    "cc_topo_set": "&&",
    "cc_app_module": "&&",
    "host": "&&",
    "exclude_biz_ids": ">=",
}

ALARM_DIMENSION_KEY = {
    # ----- define your key below ----
    "host": _("Host"),
    "alarm_type": _("Alarm Type"),
    "cc_biz_id": _("Business"),
    "cc_topo_set": _("Set"),
    "solution": _("Solution"),
}

UNIVERSALITY_DIMENSION_KEY = {
    "cc_topo_set": ALARM_DIMENSION_KEY.get("cc_topo_set"),
}

# Cache默认时间, 30 分钟
CACHE_TIMEOUT = 60 * 30

# #################### 作业平台相关常量 ####################
# 磁盘清理作业
CLEAN_TASK_ID = '4'
# 获取占用内存最多的Top10进程
TOP_MEM_TASK_ID = '3'
# 获取占用CPU最多的Top10进程
TOP_CPU_TASK_ID = '2'
# 跨业务作业集合
ALL_BIZ_TASKS = [CLEAN_TASK_ID, TOP_MEM_TASK_ID, TOP_CPU_TASK_ID]
# 跨业务的 stepId
ALL_BIZ_STEP_ID = {
    TOP_CPU_TASK_ID: '11',
    TOP_MEM_TASK_ID: '12',
    CLEAN_TASK_ID: '13'
}
# 跨业务作业执行时指定的业务id
ALL_BIZ_APP_ID = '77770001'
# 磁盘清理的作业脚本参数
CLEAN_TASK_PARAM = {
    "app_id": "77770001",
    "task_id": "4",
    "parms": "",
    "parms0": "%s",
    "argv": "on",
    "retry_time": "",
    "retry_count": "",
    "steps": "1",
    "operator": "100"
}

# 跨业务作业的详情是否需要单独处理
IS_TASKS_RESULT_SPECIAL = False
