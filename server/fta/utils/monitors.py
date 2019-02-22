# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import re

from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppAlarmType


def query_alarm_type(
    cc_biz_id=None, source_type=None, alarm_type=None, is_enabled=True,
    with_template=True,
):
    q = session.query(FtaSolutionsAppAlarmType)
    if cc_biz_id is not None:
        if with_template:
            q = q.filter(FtaSolutionsAppAlarmType.cc_biz_id.in_([cc_biz_id, 0]))
        else:
            q = q.filter(FtaSolutionsAppAlarmType.cc_biz_id == cc_biz_id)
    if source_type:
        q = q.filter(FtaSolutionsAppAlarmType.source_type == source_type)
    if alarm_type:
        q = q.filter(FtaSolutionsAppAlarmType.alarm_type == alarm_type)
    if is_enabled is not None:
        q = q.filter(FtaSolutionsAppAlarmType.is_enabled == is_enabled)
    return q


def get_alarm_type(
    cc_biz_id=None, source_type=None, with_template=True, queries=None,
):
    q = queries or query_alarm_type(
        cc_biz_id=cc_biz_id, source_type=source_type,
        with_template=with_template,
    )
    for i in q:
        obj_dict = orm_2_dict(i)
        if obj_dict["cc_biz_id"] != 0 or cc_biz_id not in obj_dict["exclude"].split(","):
            yield obj_dict


def match_alarm_type(value, alarm_type):
    match_mode = alarm_type["match_mode"]
    if match_mode == 0:
        return value == alarm_type["pattern"]
    elif match_mode == 1:
        pattern = (alarm_type.get("regex_pattern") or re.compile(alarm_type["pattern"]))
        return pattern.match(value) is not None
    elif match_mode == 2:
        from fnmatch import fnmatch
        return fnmatch(value, alarm_type["pattern"])
    return False


def lookup_alarm_type(value, alarm_type_list):
    for i in alarm_type_list:
        if match_alarm_type(value, i):
            yield i


def lookup_alarm_type_list(
    value_list, cc_biz_id, source_type,
    default=NotImplemented, with_template=True,
):
    alarm_type_pattern_list = list(get_alarm_type(
        cc_biz_id=cc_biz_id, source_type=source_type,
        with_template=with_template,
    ))
    matched = False
    for value in value_list:
        for i in lookup_alarm_type(value, alarm_type_pattern_list):
            yield i["alarm_type"]
            matched = True

    if not matched and default is not NotImplemented:
        yield default


def get_description_by_alarm_type(
    alarm_type, source_type=None, cc_biz_id=None, default=None,
):
    for i in query_alarm_type(
        alarm_type=alarm_type, source_type=source_type, cc_biz_id=cc_biz_id,
    ):
        if cc_biz_id and cc_biz_id not in i.exclude.split(","):
            return i.description
    return default
