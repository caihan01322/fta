# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from django.core import serializers

from common.django_utils import strftime_local


def obj_to_dict(obj):
    """
    将django对象转为字典
    注意如果有外键或时间，需要特殊处理.  外键主要是要与芯雲兼容
    """
    obj_str = serializers.serialize("json", [obj, ], ensure_ascii=False)
    obj_json = json.loads(obj_str)
    obj_dict = obj_json[0]['fields']
    obj_dict['id'] = obj_json[0]['pk']

    # 处理datetime
    if obj_json[0]['model'] == 'fta_solutions_app.alarminstance':
        obj_dict['source_time'] = {
            "__type__": "datetime",
            "__value__": obj.source_time_show
        }
        obj_dict['begin_time'] = {
            "__type__": "datetime",
            "__value__": strftime_local(obj.begin_time)
        }

    return obj_dict
