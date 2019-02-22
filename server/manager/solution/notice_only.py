# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

from fta import settings
from fta.solution.base import BaseSolution
from fta.utils import logging, people, send, split_list
from fta.utils.context import Context
from fta.utils.i18n import _
from manager.solution.bk_component import VAR

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    通知或审批套餐

    :param conf["message"]: 通知内容
    :param conf["wechat"]: 发送微信通知
    :param conf["sms"]: 发送短信通知
    :param conf["im"]: 发送RTX通知
    :param conf["mail"]: 发送邮件通知
    :param conf["phone"]: 发送电话通知
    :param conf["extra_people"]: 额外通知人
    """

    WAIT_MARK = "wait"
    APPROVED_MARK = "approved"

    DUMMY_RESULT = {"result": {
        "result": "True",
        "message": _("Review content: Test approval")}}

    def get_verifier(self, config):
        # 获取默认通知人
        default_verifier = people.get_verifier(self.alarm_instance["id"])
        # 获取额外通知人
        extra_people = split_list(config.get('extra_people', ''))
        return list(default_verifier) + list(extra_people)

    def _get_node_title(self, node_idx):
        return self.get_solution(self.alarm_instance, node_idx)["title"]

    def _get_node_result(self, node_idx):
        solution_context_id = self.get_context_id(
            self.alarm_instance["id"], node_idx)
        return Context(solution_context_id).result

    def init_context(self):
        solution = json.loads(self.alarm_instance["snap_solution"])
        graph_json = self.convert_solution2graph(solution)
        next_node = graph_json[int(self.node_idx)][0].keys()
        pre_node = [node_idx for node_idx, node_json in enumerate(graph_json)
                    if str(self.node_idx) in map(str, node_json[0].keys())]
        next_node_title = map(unicode, map(self._get_node_title, next_node))
        pre_node_title = map(unicode, map(self._get_node_title, pre_node))
        pre_node_result = map(self._get_node_result, pre_node)
        context = Context(self.alarm_instance["id"])
        context.diy_solution_next = ",".join(next_node_title)
        context.diy_solution_pre = ",".join(pre_node_title)
        context.diy_solution_pre_result = ",".join(pre_node_result)
        # 如果通知是最后一个步骤，那么通知集成上一步节点的状态
        if not next_node:
            self.pre_result = self._get_result(pre_node_result)
        # 否则通知成功就成功
        else:
            self.pre_result = "success"

    def _get_result(self, pre_node_result):
        if "failure" in pre_node_result:
            return "failure"
        if "skipped" in pre_node_result:
            return "skipped"
        for result in pre_node_result:
            if result != "success":
                return result
        return "success"

    def run(self):
        # 非正式环境跳过
        if settings.SOLUTION_DUMMY is not False:
            return self.set_finished("success", _("Pseudo execution"))

        if not self.conf['message']:
            return self.set_finished(
                "failure", _("Notification is empty, notification failed"),
                failure_type="user_code_failure",
            )

        # 没有前后节点可能初始化失败
        try:
            self.init_context()
        except BaseException:
            self.pre_result = "success"

        config = VAR(self.alarm_instance).render_kwargs(self.conf)
        self.verifier = self.get_verifier(config)
        extend_message = config['message']

        # 发送通知
        if self.conf.get('wechat'):
            send.wechat(self.verifier, extend_message)
        if self.conf.get('sms'):
            send.sms(self.verifier, extend_message)
        if self.conf.get('im'):
            send.im(self.verifier, extend_message)
        if self.conf.get('email'):
            send.mail(self.verifier, extend_message, config['message'])
        if self.conf.get('phone'):
            message = extend_message.replace(u"【", "").replace(u"】", "")
            # 电话通知比较重要，失败的话认为套餐执行失败
            if send.phone(self.verifier, message) is False:
                return self.set_finished(
                    "failure", _("Failed to send telephone notification"),
                    failure_type="user_code_failure",
                )

        # 如果只是发送通知，则执行完毕，返回上一步节点的结果
        return self.set_finished(self.pre_result, _("Send notification successful"))
