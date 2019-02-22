# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from fta_utils.component import bk
from fta_utils.request_middlewares import get_request
from permission.exceptions import APIError
from project.permission.utils import prepare_user_business


class CCBiz(object):
    """
    使用方法：
    >>> CCBiz(username='123', cc_biz_id=120).get("GroupName")

    >>> CCBiz(username='123').items(key="ApplicationID", value="ApplicationName")  # 获取字典
    """

    def __init__(self, username=None, cc_biz_id=None, cc_biz_name=None):
        assert username
        bk.set_username(username)
        if cc_biz_id:
            self.key = "ApplicationID"
            self.key_value = unicode(cc_biz_id)
        elif cc_biz_name:
            self.key = "ApplicationName"
            self.key_value = unicode(cc_biz_name)

    def get(self, attr_name, default=None):
        return self.get_items(self.key, attr_name).get(self.key_value, default)

    @staticmethod
    def get_items(key, value):
        data = {}
        cc_result = bk.cc.get_app_by_user(data)

        if not cc_result.get('result', False):
            raise APIError(cc_result.get('message', 'call component sdk error'))
        cc_data = cc_result['data']
        return {unicode(biz[key]): unicode(biz.get(value, '')) for biz in cc_data if biz.get('Default') == '0'}

    @staticmethod
    def items(key, value):
        try:
            # 直接从数据库中查询，不再查 cc 接口
            request = get_request()
            biz_list = prepare_user_business(request)
            return {unicode(biz.cc_id): unicode(biz.cc_name) for biz in biz_list}
        except Exception:
            data = {}
            cc_result = bk.cc.get_app_by_user(data)

            if not cc_result.get('result', False):
                raise APIError(cc_result.get('message', 'call component sdk error'))
            cc_data = cc_result['data']
            return {unicode(biz[key]): unicode(biz.get(value, '')) for biz in cc_data if biz.get('Default') == '0'}
