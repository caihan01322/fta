# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa


class ResponseToolkit(object):
    CODE_NOT_SET = 0
    CODE_OK = 1200
    CODE_VERIFY_ERROR = 1400
    CODE_SYSTEM_ERROR = 1500

    @classmethod
    def make_json_response(
            cls, result=None, success=False, message=u"ok", code=0, status_code=200, response_args=None,
    ):
        from django.http import JsonResponse
        response_args = response_args or {}
        response_args.setdefault("status", status_code)
        return JsonResponse({
            "result": result,
            "success": success,
            "message": message,
            "code": code,
        }, **response_args)
