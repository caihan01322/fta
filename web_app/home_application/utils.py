# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import requests
from django.conf import settings

from common.log import logger
from fta_utils.component import SDKClient
from permission import roles


def serialize_healthz():
    healthz = {}
    # 检查自愈后台健康度
    try:
        res = requests.get(settings.FTA_STATUS_URL, timeout=16, verify=False).json()
        res.pop("data")
        res.pop("code")
    except Exception as e:
        logger.exception(u"healthz api error:%s" % e)
        healthz["fta_backend"] = {
            "result": False,
            "message": str(e)
        }
    else:
        healthz["fta_backend"] = res

    # 如果有登录态，检查 APP 依赖的接口
    cc_data = {}
    try:
        bk = SDKClient(is_backend=True)
        # 检查cc依赖
        resp = bk.cc.get_app_by_user_role(user_role=','.join(roles.ALL_ROLES))
        if resp.get("result", False):
            cc_data["get_app_by_user_role"] = True
        else:
            cc_data["get_app_by_user_role"] = resp.get("message")

        data = bk.cc.get_app_agent_status(app_id=1)
        if data.get("result", False):
            cc_data["get_app_agent_status"] = True
        else:
            cc_data["get_app_agent_status"] = data.get("message")
    except Exception as e:
        logger.exception(u"healthz api error:%s" % e)
    if cc_data:
        healthz["fta_app"] = cc_data
    return healthz


def get_false_num(d, num=0):
    for k, v in d.iteritems():
        if isinstance(v, dict):
            num = get_false_num(v, num)
        elif v is False:
            num += 1
    return num


def get_unhealth_num():
    healthz = serialize_healthz()
    unhealth_num = get_false_num(healthz)
    return unhealth_num
