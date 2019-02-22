# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""all send method here"""

from fta.utils import logging

logger = logging.getLogger('utils')

__ALL__ = ['wechat', 'sms', 'im', 'mail', 'phone']


def wechat(verifier, message):
    logger.info(u"send.wechat(%s): %s", verifier, message)
    return False


def sms(verifier, message):
    logger.info(u"send.sms(%s): %s", verifier, message)
    return False


def im(verifier, message):
    logger.info(u"send.im(%s): %s", verifier, message)
    return False


def mail(verifier, message, title):
    logger.info(u"send.mail(%s): %s", verifier, message)
    return False


def phone(verifier, message):
    logger.info(u"send.phone(%s): %s", verifier, message)
    return False
