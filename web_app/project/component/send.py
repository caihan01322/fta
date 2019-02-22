# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
此模块集合了所有信息方式的原始发送接口
"""
from django.utils.translation import ugettext as _

from common.log import logger
from fta_utils.component import SDKClient

# 信息签名
try:
    from fta.settings import SIGNATURE
except Exception:
    SIGNATURE = ""

__ALL__ = ['wechat', 'sms', 'mail', 'phone', 'raw_wechat']

BREAKS = "\n"

WECHAT_BLOCK = {
    "#": _(u"井号"),
    "&": _(u"and符")
}

# 组件调用 client
bk = SDKClient(is_backend=True)


def filter_wechat_message(message):
    """将一些无法发送的字符替换"""
    lines = []
    include_block = False
    for word, desc in WECHAT_BLOCK.items():
        if word in message:
            include_block = True
            message = message.replace(word, '\\%s' % ord(word))
            lines.append(_(u'将文本中[%s]替换为[\\%s]') % (desc, ord(word)))
    if include_block:
        lines.insert(0, _(u'%s【注】因微信接口限制:') % BREAKS)
    lines.insert(0, message)
    return BREAKS.join(lines)


def wechat(verifier, message):
    if not verifier:
        return
    verifier = check_verifier(verifier)
    message = filter_wechat_message(message)
    message += u'%s%s%s' % (BREAKS, BREAKS, SIGNATURE) if SIGNATURE else ""
    logger.info("send.wechat(%s): %s", verifier, message)

    result = bk.cmsi.send_weixin({
        "receiver__username": verifier,
        "data": {
            "heading": _(u"故障自愈通知"),
            "message": message
        }
    })
    if not result.get("result"):
        logger.warning(u"send wechat error %s %s", verifier, result)
    return result


def raw_wechat(verifier, message):
    """
    腾讯云只能通过ESB接口发送微信
    """
    return wechat(verifier, message)


def sms(verifier, message):
    if not verifier:
        return
    verifier = check_verifier(verifier)
    message += u'%s%s%s' % (BREAKS, BREAKS, SIGNATURE) if SIGNATURE else ""
    logger.info("send.sms(%s): %s", verifier, message)

    result = bk.cmsi.send_sms({
        "content": message,
        "receiver__username": verifier
    })
    if not result.get("result"):
        logger.warning(u"send sms error %s %s", verifier, result)
    return result


def mail(verifier, message, title=_(u'【自愈通知】邮件')):
    return True
    if not verifier:
        return
    verifier = check_verifier(verifier)
    title += SIGNATURE
    logger.info("send.mail(%s): %s", verifier, title)

    result = bk.cmsi.send_mail({
        "receiver__username": verifier,
        "title": title,
        "content": message
    })
    if not result.get("result"):
        logger.warning(u"send e-mail error %s %s", verifier, result)
    return result


def phone(verifier, message):
    '''
    @summary: 可自定义内容的自动语音通知
    @param users: 发送给的用户，以半角逗号间隔
    '''
    if not verifier:
        return
    verifier = check_verifier(verifier)
    logger.info("send.phone(%s): %s", verifier, message)

    result = bk.cmsi.noc_notice({
        "auto_read_message": message,
        "receiver__username": verifier,
    })
    if not result.get("result"):
        logger.warning(u"send phoen msg error %s %s", verifier, result)
    return result


def check_verifier(verifier):
    if isinstance(verifier, list) or isinstance(verifier, tuple):
        return ','.join(verifier)
    return verifier
