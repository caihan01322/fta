# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from common.mymako import render_mako_context, render_json
from fta_solutions_app.models import Conf


def wechat_config(request):
    """
    微信配置
    """
    # 只有管理员有权限
    if not request.user.is_superuser:
        return redirect('admin:index')
    url_config = [
        {
            'name': 'WECHAT_APP_URL',
            'value': Conf.get('WECHAT_APP_URL'),
            'description': _(u"微信端地址(外网可访问)")
        },
        {
            'name': 'WECHAT_STATIC_URL',
            'value': Conf.get('WECHAT_STATIC_URL'),
            'description': _(u"微信端静态资源地址(外网可访问)")
        }
    ]
    set_configs = [conf for conf in settings.WECHAT_CONFIG
                   if conf.get('name') != 'WECHAT_API_TOKEN']
    extra_config = [
        {
            'name': 'WECHAT_SUPER_APPROVER',
            'value': Conf.get('WECHAT_STATIC_URL'),
            'description': _(u"审批管理员")
        }
    ]
    configs = url_config + set_configs + extra_config
    context = {
        'SITE_URL': settings.SITE_URL,
        'STATIC_URL': settings.STATIC_URL,
        'configs': configs,
    }
    return render_mako_context(request, 'admin/wechat_config.html', context)


def save_wechat_config(request):
    """
    保存微信配置信息
    """
    # 只有管理员有权限
    if not request.user.is_superuser:
        return redirect('admin:index')

    conf_name = request.POST.get('conf_name')
    conf_value = request.POST.get('conf_value')
    if not conf_name or not conf_value:
        return render_json({'result': False, 'message': _(u"参数错误")})

    Conf.set(conf_name, conf_value)
    return render_json({'result': True, 'message': _(u"配置修改成功")})
