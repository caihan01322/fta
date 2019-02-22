# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
与人相关的逻辑，比如获取告警负责人或相关责任人
相关责任人的逻辑一定要谨慎，因为如果不相关就会造成骚扰和混乱（特别是有领导的情况）
"""

import json

from fta import settings
from fta.utils import hooks, logging, split_list
from fta.utils.alarm_instance import get_alarm_instance

logger = logging.getLogger("root")


# @func_cache()  # for debug
def get_verifier(alarm_instance_id):
    """
    get verifier by alarm_instance_id
    will return settings.VERIFIER if you set in settings

    :param alarm_instance_id: alarm_instance"s id
    :return verifier_list: ["", ]
    """

    # 运行环境指定了负责人
    if hasattr(settings, "VERIFIER"):
        logger.info("$%s verifier by VERIFIER: %s",
                    alarm_instance_id, settings.VERIFIER)
        return settings.VERIFIER

    alarm_instance = get_alarm_instance(instance_id=alarm_instance_id)
    alarm_def = json.loads(alarm_instance["snap_alarm_def"])
    notify_conf = json.loads(alarm_def.get("notify", "{}") or "{}")

    if hasattr(settings, "VERIFIER_BLACK_LIST"):
        # 黑名单业务，不通知
        cc_biz_id = alarm_instance["cc_biz_id"]
        if int(cc_biz_id) in settings.VERIFIER_BLACK_LIST:
            logger.info("%s %s in black_list", alarm_instance_id, cc_biz_id)
            return []

    # # 只获取 alarm_def 额外负责人
    # if notify_conf.get("only_to_extra"):
    #     logger.info("$%s verifier: only_to_extra", alarm_instance_id)
    #     return split_list(alarm_def.get("responsible", ""))
    #
    # # 只获取 IP 主机负责人
    # if notify_conf.get("only_to_host"):
    #     logger.info("$%s verifier: only_to_host", alarm_instance_id)
    #     return get_ip_responsible(alarm_instance)
    #
    # # 只获取 Role 负责人
    # if notify_conf.get("only_to_role"):
    #     logger.info("$%s verifier: only_to_role", alarm_instance_id)
    #     return get_role_responsible(alarm_instance)

    verifier_list = []
    if notify_conf.get("to_role"):
        if "role_list" in notify_conf:
            if notify_conf.get("role_list"):
                # 获取角色责任人
                verifier_list = _append_to_end(
                    verifier_list, get_role_responsible(alarm_instance),
                )
                logger.info("$%s verifier_role: %s",
                            alarm_instance_id, verifier_list)
        else:
            # 获取业务负责人
            verifier_list = _append_to_end(
                verifier_list, get_biz_responsible(alarm_instance["cc_biz_id"]),
            )
            logger.info("$%s verifier_alarm_def: %s",
                        alarm_instance_id, verifier_list)

    if notify_conf.get("to_extra"):
        # 加上 alarm_def 额外通知人
        extra_responsibles = split_list(alarm_def.get("responsible", ""))
        verifier_list = _append_to_end(verifier_list, extra_responsibles)

    if notify_conf.get("to_host"):
        # 加上主机责任人
        host_operator = get_ip_responsible(alarm_instance)
        verifier_list = _append_to_end(host_operator, verifier_list)

    logger.info("$%s verifier: %s", alarm_instance_id, verifier_list)
    return verifier_list


def _append_to_end(raw_list, append_list):
    new_list = [item for item in raw_list if item]
    new_list.extend([item for item in append_list
                     if item and item not in raw_list])
    return new_list


hook = hooks.HookManager("people")
get_biz_name = hook.get("get_biz_name", lambda x: x)
get_ip_responsible = hook.get("get_ip_responsible", lambda x: "")
get_biz_responsible = hook.get("get_biz_responsible", lambda x: "")
get_role_responsible = hook.get("get_role_responsible", lambda x: "")
