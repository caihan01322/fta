# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import random

import arrow

from fta import settings
from fta.storage.cache import Cache
from fta.utils import logging

# from fta.utils import get_local_ip

logger = logging.getLogger("utils")

cache = Cache()


class CallbackManager(object):

    def __init__(self, component):
        self.component = component

    @property
    def default_data(self):
        if settings.SOLUTION_DUMMY is not False:
            self.component._default_data.update({"dummy": True})
            logger.error(
                "Call ExecComponent When SOLUTION_DUMMY is True: %s",
                self.component._url)
        return self.component._default_data

    @property
    def instance_id(self):
        if not hasattr(self, "_instance_id"):
            self._instance_id = cache.get("id") or arrow.utcnow().timestamp
        return self._instance_id

    @property
    def process_id(self):
        if not hasattr(self, "_process_id"):
            self._process_id = "%s$%s$" % (
                self.component.app_code, self.instance_id)
        return self._process_id

    @property
    def instance_uniqid(self):
        if not hasattr(self, "_instance_uniqid"):
            self._instance_uniqid = self.process_id + \
                self.randstr(32 - len(self.process_id))
            logger.info(
                "$%s component uniqid %s",
                self.instance_id, self._instance_uniqid)
        return self._instance_uniqid

    @property
    def callback_url(self):
        return "%s/fta/callback/%s/" % (
            settings.WEBSERVER_URL, self.instance_uniqid)

    @staticmethod
    def randstr(length=32):
        ALPHABET = ("0123456789"
                    "abcdefghijklmnopqrstuvwxyz"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return ''.join([random.choice(ALPHABET) for _ in range(length)])
