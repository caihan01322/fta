# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.conf import settings

from fta_utils.request_middlewares import get_request


class SDKClient(object):
    sdk_package = None
    sdk_plat_module = dict()

    @property
    def __version__(self):
        return self.__class__.sdk_package.__version__

    def __new__(cls, is_backend=False):
        if cls.sdk_package is None:
            try:
                cls.sdk_package = __import__(settings.ESB_MODULE, fromlist=['shortcuts'])
            except ImportError, e:
                raise ImportError("Sdk is not found in project dir: %s" % e)
        return super(SDKClient, cls).__new__(cls, is_backend)

    def __init__(self, is_backend=False):
        self.mod_name = ""
        self.sdk_mod = None
        self.username = ""
        self.is_backend = is_backend

    def __getattr__(self, item):
        if not self.mod_name:
            ret = SDKClient()
            ret.mod_name = item
            ret.username = self.username
            ret.is_backend = self.is_backend
            ret.setup_modules()
            if callable(ret.sdk_mod):
                return ret.sdk_mod
            return ret
        else:
            ret = getattr(self.sdk_mod, item)
        if callable(ret):
            pass
        else:
            ret = self
        return ret

    def set_username(self, username):
        self.username = username

    def setup_modules(self):
        if self.is_backend:
            self.sdk_mod = getattr(self.sdk_client_backend, self.mod_name, None)
        else:
            self.sdk_mod = getattr(self.sdk_client, self.mod_name, None)
        if self.sdk_mod is None:
            raise ImportError("Sdk(%s) has no module :%s" % (id(self), self.mod_name))

    @property
    def sdk_client(self):
        """
        调用与业务相关的接口，如查询用户的业务信息等
        必须传入用户的身份信息，如 request 或 username
        """
        try:
            request = get_request()
            # 调用sdk方法获取sdk client
            return self.sdk_package.shortcuts.get_client_by_request(request)
        except Exception, e1:
            if not self.username:
                raise e1
            try:
                return self.sdk_package.shortcuts.get_client_by_user(self.username)
            except Exception, e:
                raise e

    @property
    def sdk_client_backend(self):
        """
        调用与业务无关的接口，如发送短信等
        只需要获取一个有效的 auth_token 即可
        """
        try:
            from project.conf.user import BkUser as User
            username = User.objects.filter(is_staff=True).order_by("-last_login")[0].username
            # 获取当前最新的 auth_token
            return self.sdk_package.shortcuts.get_client_by_user(username)
        except Exception, e:
            raise e


bk = SDKClient()
