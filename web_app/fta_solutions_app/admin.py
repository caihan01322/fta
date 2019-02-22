# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.contrib import admin
from django.utils.translation import ugettext as _

from fta_solutions_app import models
from user_activity_log.models import UserActivityLog


class QcloudUserActivityLog(admin.ModelAdmin):
    list_display = ('id', 'app_code', 'activity_name', 'request_params', 'activity_time',)
    search_fields = ('id', 'app_code', 'activity_name', 'request_params', 'activity_time',)


admin.site.register(UserActivityLog, QcloudUserActivityLog)


class QcloudOwnerInfoAdmin(admin.ModelAdmin):
    """docstring for QcloudOwnerInfoAdmin"""
    list_display = ('owner_uin', 'qcloud_app_id')
    search_fields = ('owner_uin', 'qcloud_app_id')


class AlarmDefAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_enabled', 'cc_biz_id', 'alarm_type', 'source_type', 'create_time', 'update_time',)
    search_fields = ('id', 'cc_biz_id', 'alarm_type', 'tnm_attr_id', 'module', 'topo_set', 'title', 'source_type',)
    list_filter = ('alarm_type', 'cc_biz_id', 'is_enabled', 'source_type')


class AlarmTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'cc_biz_id', 'source_type', 'alarm_type', 'pattern', 'match_mode', 'description',)
    search_fields = ('cc_biz_id', 'source_type', 'alarm_type', 'pattern', 'description',)
    list_filter = ('cc_biz_id', 'source_type', 'alarm_type', 'pattern', 'description',)


class SolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cc_biz_id', 'solution_type', 'title', 'creator', 'codename',)
    list_filter = ('solution_type', 'cc_biz_id', 'codename',)


class DataChanglogAdmin(admin.ModelAdmin):
    list_display = ('change_model', 'change_id', 'change_type', 'username', 'change_time')
    search_fields = ('change_model', 'change_id', 'username')
    list_filter = ('change_type', 'change_model', 'change_time', 'username')


class AlarmInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'source_time', 'end_time', 'cc_biz_id', 'alarm_type',
        'ip', 'status', 'solution_type', 'priority')
    list_filter = ('source_time', 'cc_biz_id', 'status', 'alarm_type', 'solution_type',)
    readonly_fields = ['begin_time']

    actions = ['change_status_to_ref', 'change_status_to_failure']

    def change_status_to_ref(modeladmin, request, queryset):
        queryset.update(status='for_reference')

    change_status_to_ref.short_description = _(u"将状态置为<请参考>")

    def change_status_to_failure(modeladmin, request, queryset):
        queryset.update(status='failure')

    change_status_to_failure.short_description = _(u"将状态置为<失败>，这样INC可以尽快开始人工处理")


class AlarmInstanceBackupAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'source_time', 'end_time', 'cc_biz_id', 'alarm_type',
        'ip', 'status', 'solution_type', 'priority',
    )
    list_filter = ('source_time', 'cc_biz_id', 'status', 'alarm_type', 'solution_type')
    readonly_fields = ['begin_time']

    actions = ['change_status_to_ref', 'change_status_to_failure']

    def change_status_to_ref(modeladmin, request, queryset):
        queryset.update(status='for_reference')

    change_status_to_ref.short_description = _(u"将状态置为<请参考>")

    def change_status_to_failure(modeladmin, request, queryset):
        queryset.update(status='failure')

    change_status_to_failure.short_description = _(u"将状态置为<失败>，这样INC可以尽快开始人工处理")


class AlarmInstanceArchiveAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'date', 'sub_count', 'cc_biz_id', "biz_team",
        "is_success", "alarm_type", "failure_type",
        "solution_type",
    )
    list_filter = ('date', "biz_team", "is_success", "alarm_type", "failure_type", "solution_type", "is_off_time")


class OutOfScopeArchiveAdmin(admin.ModelAdmin):
    list_display = (
        "id", "created_on", "updated_on", "status", "cc_biz_id",
        "alarm_type", "cc_module", "cc_set_name", "sub_count",
    )
    list_filter = ("created_on", "updated_on", "cc_biz_id", "alarm_type", "status",)


class IgnoreAlarmAdmin(admin.ModelAdmin):
    list_display = ("cc_biz_id", "alarm_type", "attr_id", "cc_module", "note")


class KPICacheAdmin(admin.ModelAdmin):
    list_display = ("date", "cc_biz_id", "kpi_type", "tnm_total", "tnm_covered", "tnm_success")
    list_filter = ("date", "cc_biz_id", "kpi_type")


class AlarmInstanceLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'alarm_instance', 'time', 'level', 'step_name', 'content',)
    list_filter = ('time', 'level')
    readonly_fields = ('alarm_instance',)


class IncidentAlarmInline(admin.StackedInline):
    model = models.IncidentAlarm
    readonly_fields = ['alarm']


class IncidentAdmin(admin.ModelAdmin):
    readonly_fields = ['incident_def']
    list_display = ('id', 'cc_biz_id', 'begin_time', 'end_time', 'description',)
    list_filter = ('cc_biz_id', 'incident_type', 'is_visible')


class IncRelatedAlarmAdmin(admin.ModelAdmin):
    list_display = ('orderno', 'product_id', 'archive', 'trigger_start_time', 'content')
    search_fields = ('orderno',)
    list_filter = ('archive',)


class IncOrderAdmin(admin.ModelAdmin):
    list_display = ('inc_orderno', 'alarm_id', 'push_type')
    search_fields = ('inc_orderno', 'alarm_id')
    list_filter = ('push_type',)


class IncidentDefAdmin(admin.ModelAdmin):
    list_display = ('id', 'codename', 'description', 'priority', 'is_enabled', 'cc_biz_id')
    ordering = ('id',)


class WorldAdmin(admin.ModelAdmin):
    list_filter = ('cc_biz_id',)


class AdviceDefAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'codename', 'is_enabled', 'subject_type',
        'check_type', 'check_sub_type', 'interval',
        'threshold', 'description', 'advice_type', 'advice'
    )
    list_filter = ('cc_biz_id', 'check_type', 'check_sub_type',)


class AdviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'advice_def', 'cc_biz_id', 'subject', 'create_time', 'status',)
    # 'alarm_start_time', 'alarm_end_time', 'alarm_num')
    list_filter = ('cc_biz_id', 'create_time', 'status')


class AdviceFtaDef(admin.ModelAdmin):
    list_display = ('id', 'is_enabled', 'cc_biz_id', 'advice_def_id', 'solution_id')
    search_fields = ('cc_biz_id', 'topo_set', 'title')
    list_filter = ('cc_biz_id', 'is_enabled', 'advice_def_id', 'solution_id')


class BizConfAdmin(admin.ModelAdmin):
    list_display = ('cc_biz_id', 'tnm_servicegroup_id', 'responsible')
    list_filter = ('cc_biz_id', 'tnm_servicegroup_id')


class ContextAdmin(admin.ModelAdmin):
    list_display = ('key', 'field', 'value', 'updated_on', 'created_on')


class ConfAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'description')


class EagleEyeAdmin(admin.ModelAdmin):
    list_display = ('incident_id', 'eagle_eye_orderno')
    search_fields = ('incident_id', 'eagle_eye_orderno')


class AlarmApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'source_type', 'cc_biz_id', 'app_name',
        'app_id', 'exception_max_num', 'is_enabled',
        'is_deleted', 'create_time',
    )
    search_fields = (
        'id', 'source_type', 'cc_biz_id', 'app_name',
        'create_user', 'update_user',
    )
    list_filter = ('source_type', 'cc_biz_id')


admin.site.register(models.QcloudOwnerInfo, QcloudOwnerInfoAdmin)
admin.site.register(models.AlarmDef, AlarmDefAdmin)
admin.site.register(models.AlarmType, AlarmTypeAdmin)
admin.site.register(models.Solution, SolutionAdmin)
admin.site.register(models.AlarmInstance, AlarmInstanceAdmin)
admin.site.register(models.AlarmInstanceBackup, AlarmInstanceBackupAdmin)
admin.site.register(models.AlarmInstanceLog, AlarmInstanceLogAdmin)

admin.site.register(models.Conf, ConfAdmin)
admin.site.register(models.Context, ContextAdmin)
admin.site.register(models.DataChanglog, DataChanglogAdmin)
admin.site.register(models.IncidentDef, IncidentDefAdmin)
admin.site.register(models.Incident, IncidentAdmin)
admin.site.register(models.IncRelatedAlarm, IncRelatedAlarmAdmin)
admin.site.register(models.IncOrder, IncOrderAdmin)
admin.site.register(models.IncidentAlarm)
admin.site.register(models.BizConf, BizConfAdmin)
admin.site.register(models.World, WorldAdmin)
admin.site.register(models.Advice, AdviceAdmin)
admin.site.register(models.AdviceDef, AdviceDefAdmin)
admin.site.register(models.AdviceFtaDef, AdviceFtaDef)

admin.site.register(models.AlarmInstanceArchive, AlarmInstanceArchiveAdmin)
admin.site.register(models.OutOfScopeArchive, OutOfScopeArchiveAdmin)
admin.site.register(models.IgnoreAlarm, IgnoreAlarmAdmin)
admin.site.register(models.KPICache, KPICacheAdmin)
admin.site.register(models.EagleEye, EagleEyeAdmin)
admin.site.register(models.ApproveCallback)
admin.site.register(models.UserBiz)
admin.site.register(models.UserAction)

admin.site.register(models.AlarmApplication, AlarmApplicationAdmin)
