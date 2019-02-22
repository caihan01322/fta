# -*-coding:utf8-*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json


def get_plat_info(alarm_instance):
    # 获取alarm_instance中的平台信息(包括平台ID, 开发商ID)
    origin_alarm = json.loads(alarm_instance['origin_alarm'])
    cc_plat_id = origin_alarm['_match_info'].get('cc_plat_id')
    cc_company_id = origin_alarm['_match_info'].get('cc_company_id')
    return {'plat_id': cc_plat_id, 'company_id': cc_company_id}


def convert_plat_id(plat_id):
    """把GSE的平台ID转换为CC的平台ID"""
    if plat_id == 0 or plat_id == '0':
        return 1
    return plat_id
