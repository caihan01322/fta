# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""微信登录"""
from django.contrib import auth
from django.http import HttpResponseRedirect

from account.decorators import login_exempt
from common.log import logger
from common.mymako import render_mako_context
from fta_solutions_app.models import Conf
from wechat.auth import utils
from wechat.enterprise import get_oauth_redirect_url


@login_exempt
def login(request):
    """企业号登陆接口
    """
    try:
        # 获取跳转链接
        location = request.GET.get('next', '').strip()
        if not location:
            wechat_app_url = Conf.get('WECHAT_APP_URL')
            location = '%stodo/' % wechat_app_url

        # 已经验证用户先登出，再跳转
        if request.user.is_authenticated():
            auth.logout(request)

        code = request.GET.get('code')
        state = request.GET.get('state')

        if code and state:
            if not utils.valid_state(request, state):
                # state验证非法，
                return render_mako_context(request, 'wechat/wx_error.html', {'message': u"登录已经失效，请刷新后重试！"})
            if code == 'authdeny':
                # 获取用户权限失败
                return render_mako_context(request, 'wechat/wx_error.html', {'message': u"授权被拒绝，请刷新后重试！"})
            user = auth.authenticate(code=code)
            if user:
                auth.login(request, user)
                response = HttpResponseRedirect(location)
                return response
        elif not state:
            # 构造链接
            uri = request.build_absolute_uri()
            state = utils.set_state(request)
            redirect_uri = get_oauth_redirect_url(uri, state=state)
            logger.info('redirect_uri %s' % redirect_uri)
            return HttpResponseRedirect(redirect_uri)
        # code验证非法等其他情况，
        return render_mako_context(request, 'wechat/wx_error.html', {'message': u"登录已经失效，请刷新后重试！"})
    except Exception as error:
        logger.error('wechat login error: %s' % error)
        return render_mako_context(request, 'wechat/wx_error.html', {'message': u"登录已经失效，请刷新后重试！"})
