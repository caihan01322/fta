# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from fta.storage.mysql import session
from fta.storage.tables import WechatApprove
from fta.utils import logging, send

logger = logging.getLogger("solution")


# import json
#
# import requests
# from project.utils.component import bk
# from fta import settings
# from fta.utils import logging
# from fta.utils.conf import Conf
# from fta.utils import logging, people, send, split_list, timeout
# rpool = requests.Session()
#
# def wechat_approve(obj_id, verifier, message, callback_url=None):
#     """微信审批
#     params: obj_id 唯一ID，{alarm_instance_id}_{node_idx} 回调使用的intance_id
#     params: verifier 审批人，多个以逗号分隔
#     params: message 发送的审批信息
#     params: callback_url, 不填默认为fta回调地址
#     """
#     if settings.ENV == "PRODUCT":
#         url = "%swechat/create_approve/" % settings.APP_URL_PROD
#     else:
#         url = '%swechat/create_approve/' % settings.APP_URL_TEST
#
#     data = {
#         'obj_id': obj_id,
#         'verifier': verifier,
#         'message': message,
#         'callback_url': callback_url,
#         'app_code': bk.app_code,
#         'app_secret': bk.app_secret
#     }
#     headers = {'TOKEN': Conf.get('WECHAT_API_TOKEN', '')}
#     data = json.dumps(data, ensure_ascii=False).encode('utf-8')
#     resp = rpool.post(url, data=data, verify=False, timeout=5, headers=headers)
#     logger.info('wechat_approve resp: %s' % resp.content)
#     return resp


def wechat_approve(obj_id, verifier, message, callback_url=None):
    """微信审批
    params: obj_id 唯一ID，{alarm_instance_id}_{node_idx} 回调使用的intance_id
    params: verifier 审批人，多个以逗号分隔
    params: message 发送的审批信息
    params: callback_url, 不填默认为fta回调地址
    """
    create_approve(verifier, message, obj_id, callback_url)


def create_approve(verifier, message, obj_id, callback_url):
    """创建审批单API
    包含：自愈故障替换API
    """
    try:
        approve = WechatApprove(message=message, obj_id=obj_id, approve_users=verifier, callback_url=callback_url)
        session.add(approve)
        session.flush()

        # 发送微信消息
        send_message(verifier, obj_id, message)
        logger.info('%s create wechat_approve success approve_id: %s' % (obj_id, approve.id))
    except Exception as e:
        logger.info('%s create wechat_approve failed reason: %s' % (obj_id, e))


def send_message(verifier, obj_id, message):
    """发送审批单
    """
    content = u"【故障自愈】即将执行 {message},请审核！\n同意请回复: TY {obj_id}\n驳回请回复: BH {obj_id}"
    data = {'message': message, 'obj_id': obj_id}
    return send.wechat(verifier, content.format(**data))
