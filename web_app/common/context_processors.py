# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
'''
context_processor for common(setting)

** 除setting外的其他context_processor内容，均采用组件的方式(string)
'''
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _

from project.conf.user import get_show_name, get_avatar, get_usermgr_url


def mysetting(request):
    return {
        '_': _,
        'MEDIA_URL': settings.MEDIA_URL,  # MEDIA_URL
        'STATIC_URL': settings.STATIC_URL,  # 本地静态文件访问
        'APP_PATH': request.get_full_path(),  # 当前页面，主要为了login_required做跳转用
        'RUN_MODE': settings.RUN_MODE,  # 运行模式
        'APP_CODE': settings.APP_CODE,  # 在蓝鲸系统中注册的  "应用编码"
        'SITE_URL': settings.SITE_URL,  # URL前缀
        'REMOTE_STATIC_URL': settings.REMOTE_STATIC_URL,  # 远程静态资源url
        'STATIC_VERSION': settings.STATIC_VERSION,  # 静态资源版本号,用于指示浏览器更新缓存
        'SETTINGS_JS_NAME': settings.SETTINGS_JS_NAME,
        'OP_URL_PREFIX': settings.OP_URL_PREFIX,
        'WECHAT_APP_URL': settings.WECHAT_APP_URL,
        'IS_ADMIN_OPERATE_ALL_BIZ': settings.IS_ADMIN_OPERATE_ALL_BIZ,
        'IS_FTA_HELPER': settings.IS_FTA_HELPER,
        'HTML_TITLE': settings.HTML_TITLE,
        'GCLOUD_DETAIL_ENDPOINT': settings.GCLOUD_DETAIL_ENDPOINT,
        'CC_NEW_APP_URL': settings.CC_NEW_APP_URL,
        'BK_JOB_HOST': settings.BK_JOB_HOST,
        'BK_CC_HOST': settings.BK_CC_HOST,
        'SHOW_NAME': get_show_name(request),
        'BK_PAAS_HOST': settings.BK_PAAS_HOST,
        'NOW': timezone.now(),
        'AVATAR': get_avatar(request),  # 用户头像
        'USERMGR_URL': get_usermgr_url(request),
    }


def get_constant_settings():
    return {}
