# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from django.http import HttpResponse

from common.mymako import render_mako_context
from home_application.utils import serialize_healthz
from project.conf.decorators import login_exempt


def fta_doc(request, doc_name):
    """
    首页
    """
    return render_mako_context(request, '/doc/fta%s.html' % doc_name)


def fta_vedio(request):
    """视频教程
    """
    return render_mako_context(request, '/fta-video.html')


@login_exempt
def healthz(request):
    """
    fta healthz
    """
    healthz = json.dumps(serialize_healthz())
    if request.GET.get("is_view"):
        return render_mako_context(request, 'healthz.html', {"healthz": healthz})
    return HttpResponse(healthz)
