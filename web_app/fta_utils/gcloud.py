# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import logging
import urlparse
from functools import partial

import requests

try:
    from fta import settings
except ImportError:
    try:
        from django.conf import settings
    except ImportError:
        pass

logger = logging.getLogger(__name__)


class FtaGCloudClient(object):

    def __init__(
            self, cc_biz_id, app_code=None, app_secret=None, headers=None, common_args=None,
            timeout=None, endpoint=None, detail_link=None
    ):
        """
        :param str app_code: App code to use
        :param str app_secret: App secret to use
        :param dict headers: headers be sent to api
        :param dict common_args: Args that will apply to every request
        :param int timeout: timeout for request
        """

        self.cc_biz_id = cc_biz_id
        self.app_code = app_code or getattr(settings, "APP_CODE", None)
        self.app_secret = app_secret or getattr(settings, "APP_SECRET_KEY", None)
        self.headers = headers or {}
        self.common_args = common_args or {}
        self.timeout = timeout
        self.endpoint = endpoint or getattr(settings, "GCLOUD_ENDPOINT", "", )
        self.detail_link = detail_link or urlparse.urljoin(
            getattr(settings, "GCLOUD_DETAIL_ENDPOINT", ""),
            "taskflow/detail/{task_id}/{cc_biz_id}/"
        )

        self.create_task = partial(self.request, method="POST", path="task_api/create_task/{biz_cc_id}/", )
        self.get_task_status = partial(self.request, method="GET", path="task_api/get_task_status/{biz_cc_id}/", )
        self.run_task = partial(self.request, method="POST", path="task_api/run_task/{biz_cc_id}/", )
        self.get_tmpl = partial(self.request, method="GET", path="tmpl_api/get_tmpl/{biz_cc_id}/", )
        self.get_tmpl_info = partial(self.request, method="GET", path="tmpl_api/get_tmpl_info/{biz_cc_id}/", )

    @property
    def api(self):
        return self

    def task_detail_url(self, task_id):
        return self.detail_link.format(task_id=task_id, cc_biz_id=self.cc_biz_id, )

    def request(self, kwargs=None, path="", method="GET"):
        url = urlparse.urljoin(self.endpoint, path).format(biz_cc_id=self.cc_biz_id, )
        data = self.common_args.copy()
        data.update(kwargs or {})
        data.update({
            "app_code": self.app_code,
            "app_secret": self.app_secret,
        })
        request_params = {
            "headers": self.headers,
            "timeout": self.timeout,
        }

        if method == "GET":
            request_params["params"] = data
        else:
            request_params["json"] = data
        logger.info("%s %s %s", method, url, request_params)
        try:
            response = requests.request(method=method, url=url, verify=False, **request_params)
        except requests.RequestException as err:
            logger.exception(err)
            return {
                "result": False,
                "message": "request failed",
                "data": None,
            }

        if response.status_code >= 400:
            logger.error("gcloud response: %s", response.content)

        try:
            return response.json()
        except Exception as err:
            logger.error("gcloud loads json failed: %s", response.content)
            return {
                "result": False,
                "message": "loads json failed",
                "data": None,
            }
