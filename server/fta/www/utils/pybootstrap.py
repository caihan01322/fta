# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import traceback

from fta.utils import logging

logger = logging.getLogger('webserver')


class Row(object):

    TYPE = "row"

    def __init__(self, *args):
        self.i = -1
        self.args = args

    def next(self):
        try:
            self.i += 1
            return self.args[self.i]
        except BaseException:
            raise StopIteration

    def __iter__(self):
        return self


class Col(object):

    TYPE = "col"

    def __init__(self, *args, **kwargs):
        self.i = -1
        self.args = args
        self.kwargs = kwargs

    def next(self):
        try:
            self.i += 1
            return self.args[self.i]
        except BaseException:
            raise StopIteration

    def __iter__(self):
        return self


def merge_attr(*attr_dicts):
    result = {}
    for attr_dict in attr_dicts:
        for k, v in attr_dict.items():
            if k in result:
                result[k] = ' '.join([result[k], v])
            else:
                result[k] = v
    return result


class Field(object):

    DEFAULT_ATTR = {"class": "form-control"}

    def __init__(self, name, **kwargs):
        std_attr = {"name": name, "id": name}
        attr_dict = merge_attr(self.DEFAULT_ATTR, std_attr, kwargs)
        attr_list = ['%s="%s"' % (k, v) for k, v in attr_dict.items()]
        self.name = name
        self.attrs = " ".join(attr_list)
        self.value = ""

    def set_value(self, value):
        self.value = value


class TextAreaField(Field):

    TYPE = "textarea"


class SubmitField(Field):

    DEFAULT_ATTR = {"class": "btn"}

    TYPE = "submit"


class Form(object):

    def __init__(self, form={}, action_url=""):
        self._info_list = []
        self._error_list = []
        self._action_url = action_url
        self._form = form
        if self._form:
            for attr in self._field_attr():
                getattr(self, attr).set_value(self._clean_attr(attr))

    def _clean_attr(self, attr):
        clean_func_name = "clean_%s" % attr
        if hasattr(self, clean_func_name):
            clean_func = getattr(self, clean_func_name, lambda s, x: "")
            try:
                return clean_func(self._form.get(attr, ""))
            except Exception as e:
                logger.exception(e)
                self.add__error(e)
                return traceback.format_exc()
        return self._form.get(attr) or ""

    def _field_attr(self):
        attrs = []
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            if isinstance(getattr(self, attr), Field):
                attrs.append(attr)
        return attrs

    def add__info(self, info):
        self._info_list.append(info)

    def set__info(self, info):
        self._info_list = [info]

    def add__error(self, error):
        self._error_list.append(error)

    def set__error(self, error):
        self._error_list = [error]
