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
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppApproveCallback
from fta.utils import logging, people, send, split_list, timeout
from fta.utils.context import Context
from fta.utils.i18n import _, lazy_gettext
from manager.solution.bk_component import VAR
from project.utils.wechat import wechat_approve

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
    :param conf["approve"]: 发送审批通知
    :param conf["extra_people"]: 额外通知人
    """

    WAIT_MARK = "wait"
    APPROVED_MARK = "approved"

    DUMMY_RESULT = {
        "result": {
            "result": "True",
            "message": _("Review content: Test approval")
        }
    }

    # 消息中需要翻译的词
    MESSAGE_KEY_WORLDS = [
        u"【故障自愈】内存使用率TOP10列表",
        u"【故障自愈】CPU使用率TOP10列表",
        u"业务",
        u"模块",
        u"主机",
        u"空闲机池",
        u"资源池",
        u"空闲机",
        u"故障机"
    ]

    def __init__(self, alarm_instance, node_idx, run_times=0):
        super(Solution, self).__init__(alarm_instance, node_idx, run_times)
        self.pre_result = ''
        self.verifier = ''

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

        if self.conf.get('approve'):
            extend_message = u"%s %s" % (
                config['message'],
                _("Please log in to o.qcloud.com -- Personal Center -- My Approval to execute approval operation"))
        else:
            extend_message = config['message']

        for keyword in self.MESSAGE_KEY_WORLDS:
            s = extend_message.find(keyword)
            if s >= 0:
                new_msg = extend_message[:s] + lazy_gettext(keyword) + extend_message[s + len(keyword):]
                extend_message = new_msg

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

        # 发送审批通知
        if self.conf.get('wechat_approve'):
            try:
                wechat_approve(
                    obj_id=get_obj_id(self.alarm_instance["id"], self.node_idx),
                    verifier=",".join(self.verifier),
                    message=config["message"],
                )
                self.wait_timeout = timeout.get_timeout_time(self.alarm_instance) / 2
            except Exception as e:
                logger.warning("$%s wechat_approve error:%s", self.alarm_instance["id"], e)
                return self.set_finished("failure", _("Failed to send approval"), failure_type="user_code_failure", )

        # 如果只是发送通知，则执行完毕，返回上一步节点的结果
        if not self.conf.get('wechat_approve'):
            return self.set_finished(self.pre_result, _("Send notification successful"))

        return self.wait_approve_callback()

    def wait_approve_callback(self):
        """获取审批结果"""
        if self.wait_timeout <= 0:
            # 审批超时
            return self.set_finished("failure", _("Approval timeout"), failure_type="timeout", )

        self.wait_callback_time = self.wait_callback_time or 12
        self.wait_callback_time = min(int(self.wait_callback_time * 1.5), 60)
        self.wait_timeout -= self.wait_callback_time

        # APP要做审批去重
        status, result = get_approve_result(self.alarm_instance['id'], self.node_idx)
        if status is not None:
            logger.info(result)

            status = "success" if result['approval'] else "failure"
            return self.set_finished(status, result['reason'])
        else:
            self.wait_callback("wait_approve_callback", delta_seconds=int(self.wait_callback_time))


def get_obj_id(alarm_id, node_idx):
    return "%s_%s" % (alarm_id, node_idx)


def get_callback_url(alarm_id, node_idx):
    return settings.APPROVE_CALLBACK_URL % (alarm_id, node_idx)


def get_approve_result(alarm_id, node_idx):
    approve_list = session.query(FtaSolutionsAppApproveCallback).filter_by(alarm_id=alarm_id, node_idx=node_idx)
    status = None  # 默认状态为未审批
    result = {'obj_id': None, 'approval': None, 'reason': None}
    for a in approve_list:
        status = a.approval
        result = {'obj_id': a.obj_id, 'approval': a.approval, 'reason': a.reason}
        break
    return status, result
