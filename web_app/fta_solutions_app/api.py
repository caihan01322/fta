# -*- coding:utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
提供自愈数据的 restful 接口
"""

from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization  # DjangoAuthorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS, ALL
from tastypie.validation import Validation

from fta_solutions_app import models


class FTAAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        """
        由中间件做权限管理，这里不再处理一遍
        """
        return True

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username


class GlobalResourceMixin(object):
    global_methods = set(["GET", ])
    global_exclude_filters = {
        "cc_biz_id__exact": 0,
    }
    global_queryset = None

    def append_global_object_list(self, request, applicable_filters):
        applicable_filters.update(self.global_exclude_filters)
        if self.global_queryset:
            object_list = self.global_queryset
        else:
            object_list = self.get_object_list(request)
        return object_list.filter(**applicable_filters)

    def apply_filters(self, request, applicable_filters):
        object_list = super(GlobalResourceMixin, self).apply_filters(
            request, applicable_filters,
        ).filter(**applicable_filters)
        if request.method in self.global_methods:
            object_list = object_list | self.append_global_object_list(
                request, applicable_filters,
            )
        return object_list


class JsonSchemaValidation(Validation):

    def __init__(self, schema, *args, **kwargs):
        self.schema = schema

    def is_valid(self, bundle, request=None):
        from jsonschema import Draft4Validator, ValidationError
        if not bundle.data:
            return {'__all__': 'Not quite what I had in mind.'}

        validator = Draft4Validator(self.schema)
        try:
            validator.validate(bundle.data)
        except ValidationError as err:
            return {'__all__': err.message}


class AlarmDefResource(ModelResource):

    class Meta:
        queryset = models.AlarmDef.objects.all()
        authorization = Authorization()

        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }


class AlarmTypeResource(GlobalResourceMixin, ModelResource):

    class Meta:
        queryset = models.AlarmType.objects.all().filter(is_hidden=False)
        authorization = Authorization()
        excludes = ["exclude"]
        always_return_data = True
        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }
        validation = JsonSchemaValidation({
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "minLength": 1,
                },
                "pattern": {
                    "type": "string",
                    "minLength": 1,
                },
                "cc_biz_id": {
                    "type": ["number", "string"],
                    "minimum": 0,
                    "exclusiveMaximum": True,
                }
            },
            "required": ["cc_biz_id", "pattern", "description"],
        })


class AlarmApplicationResource(ModelResource):

    class Meta:
        queryset = models.AlarmApplication.objects.all().filter(is_deleted=False)
        authorization = Authorization()

        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }


class SolutionResource(ModelResource):

    class Meta:
        queryset = models.Solution.objects.all()
        authorization = Authorization()
        authentication = FTAAuthentication()
        always_return_data = True
        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }


class WorldResource(ModelResource):

    class Meta:
        queryset = models.World.objects.all()
        authorization = Authorization()

        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }


class AlarmInstanceResource(ModelResource):
    alarm_def_id = fields.IntegerField(attribute="alarm_def_id")
    alarm_def = fields.ForeignKey(AlarmDefResource, 'alarm_def')

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(AlarmInstanceResource, self).apply_filters(request, applicable_filters)
        tnm_alarm_ids = request.GET.get('tnm_alarm_ids', None)
        filters = {}
        if tnm_alarm_ids:
            tnm_alarm_ids = tnm_alarm_ids.split(',')
            filters.update(dict(source_id__in=tnm_alarm_ids))
        return base_object_list.filter(**filters).distinct()

    class Meta:
        queryset = models.AlarmInstance.objects.all()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            "id": ALL,
            "source_id": ALL,
            "ip": ALL,
            "cc_biz_id": ALL,
            "alarm_def": ALL_WITH_RELATIONS,
            "begin_time": ALL_WITH_RELATIONS,
        }


class IncidentDefResource(ModelResource):

    class Meta:
        queryset = models.IncidentDef.objects.all()
        authorization = Authorization()
        filtering = {
            "is_enabled": ALL,
            "cc_biz_id": ALL,
        }


class IncidentResource(ModelResource):
    incident_def = fields.ForeignKey(
        IncidentDefResource, 'incident_def', full=True)

    class Meta:
        queryset = models.Incident.objects.all()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'dimension': ALL,
            'begin_time': ALL,
            'end_time': ALL,
            'last_check_time': ALL,
            "cc_biz_id": ALL,
        }


class IncidentAlarmResource(ModelResource):
    incident = fields.ForeignKey(IncidentResource, 'incident')
    alarm = fields.ForeignKey(AlarmInstanceResource, 'alarm')

    class Meta:
        queryset = models.IncidentAlarm.objects.all()
        authorization = Authorization()
        filtering = {
            'incident': ALL_WITH_RELATIONS,
            "cc_biz_id": ALL,
        }


class BizConfResource(ModelResource):

    class Meta:
        queryset = models.BizConf.objects.all()
        authorization = Authorization()

        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }


class AdviceResource(ModelResource):

    class Meta:
        queryset = models.Advice.objects.all()
        authorization = Authorization()

        filtering = {
            "id": ALL,
            "cc_biz_id": ALL,
        }
