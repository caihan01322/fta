# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""API公共校验方法
"""
import base64
import datetime
import json

import arrow

from dateutil.parser import parse
from fta import constants
from fta.utils import hooks
from fta.utils import is_ip as _is_ip
from fta.utils.i18n import _


class ValidateError(Exception):
    pass


def is_json(data):
    try:
        data = json.loads(data)
    except BaseException:
        raise ValidateError(_("Invalid JSON format"))
    if not isinstance(data, dict):
        raise ValidateError(_("JSON must be dict type"))
    return data


def fix_field_by_app(data, fields, app_id):
    for f in fields:
        data[f] = "%s:%s" % (app_id, data[f])
    return data


def is_required(data, fields):
    """检查是否存在，为空, data是合法的dict
    """
    for field in fields:
        if not data.get(field):
            raise ValidateError(_("The field [%(field)s] does not exist or is empty", field=field))
    return data


def is_ip(data, fields):
    for field in fields:
        value = data[field]
        if not _is_ip(value):
            raise ValidateError(_("The field [%(field)s] is an invalid IP address", field=field))
    return data


def is_datetime(data, fields, format=None, replace=False, tzinfo=None):
    for field in fields:
        value = data[field]
        try:
            params = [value]
            if format:
                params.append(format)

            clean_value = arrow.get(*params)
            # 如果告警源已经有时区，则忽略tzinfo
            try:
                source_tzinfo = parse(value).tzinfo
            except Exception:
                source_tzinfo = None
            if source_tzinfo is None and tzinfo:
                clean_value = clean_value.replace(tzinfo=tzinfo)
            clean_value = clean_value.to('utc').format(constants.STD_ARROW_FORMAT)
        except BaseException:
            msg = _("The field [%(field)s] is an invalid time format. Time format must be like: %(time)s",
                    field=field, time=datetime.datetime.now.strftime(format))
            raise ValidateError(msg)

        else:
            if replace:
                data[field] = clean_value
    return data


def is_format(data, fields, format='', replace=False):
    for field in fields:
        value = data[field]
        try:
            if format == 'json':
                clean_value = json.loads(value)
            elif format == 'base64':
                clean_value = base64.b64decode(value)
            else:
                clean_value = value
        except BaseException:
            raise ValidateError(
                _("The field [%(field)s] is in invalid %(format)s format", field=field, format=format))
        else:
            if replace:
                data[field] = clean_value
    return data


hook = hooks.HookImport('manager.www.utils.validate', fail_silently=False)
hook.import_all('is_', env=locals())
