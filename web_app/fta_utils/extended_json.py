# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID

import arrow

STD_DT_FORMAT = '%Y-%m-%d %H:%M:%S'  # 2015-01-21 10:18:06
STD_ARROW_FORMAT = 'YYYY-MM-DD HH:mm:ss'  # 2015-01-21 10:18:06

SUPPORTED_TYPES = {datetime, date, time, Decimal, UUID, set}
assert len(SUPPORTED_TYPES) == len({c.__name__ for c in SUPPORTED_TYPES})
SUPPORTED_TYPES_NAME2CLASS = {c.__name__: c for c in SUPPORTED_TYPES}


class CustomJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        type_ = type(obj)
        if type_ in SUPPORTED_TYPES:
            if issubclass(type_, (datetime, date, time)):
                return {'__type__': type_.__name__, '__value__': obj.strftime(STD_DT_FORMAT)}
            if issubclass(type_, Decimal):
                return {'__type__': type_.__name__, '__value__': obj.as_tuple()}
            if issubclass(type_, UUID):
                return {'__type__': type_.__name__, '__value__': obj.hex}
            if issubclass(type_, set):
                return list(obj)
        return json.JSONEncoder.default(self, obj)


class CustomJSONDecoder(json.JSONDecoder):

    def __init__(self, **kw):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, **kw)

    def dict_to_object(self, d):
        type_ = SUPPORTED_TYPES_NAME2CLASS.get(d.get('__type__'))
        if type_ in SUPPORTED_TYPES:
            if issubclass(type_, (datetime, date, time)):
                dt = arrow.get(d.get('__value__')).replace(tzinfo='local').naive
                if type_ is datetime:
                    return dt
                elif type_ is date:
                    return dt.date()
                else:
                    return dt.timetz()
            if issubclass(type_, Decimal):
                return Decimal(d.get('__value__'))
            if issubclass(type_, UUID):
                return UUID(d.get('__value__'))
        return d


class JSONEncoderDT(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime(STD_DT_FORMAT)
        else:
            return super(JSONEncoderDT, self).default(o)


class JSONDecoderDT(json.JSONDecoder):

    def __init__(self, **kw):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, **kw)

    def dict_to_object(self, d):
        type_ = SUPPORTED_TYPES_NAME2CLASS.get(d.get('__type__'))
        if type_ in SUPPORTED_TYPES:
            if issubclass(type_, (datetime, date, time)):
                return d.get('__value__')
        return d


class JSONDecoderMongo(json.JSONDecoder):

    def __init__(self, **kw):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, **kw)

    def dict_to_object(self, d):
        if "$oid" in d:
            return d["$oid"]
        if "$date" in d:
            timestamp = str(d["$date"])[:-3]
            return arrow.get(timestamp).format(STD_ARROW_FORMAT)
        return d


def dumps(obj, **kwargs):
    return json.dumps(obj, cls=CustomJSONEncoder, **kwargs)


def loads(s, **kwargs):
    return json.loads(s, cls=CustomJSONDecoder, **kwargs)
