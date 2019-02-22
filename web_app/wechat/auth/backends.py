# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from common.log import logger
from wechat.enterprise import get_user_info

User = get_user_model()


class WeChatBackend(ModelBackend):
    """微信backend"""

    def authenticate(self, code, *args, **kwargs):
        """
        code是oauth2.0 协议生成的code
        """
        try:
            user = self.qy_auth(code)
            return user
        except Exception as error:
            logger.error(u"用户验证异常: %s" % error)

    def qy_auth(self, code):
        """企业号验证
        """
        result = get_user_info(code)
        userid = result.get('UserId')
        if not userid:
            logger.error(u"用户验证失败, UserId为空")
            return None
        user, _ = User.objects.get_or_create(username=userid)
        return user
