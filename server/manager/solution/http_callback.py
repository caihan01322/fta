# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import requests

from fta.solution.base import BaseSolution
from fta.utils import logging
from fta.utils.i18n import _
from manager.solution.bk_component import VAR

logger = logging.getLogger("solution")


class Solution(BaseSolution):
    '''
    HTTP 回调套餐
    POST <URL>
    {
        "alarm_def_id": 1,
        "ip": "10.0.0.1",
        "source_type": "NAGIOS",
        "source_time": "2017-09-04T11:44:19.124258+08:00",
        "cc_biz_id": "21480"
    }
    '''

    def run(self):
        conf = VAR(self.alarm_instance).render_kwargs(self.conf)
        url = conf.get("url")
        if not url:
            self.set_finished(
                "failure",
                _("Callback address error"),
                failure_type="http_callback",
            )
            return
        retries = int(conf.get("retries", 3))
        source_time = self.alarm_instance.get("source_time")
        data = {
            "alarm_def_id": self.alarm_instance.get("alarm_def_id"),
            "ip": self.alarm_instance.get("ip"),
            "source_type": self.alarm_instance.get("source_type"),
            "alarm_type": self.alarm_instance.get("alarm_type"),
            "origin_alarm": self.alarm_instance.get("origin_alarm"),
            "source_time": source_time.isoformat() if source_time else "",
            "cc_biz_id": self.alarm_instance.get("cc_biz_id"),
        }
        for i in range(retries):
            try:
                response = requests.post(url, json=data)
                if response.status_code / 100 == 2:
                    try:
                        res_content = response.json()
                    except BaseException:
                        # 非 json 格式只返回状态码
                        res_content = _("Return code (%(status_code)s)", status_code=response.status_code)

                    self.set_finished(
                        "success", _("Callback successful: %(content)s", content=res_content),
                    )
                    break
            except Exception as err:
                self.comment = str(err)
        else:
            self.set_finished(
                "failure",
                _("Callback request failed: %(comment)s", comment=self.comment),
                failure_type="http_callback",
            )
