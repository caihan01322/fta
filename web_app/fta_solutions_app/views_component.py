# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

from django.http import HttpResponse, JsonResponse

from fta_utils.component import bk


def gcloud_component(request, cc_biz_id, task_name):
    from project.component.gcloud import get_gcloud_client_from_request
    if not request.user.is_authenticated():
        return JsonResponse({"success": False, "message": "authorization failure", })

    client = get_gcloud_client_from_request(request, cc_biz_id)
    try:
        kwargs = json.loads(request.POST.get('kwargs', '{}'))
        # 参数兼容v2版本API
        kwargs['bk_biz_id'] = cc_biz_id
        if 'tmpl_id' in kwargs:
            kwargs['template_id'] = kwargs['tmpl_id']
        task = getattr(client, task_name, None)
        if not task:
            return JsonResponse({"success": False, "message": "no permission", })
        result = task(kwargs)
        return JsonResponse({
            "success": result.get("result"),
            "data": result.get("data"),
            "message": result.get("message"),
        })
    except Exception as err:
        return JsonResponse({"success": False, "message": "execute failed: %s" % err, })


def component(request, cc_biz_id, module, task_name):
    """给前端用的调用组件的一个转发接口"""
    try:
        task = getattr(getattr(bk, module), task_name)
        kwargs = json.loads(request.POST.get('kwargs', '{}'))
        result = task(**kwargs)
        data = result.get('data')
    except Exception, e:
        return HttpResponse(json.dumps({"success": False, "message": str(e)}))
    return HttpResponse(json.dumps({"success": True, "message": data}))
