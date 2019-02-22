# -*- coding:utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import datetime
import re

from django import forms
from django.utils import timezone

from common.django_utils import strftime_local
from fta_utils.date_tool import try_parse_datetime

RE_DATE_RANGE = re.compile(r'^\d{4}(\-\d{1,2}){2}(\s+to\s+\d{4}(\-\d{1,2}){2})?$')
DATE_FORMAT = '%Y-%m-%d'


class AlarmInstFilterForm(forms.Form):
    alarm_type = forms.CharField(required=False)
    date = forms.CharField(required=False)
    export = forms.CharField(required=False)  # ip, alarm
    ip = forms.CharField(required=False)
    status = forms.CharField(required=False)
    cc_topo_set = forms.CharField(required=False)
    cc_app_module = forms.CharField(required=False)

    def clean_ip(self):
        return self.cleaned_data['ip'].strip()

    def clean_date(self):
        date = self.cleaned_data['date']
        if not date:
            date = strftime_local(timezone.now(), DATE_FORMAT)

        date_range = re.findall(r'(\d{4}(?:\-\d{1,2}){2})', date)
        if len(date_range) == 1:
            d0 = try_parse_datetime(date_range[0], is_strat=True)
            d1 = try_parse_datetime(date_range[0])
        elif len(date_range) == 2:
            d0 = try_parse_datetime(date_range[0], is_strat=True)
            d1 = try_parse_datetime(date_range[1])
        else:
            # 时间输入异常，则默认为当天
            d0 = d1 = timezone.now()
        begin_date, end_date = sorted([d0, d1])
        return (begin_date,
                end_date - datetime.timedelta(seconds=1))
