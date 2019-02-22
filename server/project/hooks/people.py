# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from project.utils import get_plat_info
from project.utils.cc import CCBiz
from project.utils.query_cc import get_cc_biz_attr, get_cc_biz_responsible, get_cc_ip_responsible

from fta import settings
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppBizconf
from fta.utils import logging, split_list
from fta.utils.decorator import func_cache, try_exception

logger = logging.getLogger("utils")


@try_exception(exception_return=[])
def get_ip_responsible(alarm_instance):
    # 运行环境指定了负责人
    if hasattr(settings, "VERIFIER"):
        logger.info("$%s ip_resp by VERIFIER: %s", alarm_instance["id"], settings.VERIFIER)
        return settings.VERIFIER

    plat_info = get_plat_info(alarm_instance)
    logger.info('get_ip_responsible log plat_id:%s, company_id:%s,', plat_info["plat_id"], plat_info["company_id"])
    return get_cc_ip_responsible(plat_info["plat_id"], plat_info["company_id"], alarm_instance["ip"])


@try_exception(exception_return=[])
def get_role_responsible(alarm_instance):
    """通过自愈 DB 获取负责人，没有则通过 CC 获取"""
    # 运行环境指定了负责人
    if hasattr(settings, 'VERIFIER'):
        logger.info("$%s rele_resp by VERIFIER: %s", alarm_instance["id"], settings.VERIFIER)
        return settings.VERIFIER

    alarm_def = json.loads(alarm_instance['snap_alarm_def'])
    notify_conf = json.loads(alarm_def.get('notify') or '{}')
    cc_biz_id = alarm_instance["cc_biz_id"]
    role_responsible = []
    role_list = notify_conf.get("role_list") or []
    for role in role_list:
        try:
            users = CCBiz(cc_biz_id).get(role).split(";")
        except Exception as e:
            logger.exception("get role error: %s", e)
            continue
        for user in users:
            if user not in role_list:
                role_responsible.append(user)
    logger.info(
        "$%s role_responsible: %s %s", alarm_instance["id"], json.dumps(role_list), json.dumps(role_responsible)
    )
    return role_responsible


@try_exception(exception_return=[])
@func_cache()
def get_biz_responsible(cc_biz_id):
    """通过自愈 DB 获取负责人，没有则通过 CC 获取"""
    # 运行环境指定了负责人
    if hasattr(settings, 'VERIFIER'):
        logger.info("biz_resp by VERIFIER: %s %s", cc_biz_id, settings.VERIFIER)
        return settings.VERIFIER
    responsibles = get_fta_biz_responsible(cc_biz_id) or get_cc_biz_responsible(cc_biz_id)
    return split_list(responsibles)


def get_fta_biz_responsible(cc_biz_id):
    # 运行环境指定了负责人
    if hasattr(settings, 'VERIFIER'):
        return settings.VERIFIER
    biz_conf = session.query(FtaSolutionsAppBizconf).filter_by(cc_biz_id=cc_biz_id).first()
    if biz_conf:
        return biz_conf.responsible
    return None


def get_biz_name(cc_biz_id):
    return get_cc_biz_attr(cc_biz_id, "ApplicationName")
