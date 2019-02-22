# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext as _

from common import context_processors
from common.mymako import render_mako_context
from permission import exceptions
from project.permission.utils import prepare_business, _redirect_to_login, record_login_log


class PermissionMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        If a request path contains cc_biz_id parameter, check if current
        user has perm view_business or return http 403.
        """
        if getattr(view_func, "login_exempt", False):
            return

        cc_biz_id = view_kwargs.get('cc_biz_id')
        if cc_biz_id:
            try:
                business = prepare_business(request, cc_id=cc_biz_id)
            except exceptions.Unauthorized:
                # permission denied for target business (irregular request)
                return HttpResponse(status=406)
            except exceptions.Forbidden:
                # target business does not exist (irregular request)
                return HttpResponseForbidden()

            if not request.user.has_perm('view_business', business):
                return HttpResponseForbidden()
        # 用户验证成功，记录登录日志
        record_login_log(request)


class UnauthorizedMiddleware(object):

    def process_response(self, request, response):
        if settings.DEBUG:
            return response
        if response.status_code in (403,):
            response = HttpResponse(
                content=_(u"您没有权限执行此操作"),
                status=400
            )
            if not request.is_ajax():
                rtx = {}
                rtx.update(context_processors.get_constant_settings())
                return render_mako_context(request, '400.html', rtx)
        return response


class NotAcceptableMiddleware(object):

    def process_response(self, request, response):
        if response.status_code == 406:
            # 对于登录态不OK的用户， 引导重新登录 （首页的直接跳登录页， 非首页的跳登录态错误页）
            response = _redirect_to_login(request)
        return response


class AnalysisPermissionMiddleware(object):
    '''
    analysis开头的url必须是超级管理员才能访问
    '''

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path
        if path.startswith('/analysis/'):
            if not request.user.is_superuser:
                return HttpResponseForbidden()
