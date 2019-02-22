# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.utils.translation import ugettext as _

from fta_solutions_app.models import AlarmType

MODEL = AlarmType
ITEM_CHECKER = lambda apps, item: not AlarmType.objects.filter(
    alarm_type=item["alarm_type"],
    source_type=item["source_type"],
    description=item["description"],
    cc_biz_id=0,
).exists()
CHECKER = lambda apps: True


def RUNNER(apps, schema_editor, module, silent):  # noqa
    for item in module.DATA:
        try:
            refs = module.MODEL.objects.filter(
                source_type=item['source_type'],
                cc_biz_id=item['cc_biz_id'],
                alarm_type=item['alarm_type'])
            if refs:
                refs.update(
                    description=item['description'])
            else:
                module.MODEL.objects.create(**item)
        except Exception:
            pass


DATA = [
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": _(u"系统启动时间异常"),
        "pattern": "system_env_os_restart",
        "alarm_type": "system_env_os_restart",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    }
]
