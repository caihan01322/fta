# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.conf.urls import patterns

urlpatterns_advice = patterns(
    'fta_advice.views',

    (r'^(?P<cc_biz_id>\d+)/advice_fta_def_list/$', 'advice_fta_def_list'),
    (r'^(?P<cc_biz_id>\d+)/advice_fta_def/edit/(?P<advice_fta_def_id>\d+)/$', 'edit_advice_fta_def'),
    (r'^(?P<cc_biz_id>\d+)/advice_fta_def/add/(?P<advice_fta_def_id>\d+)/$', 'edit_advice_fta_def'),
    (r'^(?P<cc_biz_id>\d+)/advice_fta_def/save/(?P<advice_fta_def_id>\d+)/$', 'save_advice_fta_def'),
    (r'^(?P<cc_biz_id>\d+)/advice_fta_def/del/$', 'del_advice_fta_def'),
    (r'^(?P<cc_biz_id>\d+)/advice_fta_def/block/$', 'block_advice_fta_def'),
    (r'^(?P<cc_biz_id>\d+)/advice_fta_def/advice_def/(?P<advice_def_id>\d+)/$', 'get_advice_def'),
)
