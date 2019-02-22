# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import socket
import subprocess

from fta.solution.base import BaseSolution
from fta.utils import logging
from fta.utils.i18n import _

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    检查主机存活，ping 或者 socket 端口检查

    :param conf["check_port"]: default False,
                               如果为真，则检查36000端口是否能连通
                               否则在本机进行ping 检测
    """

    def run(self):

        if self.conf.get('check_port'):
            self.success_count = self.failure_count = 0
            return self.check_port(self.alarm_instance["ip"])

        check_result = check_ping(self.alarm_instance["ip"])
        if check_result:
            return self.set_finished(
                "failure", _("Server PING reachable"), failure_type="false_alarm",
            )
        else:
            return self.set_finished("success", _("Server PING unreachable"))

    def check_port(self, port=36000):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((self.alarm_instance["ip"], port))
        if result == 0:
            self.success_count = self.success_count + 1
        else:
            self.failure_count = self.failure_count + 1
        if self.success_count >= 5:
            return self.set_finished(
                "failure", _("Server port accessible"), failure_type="false_alarm",
            )
        if self.failure_count >= 15:
            return self.set_finished("success", _("Server port inaccessible"))
        return self.wait_callback("check_port", delta_seconds=20)


def check_ping(ip, threshold=1000):
    """
    从自愈服务器运行ping命令
    :params： ip 内网IP
    :params： threshold 超时限制
    :return：是否ping通
    """
    r = subprocess.Popen(
        ['ping', '-c 1', '-W 1', ip],
        stdout=subprocess.PIPE)
    code = r.wait()
    logger.info('%s ping code: %s', ip, code)
    if code == 0:
        for line in r.stdout.readlines():
            if line.find('time=') != -1:
                try:
                    latency = float(line.split()[-2].split('=')[1])
                    logger.info('%s latency: %s', ip, latency)
                    return latency < threshold
                except BaseException:
                    logger.exception('%s parse result failed', ip)
                    return True
        return True
    else:
        return False
