# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
CONSTANTS for business logic, no need to change for any deployment env.
If it needs to change for different deployment env,
it should be put into settings.
"""

ALARM_BASE_KEY = [
    # ----- STD key begin
    "source_type",
    "source_id",
    "alarm_type",
    "alarm_time",
    "alarm_desc",
    "cc_biz_id",
    # ----- STD key end

    # ----- define your key below ----

]

ALARM_MATCH_KEY = {
    # value can be "&&" "<=" "==" "re"

    # ----- define your key below ----
    "alarm_type": "&&",

}

ALARM_DIMENSION_KEY = {
    # ----- define your key below ----
    "alarm_type": u"告警类型",

}

ALARM_TYPE_DESCRIPTION = {
    # ----- define your key below ----
    "ping": u"PING超时",

}

FTA_ADMIN_LIST = ["admin"]  # replace admin account
