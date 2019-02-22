# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
生成伪造数据，真实环境请替换真实数据源
同时也定义了推荐的数据格式
"""
import arrow

from fta.utils.i18n import _


def get_alarms():
    """生成伪造的告警"""
    return [{
        "alarm_id": arrow.utcnow().format("YYYY-MM-DD HH:mm"),
        "create_time": arrow.utcnow().format("YYYY-MM-DD HH:mm:ss"),
        "alarm_type": "ping",
        "ip": "127.0.0.1",
        "raw": _("Machine PING timeout alarm"),
    }]


def get_alarm_def():
    """生成伪造的告警定义"""
    return {
        "1": {  # alarm_def_id
            "id": 1,
            "dimension": {
                "alarm_type": ["ping"],
            },
            "alarm_type": "ping",
            "timeout": "10",
            "solution_id": 1,
        },
    }


def get_incident_def():
    """生成伪造的收敛定义"""
    return {
        "1": {
            "id": 1,
            "cc_biz_id": "10",
            "exclude_cc_biz_id": "",
            "description": _("Demo convergence"),
            "alarm_type": "ping",
            "timedelta": "15",
            "count": "1",
            "condition": {
                "alarm_type": ["ping"],
                "cc_biz_id": ["self"],
            },
            "incident_func": "pass",
        },
    }


def get_solution():
    """生成伪造的套餐定义"""
    return {
        "1": {
            "id": 1,
            "cc_biz_id": "10",
            "title": _("Demo solution"),
            "solution_type": "test",
            "conf": "{}",
        },
    }
