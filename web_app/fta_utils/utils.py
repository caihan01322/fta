# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from contextlib import contextmanager
from functools import wraps


@contextmanager
def catch(reraise=False, callback=None):
    '''Context manager to catch exception raised from a block
    '''
    result = {
        "exception": None,
    }
    try:
        yield result
    except Exception as err:
        result["exception"] = err
        if callback:
            callback(err)
        if reraise:
            raise err


def func_catch(callback=None, return_value=None, *catch_args, **catch_kwargs):
    '''decorator to catch exception raised from a function
    '''

    def f(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with catch(callback=callback, *catch_args, **catch_kwargs):
                return func(*args, **kwargs)
            return return_value

        return wrapper

    return f


class Enum(object):

    def __init__(self, items):
        self._items = items
        self._name2value = {}
        self._value2name = {}
        for name, value in items:
            if name in self._name2value:
                raise KeyError(name)
            self._name2value[name] = value

            if value in self._value2name:
                raise KeyError(value)
            self._value2name[value] = name

    def keys(self):
        return self._name2value.keys()

    def values(self):
        return self._value2name.keys()

    def items(self):
        return zip(self.keys(), self.values())

    def __getitem__(self, name):
        return self._name2value[name]

    def __call__(self, value):
        return self._value2name[value]
