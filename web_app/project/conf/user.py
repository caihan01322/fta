# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
用户相关方法
"""
from django.conf import settings
from django.utils.translation import ugettext as _

from account.models import BkUser


def get_full_name(username):
    """
    根据username查询用户的用户名和中文名
    """
    try:
        user = BkUser.objects.get(username=username)
        show_name = "%s(%s)" % (username, user.chname)
    except Exception:
        show_name = username
    return show_name


def get_short_name(username):
    """
    根据openid查询展示的uin
    """
    return username


def get_show_name(request):
    """
    获取页面上展示的用户名
    """
    return request.user.username


def get_avatar(request):
    """
    获取用户头像
    """
    return u"%simages/getheadimg.jpg" % settings.STATIC_URL


def get_usermgr_url(request):
    """获取用户中心链接
    """
    url = '%s/login/accounts/' % settings.BK_PAAS_HOST
    return _(u'<a href="%s" target="_blank">【用户管理】</a>') % (url)
