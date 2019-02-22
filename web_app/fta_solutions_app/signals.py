# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import logging

from django.core import serializers
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from fta_solutions_app.activity_log import ActivityLogClient, OBJECT_TYPE
from fta_solutions_app.models import Advice
from fta_solutions_app.models import AdviceDef
from fta_solutions_app.models import AdviceFtaDef
from fta_solutions_app.models import AlarmApplication
from fta_solutions_app.models import AlarmDef
from fta_solutions_app.models import AlarmType
from fta_solutions_app.models import BizConf
from fta_solutions_app.models import Conf
from fta_solutions_app.models import DataChanglog
from fta_solutions_app.models import IncidentDef
from fta_solutions_app.models import Solution
from fta_utils.request_middlewares import get_request
from fta_utils.utils import func_catch

logger = logging.getLogger(__name__)

# important!
# 使用requestprovider中间件来获取request对象

# 定义需要记录的model
MODELS_TO_LOG = (
    DataChanglog, AlarmDef, Solution, Conf, BizConf,
    IncidentDef, AdviceDef, Advice, AdviceFtaDef,
    AlarmApplication,
)


# 所有的model都被connect，然后再被过滤
@receiver(post_save)
def post_save_models(sender, instance, created, **kwargs):
    if isinstance(instance, MODELS_TO_LOG) and not (isinstance(instance, DataChanglog) and created):
        # DataChangelog的创建不能触发signal，否则死循环
        change_type = 'create' if created else 'update'
        save_change_log(sender, change_type, instance)


# 所有的model都被connect，然后再被过滤
@receiver(post_delete)
def post_delete_models(sender, instance, **kwargs):
    if isinstance(instance, MODELS_TO_LOG):
        change_type = 'delete'
        save_change_log(sender, change_type, instance)


def save_change_log(sender, change_type, instance):
    change_model = unicode(sender.__name__)
    data = serializers.serialize("json", [instance, ], ensure_ascii=False)

    try:
        request = get_request()
        username = request.user.username
    except Exception:
        username = "*SYSTEM*"  # celery backend process

    DataChanglog.objects.create(
        change_model=change_model,
        change_id=instance.id,
        change_type=change_type,
        new=data,
        username=username,
    )


class ModelActivityLogger(object):

    def get_cc_biz_id(self, default=None):
        cc_biz_id = default or self.instance.cc_biz_id
        if cc_biz_id != 0 or not self.request:
            return cc_biz_id
        resolver_match = self.request.resolver_match
        if resolver_match:
            cc_biz_id = resolver_match.kwargs.get("cc_biz_id", cc_biz_id)
        return cc_biz_id

    def check_AlarmDef(self, params):
        if self.instance.is_deleted:
            self.operator_type = "deletion"
        params.update({"app_code": self.get_cc_biz_id(), })
        params["content"] = self.get_content(
            instance=self.instance, operator_type=self.operator_type,
            description=self.instance.description,
            **params
        )
        return params

    def check_Solution(self, params):
        if self.instance.is_deleted:
            self.operator_type = "deletion"
        params.update({
            "app_code": self.get_cc_biz_id(),
        })
        params["content"] = self.get_content(
            instance=self.instance, operator_type=self.operator_type,
            description=self.instance.title,
            **params
        )
        return params

    def check_IncidentDef(self, params):
        params.update({
            "app_code": self.get_cc_biz_id(),
        })
        params["content"] = self.get_content(
            instance=self.instance, operator_type=self.operator_type,
            description=self.instance.description,
            **params
        )
        return params

    def check_AdviceFtaDef(self, params):
        if self.instance.is_deleted:
            self.operator_type = "deletion"
        params.update({
            "app_code": self.get_cc_biz_id(),
        })
        params["content"] = self.get_content(
            instance=self.instance, operator_type=self.operator_type,
            description=self.instance.description,
            **params
        )
        return params

    def check_AlarmType(self, params):
        params.update({
            "app_code": self.get_cc_biz_id(),
            "content": self.get_content(
                instance=self.instance, operator_type=self.operator_type,
                description=self.instance.description,
                **params
            ),
        })
        return params

    def check_AlarmApplication(self, params):
        if self.instance.is_deleted:
            self.operator_type = "deletion"
        params.update({
            "app_code": self.get_cc_biz_id(),
        })
        params["content"] = self.get_content(
            instance=self.instance, operator_type=self.operator_type,
            description=self.instance.app_name,
            **params
        )
        return params

    MODEL_MAPPINGS = {
        AlarmDef: check_AlarmDef,
        Solution: check_Solution,
        IncidentDef: check_IncidentDef,
        AdviceFtaDef: check_AdviceFtaDef,
        AlarmType: check_AlarmType,
        AlarmApplication: check_AlarmApplication,
    }

    def __init__(self, instance, operator_type):
        self.request = get_request()
        self.user = self.request and self.request.user
        self.instance = instance
        self.operator_type = operator_type

    def get_username(self):
        if not self.user:
            return "*NONAME*"
        try:
            username = self.user.get_short_name()
            if username:
                return username
        except Exception:
            pass

        try:
            username = self.user.username
            if username:
                return username
        except Exception:
            pass

        return "*SYSTEM*"

    @classmethod
    def get_content(cls, instance, operator_type, object_=None, description=None, instance_pk=None, **kwargs):
        operator_mappings = {
            "addition": _(u"新增"),
            "modification": _(u"修改"),
            "deletion": _(u"删除"),
        }
        return u"{operator}[{instance_pk}]".format(
            operator=operator_mappings.get(operator_type, _(u"操作")),
            object=object_, description=description or "",
            instance_pk=instance.pk if instance else instance_pk,
        )

    def log(self):
        instance_class = self.instance.__class__
        check_method = self.MODEL_MAPPINGS.get(instance_class)
        if not check_method:
            return

        params = check_method(self, {
            # "object_": instance_class.__name__,
            "app_code": None,
            "user": self.get_username(),
            "object_": OBJECT_TYPE[instance_class.__name__],
        })
        if self.operator_type == "deletion":
            log_method = ActivityLogClient.log_deletion
        elif self.operator_type == "addition":
            log_method = ActivityLogClient.log_addition
        elif self.operator_type == "modification":
            log_method = ActivityLogClient.log_modification
        log_method(**params)


@receiver(post_save)
@func_catch(logger.error)
def log_model_activity_create_and_modify(sender, instance, created, **kwargs):
    if not isinstance(instance, tuple(ModelActivityLogger.MODEL_MAPPINGS.keys()), ):
        return

    if created:
        operator_type = "addition"
    else:
        operator_type = "modification"
    activity_logger = ModelActivityLogger(instance, operator_type)
    activity_logger.log()


@receiver(post_delete)
@func_catch(logger.error)
def log_model_activity_delete(sender, instance, **kwargs):
    if not isinstance(instance, tuple(ModelActivityLogger.MODEL_MAPPINGS.keys()), ):
        return

    activity_logger = ModelActivityLogger(instance, "deletion")
    activity_logger.log()
