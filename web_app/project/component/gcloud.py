# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import urlparse

from django.conf import settings


class FtaGCloudClient(object):

    def __init__(
            self, request, cc_biz_id, app_code=None, app_secret=None, headers=None, common_args=None,
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
        self.headers = headers or {}
        self.detail_link = detail_link or urlparse.urljoin(getattr(
            settings, "GCLOUD_DETAIL_ENDPOINT",
            "http://gcloud-v2.test.qcloudapps.com/"
        ), "taskflow/execute/{cc_biz_id}/?instance_id={task_id}")

        self.sdk_package = __import__(settings.ESB_MODULE, fromlist=['shortcuts'])
        self.sdk_client = self.sdk_package.shortcuts.get_client_by_request(request)
        self.sops_mod = getattr(self.sdk_client, 'sops', None)

        self.create_task = getattr(self.sops_mod, 'create_task', None)

        self.get_task_status = getattr(self.sops_mod, 'get_task_status', None)

        self.run_task = getattr(self.sops_mod, 'start_task', None)

        self.get_tmpl = getattr(self.sops_mod, 'get_template_list', None)

        self.get_tmpl_info = getattr(self.sops_mod, 'get_template_info', None)

    @property
    def api(self):
        return self

    def task_detail_url(self, task_id):
        return self.detail_link.format(
            task_id=task_id, cc_biz_id=self.cc_biz_id,
        )


def get_gcloud_client_from_request(request, cc_biz_id, *args, **kwargs):
    return FtaGCloudClient(request, cc_biz_id)
