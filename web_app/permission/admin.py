# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.contrib import admin

import models


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['cc_id', 'cc_name', 'cc_owner', 'cc_company']
    list_filter = ('cc_company', 'cc_owner')
    search_fields = ['cc_name', 'cc_id', 'cc_owner', 'cc_company']
    editable_fields = ['cc_name', 'cc_id', 'cc_owner', 'cc_company']


@admin.register(models.UserBusiness)
class UserBusinessAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_buss']
    search_fields = ['user', 'default_buss']


@admin.register(models.BusinessGroupMembership)
class BusinessGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['business', 'group']
    search_fields = ['business', 'group']


@admin.register(models.Loignlog)
class LoignlogAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'login_browser', 'login_ip', 'login_host']
    search_fields = ['user__username']
