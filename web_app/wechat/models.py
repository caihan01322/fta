# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import requests
from django.db import models
from django.utils import timezone

from common.log import logger
from enterprise import send_message as send_wechat_message
from fta_solutions_app.models import ApproveCallback, Conf
from project.component import send

rpool = requests.Session()


class Approve(models.Model):
    STATUS = (
        ('WAITING', u"等待"),
        ('TY', u"同意"),
        ('BH', u"驳回")
    )
    obj_id = models.CharField(u"对象ID", max_length=255, blank=True, null=True)
    message = models.TextField(u"审批信息")
    callback_url = models.TextField(u"回调URL", null=True, blank=True)
    status = models.CharField(u"类型", max_length=32, default='WAITING', choices=STATUS)

    approve_users = models.TextField(u"审批人,多个以分号分隔")
    approve_by = models.CharField(u"审批人", max_length=128, blank=True, null=True)
    approve_at = models.DateTimeField(u"审批时间", blank=True, null=True)

    create_at = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_at = models.DateTimeField(u"更新时间", auto_now=True)

    extra = models.TextField(u"其他", blank=True, null=True)

    class Meta:
        verbose_name = u"流程审批"
        verbose_name_plural = u'流程审批'

    def __unicode__(self):
        return '<%s,%s>' % (self.pk, self.message)

    @property
    def to_users(self):
        users = self.approve_users.split(',')
        try:
            super_approver = Conf.get('WECHAT_SUPER_APPROVER')
            super_approver_list = super_approver.split(',') if super_approver else []
            users.extend(super_approver_list)
        except Exception:
            logger.exception(u"WECHAT_SUPER_APPROVER error")
        # 去重, 去空
        users = filter(lambda x: x, set(users))
        return users

    def send_message(self):
        """发送审批单
        """
        content = u"【故障自愈】即将执行 {message},请审核！\n同意请回复: TY {obj_id}\n驳回请回复: BH {obj_id}"
        data = {'message': self.message, 'obj_id': self.pk}
        result = send_wechat_message('|'.join(self.to_users), content.format(**data))
        return result

    def callback(self, action, from_user):
        """回调URL
        """
        try:
            self.status = action
            self.approve_by = from_user
            self.approve_at = timezone.now()
            self.save()

            obj_id = '%s-%s' % (self.id, self.obj_id)
            alarm_id, node_idx = self.obj_id.split('_')
            if self.status == 'TY':
                reason = u"同意（微信审批）"
            else:
                reason = u"驳回（微信审批）"
            approval = 1 if self.status == 'TY' else 0

            app_obj = ApproveCallback(
                obj_id=obj_id,
                alarm_id=int(alarm_id),
                node_idx=int(node_idx),
                approval=approval,
                reason=reason,
                approver=self.approve_by)
            app_obj.save()

            send.wechat(from_user, u"【故障自愈】审批成功")
            # send_wechat_message(from_user, u"【故障自愈】审批成功")
        except Exception as error:
            logger.error('callback: %s' % error)
            send.wechat(from_user, u"【故障自愈】审批失败：%s" % error)
            # send_wechat_message(from_user, u"【故障自愈】审批失败：%s" % error)
