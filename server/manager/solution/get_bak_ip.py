# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

from fta import constants, settings
from fta.solution.base import BaseSolution
from fta.utils import logging, timeout
from fta.utils.context import Context
from fta.utils.i18n import _
from manager.solution.notice import get_approve_result, get_obj_id
from manager.utils.query_cc import query_match_machine
from project.utils import people
from project.utils.query_cc import get_agent_abnor_list, get_host_info
from project.utils.wechat import wechat_approve

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    获取 IP 备机

    :param conf["OuterIPNum"]: 外网 IP 个数相同
    :param conf["auto_replace"]: 自动选取最新上架的机器
    :param conf[attr_name]: CC 的主机属性
    """

    DUMMY_RESULT = {"result": {
        "result": "True",
        "message": _("Review comment: 2")}}

    MATCH_ATTR = [
        "region", "device_class", "os_name"
    ]

    WECHAT_MESSAGE = [
        _("[Fault Auto-recovery] [Obtain standby machine solution]"),
        _("Machine %(fault_ip)s malfunctioned"),
        _("Screening conditions:"),
        u"%(match_dict)s",
        _("Matched idle machine:"),
        u"%(class_matched)s",
        # u"请回复",
        # u"TY XXXX 序号",
        # u"来选择备机IP",
    ]

    def get_match_dict(self):
        """生成筛选条件"""
        logger.info(
            "$%s get_bak_ip_log conf: %s",
            self.alarm_instance["id"], json.dumps(self.conf))

        # 根据故障机的 CC 信息及配置生成筛选条件
        match_dict = {
            'set_name': self.conf['set_name'],
            'module_name': self.conf['module_name'],
            'agent_status': self.conf.get('agent_status'),
            'bk_os_type': self.conf.get('bk_os_type', ''),
            'bk_state_name': self.conf.get('bk_state_name', ''),
            'bk_province_name': self.conf.get('bk_province_name', '')
        }

        for attr in self.MATCH_ATTR:
            if self.conf.get(attr) == 'on':
                match_dict[attr] = self.conf["%s_value" % attr]

        # module  名称未传则默认为空闲机
        if not self.conf.get("module_name"):
            match_dict["module_name"] = u"空闲机"

        logger.info(
            "$%s get_bak_ip_log match_dict: %s",
            self.alarm_instance["id"], json.dumps(match_dict))

        return match_dict

    def get_match_machine(self, match_dict):
        """获取匹配的机器"""
        # 调用cc api : get_hosts_by_property(根据 set 属性查询主机)
        app_id = self.alarm_instance["cc_biz_id"]
        machines = query_match_machine(app_id, match_dict)
        # kwargs = {
        #     "app_id": app_id,
        #     "set_name": match_dict.get('set_name', ''),
        #     "region": match_dict.get('region', ''),
        #     "device_class": match_dict.get('device_class', ''),
        #     "module_name": match_dict.get('module_name', ''),
        #     "os_name": match_dict.get('os_name', '')
        # }
        # machines = bk.cc.get_hosts_by_property(**kwargs)

        agent_status = match_dict.get('agent_status')
        #  只过滤已安装 agent 的机器
        if agent_status == 'on':
            agent_abnor_list = get_agent_abnor_list(app_id)
            machines_list = []
            logger.info('get_bak_ip_log machines:%s' % machines)
            logger.info('get_bak_ip_log agent_abnor_list:%s' % agent_abnor_list)

            for m in machines:
                m_str = '%s_%s_%s' % (m['InnerIP'], m['CompanyID'], m['Source'])
                if m_str in agent_abnor_list:
                    machines_list.append(m)
        else:
            machines_list = machines

        machines_set = []
        ip_set = set()
        for machine in machines_list:
            # 根据内网 IP 去重
            if machine["InnerIP"] in ip_set:
                continue
            ip_set.add(machine["InnerIP"])
            machines_set.append(machine)

        sorted_machines = sorted(
            machines_set,
            key=lambda i: i["HostID"],
            reverse=True)
        # TO CHANGE 只获取一台备机
        sorted_machines = [sorted_machines[0]] if sorted_machines else []

        logger.info(
            "$%s get_bak_ip_log match_machine: %s get %s",
            self.alarm_instance["id"], json.dumps(match_dict), sorted_machines)

        return sorted_machines

    def filter_outer_ip(self, match_machines, match_dict, machine_info):
        # 判断 CC 外网 IP 数量
        match_machines = [
            machine for machine in match_machines
            if len(machine["OuterIP"].split(',')) ==
            len(machine_info["OuterIP"])]
        match_dict[_("Outer IP Numbers")] = _("Equality")

    def get_message(self, spare_machines, match_dict):
        """生成微信消息供选择使用哪个故障机替换"""
        message = constants.WECHAT_BREAKS.join(self.WECHAT_MESSAGE) % {
            "fault_ip": self.alarm_instance["ip"],
            "match_dict": "\n".join([
                "%s:%s" % (k, v) for k, v in match_dict.items()]),
            "class_matched": self._render_machine(spare_machines),
        }
        logger.info("$%s get_bak_ip_log: %s", self.alarm_instance["id"], message)
        return message

    def _render_machine(self, machines):
        ret = []
        topo_set = self.alarm_instance.get("cc_topo_set")
        recomend_machines = [m for m in machines if m.get("SetID") == topo_set]
        other_machines = [m for m in machines if m.get("SetID") != topo_set]
        machines = recomend_machines + other_machines
        for index, machine in enumerate(machines):
            plat_id = machine["Source"]
            company_id = machine["CompanyID"]
            ip = machine["InnerIP"]
            host_info = get_host_info(plat_id, company_id, ip)
            message = _("%(index)s. %(inner_ip)s(Set:%(set)s, Module:%(module)s)",
                        index=index + 1,
                        inner_ip=machine["InnerIP"],
                        set=host_info.get("SetName", '-'),
                        module=host_info.get("ModuleName", '-'))
            ret.append(message)
        return "\n".join(ret)

    def run(self):

        # 查询故障机属性，暂不加该功能
        # try:
        #     machine_info = CC(self.alarm_instance["ip"])\
        #         .values(*self.MATCH_ATTR)[self.alarm_instance["ip"]]
        # except Exception, e:
        #     logger.warning(
        #         "$%s get_bak_ip_log get cc_info error: %s", self.alarm_instance["ip"], e)
        #     return self.set_finished("failure", u"获取故障机CC信息失败")

        # 生成筛选条件
        match_dict = self.get_match_dict()

        # 根据条件在 CC 查找主机
        match_machines = self.get_match_machine(match_dict)

        if not match_machines:
            return self.set_finished(
                "failure", _("No idle machines meeting the requirements"),
                failure_type="user_code_failure",
            )

        self.match_dict = match_dict
        self.match_machines = match_machines
        if self.conf.get("auto_replace"):
            # 不需要人工审核,自动选取最新的第一台机器
            return self.set_ip_bak(1)
        else:
            return self.send_approve()

    def send_approve(self):
        self.verifier = people.get_verifier(self.alarm_instance["id"])
        message = self.get_message(self.match_machines, self.match_dict)
        if settings.SOLUTION_DUMMY is not False:
            # ==================================
            # 为了在测试环境下测试组件回调功能，
            # 在自愈业务[fta](727)下，审批套餐调用真实组件
            if str(self.alarm_instance["cc_biz_id"]) == "727":
                fake_esb_id = "test_approve_%s_%s" % (
                    self.alarm_instance["id"], self.node_idx)
                return self.wait_esb_callback(
                    "get_callback", fake_esb_id, timeout=60 * 10,
                    dummy_result=self.DUMMY_RESULT)
            # ==================================
        else:
            try:
                wechat_approve(
                    obj_id=get_obj_id(
                        self.alarm_instance["id"], self.node_idx),
                    verifier=",".join(self.verifier),
                    message=message,
                )
                self.wait_timeout = timeout.get_timeout_time(
                    self.alarm_instance) / 2
                return self.wait_approve_callback()
            except Exception as e:
                logger.warning(
                    "$%s wechat_approve error:%s", self.alarm_instance["id"], e)
                return self.set_finished(
                    "failure", _("Failed to send approval"),
                    failure_type="user_code_failure",
                )

        #     dummy = settings.WCB_DUMMY
        #     esb_id = bk.smcs.wechat_approve__execute(
        #         app_name=u"故障自愈",
        #         operator=self.verifier[0],
        #         verifier=",".join(self.verifier),
        #         message=message)
        # return self.wait_esb_callback("get_callback", esb_id,
        #                               dummy=dummy,
        #                               dummy_result=self.DUMMY_RESULT)

    def wait_approve_callback(self):
        """获取审批结果"""
        if self.wait_timeout <= 0:
            # 审批超时
            return self.set_finished(
                "failure", _("Approval timeout"), failure_type="timeout",
            )

        self.wait_callback_time = self.wait_callback_time or 12
        self.wait_callback_time = min(int(self.wait_callback_time * 1.5), 60)
        self.wait_timeout -= self.wait_callback_time

        # APP要做审批去重
        status, result = get_approve_result(
            self.alarm_instance['id'], self.node_idx)
        if status is not None:
            logger.info(result)
            if result['approval']:
                return self.set_ip_bak(result['reason'])
            else:
                return self.set_finished(status, result['reason'])
        else:
            self.wait_callback("wait_approve_callback",
                               delta_seconds=int(self.wait_callback_time))

    # def get_callback(self, result):
    #     logger.info(
    #         "$%s get_ip_bak_callback: %s",
    #         self.alarm_instance["id"], result)
    #     approved, result = get_approve_result(result)
    #     if not approved:
    #         return self.set_finished("failure", result['reason'])
    #     elif not result['reason'].isdigit():
    #         send.wechat(self.verifier, u"无效的回复格式，请重新审批。")
    #         return self.send_approve()
    #     else:
    #         return self.set_ip_bak(approved_comment)

    def set_ip_bak(self, index):
        # TO CHANGE index 默认为1
        index = 1
        aim_machine = self.match_machines[int(index) - 1]
        context = Context(self.alarm_instance["id"])
        context.ip_bak = aim_machine["InnerIP"]
        return self.set_finished("success", _(
            "Standby machine acquisition successful %(ip_bak)s", ip_bak=context.ip_bak))
