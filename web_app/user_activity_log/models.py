# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
日志上报到db
"""
import datetime

from django.db import models
from django.utils.translation import ugettext as _


class UserActivityLog(models.Model):
    """"""
    ACTIVITY_TYPE = (
        (1, _('查询')),
        (2, _('创建')),
        (3, _('删除')),
        (4, _('修改')),
    )

    log_id = models.CharField(u'记录的唯一标识', max_length=32, db_index=True, help_text=u'便于记录多表操作的情况')
    app_code = models.CharField(u'应用编码', max_length=32,
                                help_text=u'针对蓝鲸应用访问平台或其它系统，需要记录访问的app_code')
    username = models.CharField(u'用户名称', max_length=32)
    activity_type = models.IntegerField(u'活动类型', choices=ACTIVITY_TYPE, default=1)
    activity_name = models.CharField(u'活动名称', max_length=100, help_text=u'自定义本次操作的名称')

    request_params = models.TextField(u'请求的参数', null=True, blank=True, help_text=u'记录请求的参数')
    before_data = models.TextField(u'活动前的数据', null=True, blank=True, help_text=u'记录活动前的数据，便于数据对账')
    after_data = models.TextField(u'活动后的数据', null=True, blank=True, help_text=u'记录活动后的数据，便于数据对账')
    activity_time = models.DateTimeField(u'活动时间', default=datetime.datetime.now)
    remarks = models.TextField(u'其它信息', null=True, blank=True, help_text=u'其它的信息')

    @property
    def get_show_name(self):
        name = self.activity_name.split('[')[1]
        name = "[%s" % name
        return name

    def __unicode__(self):
        return '%s' % self.log_id

    class Meta:
        verbose_name = u'user_activity_log'
        verbose_name_plural = u'user_activity_log'
        db_table = 'user_activity_log'
