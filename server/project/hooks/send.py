# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import base64

from project.utils.component import bk

from fta.utils.i18n import _

try:
    from fta.utils import logging
except BaseException:
    import logging

logger = logging.getLogger('utils')

# 信息签名
try:
    from fta.settings import SIGNATURE
except BaseException:
    SIGNATURE = ""
BREAKS = "\n"

__ALL__ = ['wechat', 'sms', 'mail', 'phone', 'im']


def wechat(verifier, message):
    """
        接收人需要在平台的个人中心里绑定微信
        所有接收人只要有一个接收失败, 结果就返回False
    """
    verifier = check_verifier(verifier)
    message_encoded = base64.b64encode(message.decode("utf-8"))
    logger.info("send.wechat(%s): %s", verifier, message)

    if not verifier:
        return

    ret = bk.cmsi.on_error_returns(False).send_weixin(
        receiver__username=verifier,
        data={
            "heading": _("Fault Auto-recovery notification"),
            "is_message_base64": True,
            "message": message_encoded
        }
    )

    if ret is False:
        logger.warning(_("Failed to send WeChat notification %s %s"), verifier, message)
    return ret


def sms(verifier, message):
    verifier = check_verifier(verifier)
    message += u'%s%s%s' % (BREAKS, BREAKS, SIGNATURE) if SIGNATURE else ""
    # 替换符号
    new_message1 = message.replace(u"【", " ").replace(u"】", " ")
    # 添加短信模板
    new_message = _(
        "[Fault Auto-recovery] %s%s Please ignore this message if you are not a subscriber.") % (new_message1, BREAKS)
    message_encoded = base64.b64encode(new_message.decode("utf-8"))
    logger.info(message_encoded)
    logger.info("send.sms(%s): %s", verifier, message)

    if not verifier:
        return

    ret = bk.cmsi.on_error_returns(False).send_sms(
        receiver__username=verifier, content=message_encoded,
        is_content_base64=True,
    )

    if ret is False:
        logger.warning(_("Failed to send SMS notification %s %s"), verifier, message)
    return ret


def mail(verifier, message, title=_("[Fault Auto-recovery] Email notification")):
    verifier = check_verifier(verifier)
    message_encoded = base64.b64encode(message.decode("utf-8"))
    title += SIGNATURE
    logger.info("send.mail(%s): %s", verifier, title)

    if not verifier:
        return

    ret = bk.cmsi.on_error_returns(False).send_mail(
        title=title, content=message_encoded,
        receiver__username=verifier, is_content_base64=True,
    )

    if ret is False:
        logger.warning(_("Failed to send email notification %s %s"), verifier, message)
    return ret


def mail_app_user(verifier, message, title=_("[Fault Auto-recovery] Email notification")):
    return mail(verifier, message, title)


def phone(verifier, message):
    verifier = check_verifier(verifier)
    logger.info("send.phone(%s): %s", verifier, message)

    if not verifier:
        return

    ret = bk.cmsi.on_error_returns(False).noc_notice(
        auto_read_message=message,
        receiver__username=verifier,
    )

    if ret is False:
        logger.warning(_("Failed to send telephone notification %s %s"), verifier, message)
    return ret


def im(verifier, message, title=_("[BlueKing Monitoring System] IM notification")):
    verifier = check_verifier(verifier)
    title += SIGNATURE
    logger.info("send.im(%s): %s", verifier, title)

    if not verifier:
        return


def check_verifier(verifiers):
    if not isinstance(verifiers, (list, tuple)):
        verifiers = verifiers.split(',')
    verifiers = filter(lambda x: x != '100', verifiers)
    return ','.join(verifiers)
