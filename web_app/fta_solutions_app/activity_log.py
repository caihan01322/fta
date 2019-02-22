# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import logging

from django.utils.translation import ugettext as _

from common.django_utils import strftime_local
from fta_utils.utils import Enum
from user_activity_log.client import UserActivityLogClient
from user_activity_log.models import UserActivityLog

logger = logging.getLogger(__name__)

OPERATOR_TYPE = Enum([
    ("query", 1),
    ("addition", 2),
    ("deletion", 3),
    ("modification", 4),
])

OPERATOR_TYPE_VALUES = {
    OPERATOR_TYPE["addition"]: _(u"新增"),
    OPERATOR_TYPE["modification"]: _(u"修改"),
    OPERATOR_TYPE["deletion"]: _(u"删除"),
}
OBJECT_TYPE = Enum([
    ("AlarmDef", _(u"自愈方案")),
    ("Solution", _(u"自愈套餐")),
    ("IncidentDef", _(u"收敛规则")),
    ("AdviceFtaDef", _(u"预警自愈")),
    ("AlarmType", _(u"告警类型")),
    ("AlarmApplication", _(u"告警源"))
])
_undefined = frozenset()


class ActivityLogClient(object):

    @classmethod
    def log(cls, app_code, user, content, object_, operator_type, *args, **kwargs):
        error = None
        try:
            client = UserActivityLogClient()
            client.log(
                app_code=app_code, username=user, activity_name=content,
                request_params=object_, activity_type=operator_type,
                *args, **kwargs
            )
        except Exception as err:
            logger.exception(err)
            error = err
        return error

    @classmethod
    def log_query(cls, *args, **kwargs):
        return cls.log(operator_type=OPERATOR_TYPE["query"], *args, **kwargs)

    @classmethod
    def log_addition(cls, *args, **kwargs):
        return cls.log(operator_type=OPERATOR_TYPE["addition"], *args, **kwargs)

    @classmethod
    def log_deletion(cls, *args, **kwargs):
        return cls.log(operator_type=OPERATOR_TYPE["deletion"], *args, **kwargs)

    @classmethod
    def log_modification(cls, *args, **kwargs):
        return cls.log(operator_type=OPERATOR_TYPE["modification"], *args, **kwargs)

    @classmethod
    def instance_to_dict(cls, instance):
        name = instance.get_show_name
        operator_type = _(OPERATOR_TYPE_VALUES[instance.activity_type])
        _object = _(instance.request_params)
        return {
            "id": instance.log_id,
            "user": instance.username,
            "app_code": instance.app_code,
            "content": "%s[%s]%s" % (operator_type, _object, name),
            "object": _object,
            "operator_type_value": instance.activity_type,
            "operator_type": operator_type,
            "time": strftime_local(instance.activity_time),
        }

    @classmethod
    def search_log(
            cls, app_code=_undefined, user=_undefined, content=_undefined,
            object_=_undefined, operator_type=_undefined, start_time=_undefined,
            end_time=_undefined, *args, **kwargs
    ):
        qs = UserActivityLog.objects.filter(**kwargs)
        if app_code is not _undefined:
            qs = qs.filter(app_code=app_code)
        if user:
            qs = qs.filter(username__in=user.split(","))
        if operator_type:
            qs = qs.filter(activity_type=operator_type)
        if start_time is not _undefined:
            qs = qs.filter(activity_time__gte=start_time)
        if end_time is not _undefined:
            qs = qs.filter(activity_time__lt=end_time)
        if object_:
            qs = qs.filter(request_params=object_)
        if content:
            qs = qs.filter(activity_name__contains=content)

        return qs
