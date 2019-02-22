# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from django import forms
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from .django_conf import APP_CODE, DATA_LIMIT_SIZE, DEFAULT_ACTIVITY_TYPE
from .utils import get_uuid, data_truncation


class CustomForm(forms.Form):

    def error_message(self, errors):
        error_content = []
        for k, v in sorted(errors.items()):
            error_content.append('%s: %s' % (k, force_unicode(v[0])))
        return ';'.join(error_content)


class CustomField(forms.Field):
    """进行参数类型校验的Field"""

    def __init__(self, *args, **kwargs):
        super(CustomField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return ''
        if not isinstance(value, basestring):
            try:
                value = json.dumps(value)
            except Exception:
                # 处理非json化的数据
                value = '%s' % value
        return value


class LogFieldHandler(CustomForm):
    """处理请求参数"""
    log_id = forms.CharField(label=_(u'记录唯一标识'), required=False)
    app_code = forms.CharField(label=_(u'应用编码'), required=False)
    username = forms.CharField(label=_(u'用户名称'), required=True)
    activity_type = forms.IntegerField(label=_(u'活动类型'), required=False)
    activity_name = forms.CharField(label=_(u'活动名称'), required=True)
    request_params = CustomField(label=_(u'请求参数'), required=False)
    before_data = CustomField(label=_(u'活动前的数据'), required=False)
    after_data = CustomField(label=_(u'活动后的数据'), required=False)
    remarks = CustomField(label=_(u'其它信息'), required=False)
    data_limit_size = forms.IntegerField(label=_(u'存储数据大小'), required=False)

    def clean(self):
        data = self.cleaned_data
        data_limit_size = data['data_limit_size'] or DATA_LIMIT_SIZE
        return {
            'log_id': data['log_id'] or get_uuid(),
            'username': data['username'],
            'app_code': data['app_code'] or APP_CODE,
            'activity_type': data['activity_type'] or DEFAULT_ACTIVITY_TYPE,
            'activity_name': data['activity_name'],
            'request_params': data['request_params'],
            'before_data': data_truncation(data['before_data'], data_limit_size=data_limit_size),
            'after_data': data_truncation(data['after_data'], data_limit_size=data_limit_size),
            'remarks': data_truncation(data['remarks'], data_limit_size=data_limit_size)
        }
