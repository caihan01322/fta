# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import requests

from fta import settings
from fta.solution.base import BaseSolution
from fta.utils import logging
from fta.utils.i18n import _
from manager.solution.bk_component import VAR

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    HTTP 请求套餐

    :param conf["url"]: 请求的 URL
    :param conf["post"]: 是否为 POST 请求
    :param conf["post_params"]: POST 参数
    :param conf["verifier_return_json"]: 验证返回的 JSON 数据
    """

    def run(self):

        conf = VAR(self.alarm_instance).render_kwargs(self.conf)

        # 非正式环境跳过
        if settings.SOLUTION_DUMMY is not False:
            return self.set_finished("success", _("Pseudo execution"))

        try:
            if conf.get("post"):
                r = requests.post(conf["url"],
                                  data=conf.get("post_params", ""))
            else:
                r = requests.get(conf["url"])
            r.raise_for_status()
            if conf.get("verifier_return_json"):
                try:
                    result = r.json()
                except BaseException:
                    raise Exception(_("Data returned is not in JSON format"))
                if result.get("result") not in ["True", "true", True]:
                    if result.get("message"):
                        raise Exception(result.get("message"))
                    raise Exception(r.text)
            return self.set_finished("success", r.text[:200])  # 最多允许200个字符
        except Exception as e:
            msg = _("Request error: %(error)s", error=e)
            logger.warning("$%s &%s %s",
                           self.alarm_instance["id"], self.node_idx, msg)
            return self.set_finished(
                "failure", msg, failure_type="user_code_failure",
            )
