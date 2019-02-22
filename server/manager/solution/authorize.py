# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta import constants, settings
from fta.solution.base import BaseSolution
from fta.utils import logging, send
from fta.utils.i18n import _
from project.utils import dba_alarm
from project.utils.cc import CC

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    自动授权套餐

    对于 DBA 告警，通过 DBA 的接口来判断是否对 IP 自动授权
    对于其他业务，就直接返回授权状态

    :param conf["DBA"]: default False, 为真则为 DBA 告警的标识
    """

    def run(self):
        if self.conf.get("DBA"):
            result, comment = dba_handler(self.alarm_instance["ip"])
        else:
            result, comment = "authorized", _("Auto authorization")
        logger.info(
            "$%s &%s authorize %s: %s",
            self.alarm_instance["id"], self.node_idx,
            self.alarm_instance["ip"], result)
        return self.set_finished(result, comment)


def dba_handler(ip):
    """
    """
    result = comment = dba_alarm.mach_priv(ip)
    message = [
        _("[Fault Auto-recovery] Auto authorization"),
        u"IP: %s" % ip,
        _("Alarm type: Hard disk alarm (redundant)"),
        _("Result: %(result)s", result=result),
    ]
    if settings.ENV == "PRODUCT":
        default_receiver = "hunterzhang,yuanyuanmu,"
        receive = default_receiver + CC(ip).get("Operator")
    else:
        receive = ""  # for test
    send.wechat(receive, constants.WECHAT_BREAKS.join(message))
    return result, comment
