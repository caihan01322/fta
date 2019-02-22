# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta import constants, settings
from fta.solution.base import UNSET_RESULT, BaseSolution
from fta.utils import lock, logging, send, timeout
from fta.utils.continuation import WaitCallback
from fta.utils.i18n import _
from fta.utils.monitors import get_description_by_alarm_type
from project.utils import people

logger = logging.getLogger("solution")


def get_approve_callback_id(alarm_instance_id, node_idx):
    return "waiting_approve_%s_%s" % (alarm_instance_id, node_idx)


class Solution(BaseSolution):

    """
    等待审批套餐。
    需要用户通过界面手动确认发起回调请求来继续操作
    作为组合套餐中编号为 -1 的节点
    """

    DUMMY_RESULT = {"result": {
        "verifier": "admin", "approved": "True", "message": ""}}

    def run(self):
        if lock.redis_lock("wait_lock_%s%s" % (
                self.alarm_instance["cc_biz_id"],
                self.alarm_instance["alarm_type"])):
            self.send_notify()
        self.logger.info(_("Error defense, wait for approval"))

        # 状态重新标注为 waiting
        self.converged_status = lock.lock_alarm_instance(
            self.alarm_instance['event_id'], 'recovering', 'waiting')

        # 审批套餐是由 APP 发起审批的，由用户在 APP 发起回调
        fake_esb_id = get_approve_callback_id(
            self.alarm_instance["id"], self.node_idx)
        # 超时事件为剩余超时时间的一半
        wait_timeout = timeout.get_timeout_time(self.alarm_instance) / 2
        self.wait_esb_callback("receive_approve", fake_esb_id,
                               timeout=wait_timeout,
                               dummy_result=self.DUMMY_RESULT)

    def send_notify(self):
        alarm_instance = self.alarm_instance
        verifier = people.get_verifier(alarm_instance["id"])
        notify_message = [
            _("[Fault Auto-recovery] [To Be Approved])"),
            _("Business: %(cc_biz_name)s", cc_biz_name=alarm_instance["cc_biz_id"]),
            _("Alarm Type: %(alarm_type)s", alarm_type=get_description_by_alarm_type(
                alarm_instance['alarm_type'],
                cc_biz_id=alarm_instance['cc_biz_id'],
                default=alarm_instance['alarm_type'],
            )),
            _("Webpage: Please go to Fault Auto-recovery APP for approval or operation"),
        ]
        if hasattr(settings, "WECHAT_URL"):
            notify_message.append(
                u"微信：%swechat/todo" % settings.WECHAT_URL)
        send.wechat(verifier, constants.WECHAT_BREAKS.join(notify_message))

    def receive_approve(self, result):
        logger.info(
            "$%s approve_receive: %s",
            self.alarm_instance["id"], result)

        # 状态重新标注为 recovering
        self._mark_recovering()
        if result['approved'] == "True":
            approved = _("Pass")
        else:
            approved = _("Reject")
        approved_msg = u"[%s]" % (result["message"] or "")

        comment = _("[%(verifier)s]%(approved)s approved %(approved_msg)s",
                    verifier=result['verifier'], approved=approved, approved_msg=approved_msg)

        status = "success" if result["approved"] == "True" else "skipped"
        return self.set_finished(status, comment)

    def timeout_callback(self, esb_id_, func_, timeout_):
        logger.info("$%s &%s waiting timeout",
                    self.alarm_instance["id"], self.node_idx)

        if self.result == UNSET_RESULT:
            # 状态重新标注为 recovering
            self._mark_recovering()

            return self.set_finished(
                "skipped", _("[System] rejected the approval [timeout]"),
                failure_type="timeout",
            )
        else:
            raise WaitCallback("pass_timeout_callback")

    def _mark_recovering(self):
        """状态重新标注为 recovering"""
        try:
            self.converged_status = lock.lock_alarm_instance(
                self.alarm_instance["event_id"], "waiting", "recovering")
        except lock.LockError:
            pass
