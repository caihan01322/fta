# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
此模块负责自愈系统本身的通知，包括对开发和对用户的异常通知和知会等
"""

import inspect
import random
import sys
import traceback

from fta import constants, settings
from fta.utils import get_local_ip, hooks, logging, send
from fta.utils.conf import get_fta_admin_str, get_fta_boss_str
from fta.utils.decorator import redis_lock

logger = logging.getLogger("root")

LOCAL_IP = get_local_ip()

EXCEPTION_LINE = u"-" * 15


def exception(message, filename=None, lineno=None, exc_info=None):
    if not filename or not lineno:
        _, _, tb = sys.exc_info()
        filename, lineno, _, _ = traceback.extract_tb(tb)[-1]

    if not exc_info:
        exc_info = traceback.format_exc().split("\n")

    lines = [
        u"【自愈通知】【异常错误】",
        u"【%s:%s:%s】" % (LOCAL_IP, filename, lineno),
        u"%s" % message
    ]
    lines.append(EXCEPTION_LINE)
    lines.extend(exc_info)
    error_key = "send_info.exception: %s at %s" % (filename, lineno)

    try:
        _send(lines, error_key, message, logging.EXCEPTION)
    except Exception:
        logger.error("send exception message errror")


def error(message, filename=None, lineno=None):
    if not filename or not lineno:
        filename = inspect.currentframe().f_back.f_code.co_filename
        lineno = inspect.currentframe().f_back.f_lineno

    lines = [
        u"【自愈通知】【错误】",
        u"【%s:%s:%s】" % (LOCAL_IP, filename, lineno),
        u"%s" % message
    ]
    error_key = "send_info.error: %s at %s" % (filename, lineno)

    _send(lines, error_key, message, logging.ERROR)


def critical(message, filename=None, lineno=None):
    if not filename or not lineno:
        filename = inspect.currentframe().f_back.f_code.co_filename
        lineno = inspect.currentframe().f_back.f_lineno
    error_key = "send_info.error: %s at %s" % (filename, lineno)
    lines = [u"故障自愈重要告警,%s" % message]
    _send(lines, error_key, message, logging.CRITICAL)


def _send(lines, error_key, message, level):
    # 如果环境指定了强制接收人，则用强制接受人
    try:
        receiver = ','.join(settings.VERIFIER)
    except BaseException:
        receiver = ""
    # 没指定强制接收人，则发给管理员
    if not receiver:
        receiver = get_fta_admin_str()

    # 不同级别的日志采用不同的通知方式
    if level == 30:
        send_func = mail_key_value
        # 对于 warning 通知至少收敛 1 小时
        # send_func = redis_lock("send_warning_lock", 60*60)(send_func)
    if level == 40:
        send_func = wechat_or_sms_send
        # 根据 文件名+文件行号 的 key 收敛 5 分钟通知
        send_func = redis_lock(error_key, 60 * 5)(send_func)
        # 根据 通知内容 的 key 收敛 5 分钟通知
        send_func = redis_lock(message, 60 * 5)(send_func)
    elif level == 50:
        send_func = phone_and_other_send
        # 根据 文件名+文件行号 的 key 收敛 30 分钟通知
        send_func = redis_lock(error_key, 60 * 30)(send_func)
        # 根据 通知内容 的 key 收敛 30 分钟通知
        send_func = redis_lock(message, 60 * 30)(send_func)

    send_func(receiver=receiver, message="\n".join(lines))


def default_wechat_or_sms_send(receiver, message):
    """发送微信或短信通知"""
    if settings.ENV == "PRODUCT":
        # 发给开发者自己的正式环境告警, 需要使用微信和短信2种通知方式
        if send.wechat(receiver, message) is False:
            logger.error("%s send to [%s] wechat message[%s] failure" %
                         (constants.ERROR_02_ESB_WECHAT, receiver, message))
            if send.sms(receiver, message.split(EXCEPTION_LINE)[0]) is False:
                logger.error(
                    "%s send to [%s] sms message[%s] failure" %
                    (constants.ERROR_02_ESB_SMS, receiver, message))
        # 正式环境的告警额外微信通知给 BOSS
        fta_boss_str = get_fta_boss_str()
        send.wechat(fta_boss_str, message)
    else:
        # 尝试通过组件发送微信
        if send.wechat(receiver, message) is False:
            # 失败则尝试通过组件发送短信
            if send.sms(receiver, message.split(EXCEPTION_LINE)[0]) is False:
                logger.error(
                    "%s send to [%s]  message[%s] all failure" %
                    (constants.ERROR_02_ESB_SMS, receiver, message))


def phone_and_other_send(receiver, message):
    """正式环境的重要告警, 直接电话通知"""
    wechat_or_sms_send(receiver, message)
    if settings.ENV == "PRODUCT":
        receiver = receiver.split(",")
        random.shuffle(receiver)
        send.phone(receiver, message)


def mail_key_value(receiver, message):
    message = message.replace("\n", "<br/>")
    send.mail(receiver, message, u"【自愈通知】【WARNING 日志汇总】")


hook = hooks.HookManager("send_notice")
wechat_or_sms_send = hook.get('wechat_or_sms_send', default_wechat_or_sms_send)
