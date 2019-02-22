# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import pytz
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _

from common import context_processors
from common.mymako import render_mako_context
from permission.exceptions import APIError


class TimezoneMiddleware(object):
    def process_request(self, request):
        tzname = request.session.get('blueking_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


class ApiExceptionMiddleware(object):
    """调用ESB异常处理中间件"""

    def process_exception(self, request, exception):
        """
        Capture APIError and replace it with user-friendly error response
        """
        if isinstance(exception, APIError):
            error_msg = _(u"调用 ESB API 接口异常，请联系开发者处理")
            if not request.is_ajax():
                context = {'error_msg': error_msg}
                context.update(context_processors.get_constant_settings())
                return render_mako_context(request, 'api_error.html', context)
            else:
                return HttpResponse(error_msg)
