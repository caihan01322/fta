# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""weixin auth utility
"""
import random
import string
import time

from common.log import logger
from fta_solutions_app.models import Conf
from fta_utils.component import SDKClient
from permission import roles


def set_state(request, length=32):
    """获取state，并存储到session中
    """
    state = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    request.session['REQ_STATE'] = state
    request.session['REQ_STATE_TIMESTAMP'] = time.time()
    return state


def valid_state(request, state, expires_in=60):
    """验证state, 只允许60秒内返回请求
    """
    try:
        raw_state = request.session.get('REQ_STATE')
        raw_timestamp = request.session.get('REQ_STATE_TIMESTAMP')
        # 验证state
        if not raw_state or raw_state != state:
            return False
        # 验证时间戳
        if not raw_timestamp or time.time() - raw_timestamp > expires_in:
            return False
        # 验证成功后清空session
        request.session['REQ_STATE'] = None
        request.session['REQ_STATE_TIMESTAMP'] = None
        return True
    except Exception as error:
        logger.error('valid_state error: %s' % error)
        return False


def get_user_bizs(username):
    """
    获取用户的业务列表
    """
    bk = SDKClient(is_backend=True)
    result = bk.cc.get_app_by_user_role({
        'user_role': ','.join(roles.ALL_ROLES),
        'username': username,
        'uin': username
    })
    logger.info('wechat get_user_bizs username:%s, result:%s' % (username, result))
    if not result['result']:
        return []

    data = result['data']
    cc_biz_ids = []
    if data:
        # 按照开发商过滤
        for key, val in data.iteritems():
            if val:
                for item in val:
                    app_id = item.get('ApplicationID')
                    if app_id and app_id not in cc_biz_ids:
                        cc_biz_ids.append(str(app_id))
    return cc_biz_ids


def is_wehcat_super_approver(username):
    """
    是否为微信审批的管理员，即可以收到并审批所有的微信审批信息
    """
    super_approver = Conf.get('WECHAT_SUPER_APPROVER')
    super_approver_list = super_approver.split(',') if super_approver else []
    return username in super_approver_list


def is_app_in_user_bizs(username, cc_biz_id):
    """
    判断用户是否拥有该业务的权限
    """
    # 超级管理员拥有所有业务的权限
    if is_wehcat_super_approver(username):
        return True

    user_bizs = get_user_bizs(username)
    return str(cc_biz_id) in user_bizs
