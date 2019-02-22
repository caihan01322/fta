# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
import urllib

import requests

from common.log import logger
from fta_solutions_app.models import Conf

rpool = requests.Session()


def access_token():
    """获取access_token
    """
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    corpid = Conf.get('WECHAT_CORPID')
    corpsecret = Conf.get('WECHAT_SECRET')
    params = {'corpid': corpid, 'corpsecret': corpsecret}
    resp = rpool.get(url, params=params, verify=False, timeout=5)
    logger.info('access_token: %s, %s' % (resp.request.url, resp.content))
    result = resp.json()
    return result['access_token']


def send_message(touser, content):
    """发送文本消息
    """

    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
    agentid = Conf.get('WECHAT_AGENT_ID')
    data = {
        "touser": touser,
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": content
        },
        "safe": 0
    }
    params = {'access_token': access_token()}
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    resp = rpool.post(url, params=params, data=data, verify=False, timeout=5)
    logger.info('send_message: %s, %s' % (resp.request.body, resp.content))
    result = resp.json()
    return result


def get_user_info(code):
    """获取用户信息
    """
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
    params = {'access_token': access_token(), 'code': code}
    resp = rpool.get(url, params=params, verify=False, timeout=5)
    logger.info('get_user_info: %s, %s' % (resp.request.url, resp.content))
    result = resp.json()
    return result


def get_oauth_redirect_url(redirect_uri, state):
    """获取oauth访问链接
    """
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    corpid = Conf.get('WECHAT_CORPID')
    params = {
        'appid': corpid,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'snsapi_base',
        'state': state
    }
    params = urllib.urlencode(params)
    redirect_uri = '%s?%s#wechat_redirect' % (url, params)
    return redirect_uri
