# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    string_types = (str, unicode)
else:
    text_type = str
    string_types = (str, )


class LazyString(object):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, attr):
        if attr == "__setstate__":
            raise AttributeError(attr)
        string = text_type(self)
        if hasattr(string, attr):
            return getattr(string, attr)
        raise AttributeError(attr)

    def __repr__(self):
        return "l'{0}'".format(text_type(self))

    def __str__(self):
        return text_type(self._func(*self._args, **self._kwargs))

    def __len__(self):
        return len(text_type(self))

    def __getitem__(self, key):
        return text_type(self)[key]

    def __iter__(self):
        return iter(text_type(self))

    def __contains__(self, item):
        return item in text_type(self)

    def __add__(self, other):
        return text_type(self) + other

    def __radd__(self, other):
        return other + text_type(self)

    def __mul__(self, other):
        return text_type(self) * other

    def __rmul__(self, other):
        return other * text_type(self)

    def __lt__(self, other):
        return text_type(self) < other

    def __le__(self, other):
        return text_type(self) <= other

    def __eq__(self, other):
        return text_type(self) == other

    def __ne__(self, other):
        return text_type(self) != other

    def __gt__(self, other):
        return text_type(self) > other

    def __ge__(self, other):
        return text_type(self) >= other

    def __html__(self):
        return text_type(self)

    def __hash__(self):
        return hash(text_type(self))

    def __mod__(self, other):
        return text_type(self) % other

    def __rmod__(self, other):
        return other + text_type(self)
