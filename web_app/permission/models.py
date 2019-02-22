# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone

from project.conf.user import BkUser as User


class Business(models.Model):
    cc_id = models.IntegerField(unique=True)
    cc_name = models.CharField(max_length=100)
    cc_owner = models.CharField(max_length=100)
    cc_company = models.CharField(max_length=100)

    groups = models.ManyToManyField(
        Group,
        through='BusinessGroupMembership'
    )

    class Meta:
        verbose_name = u"Business"
        verbose_name_plural = u"Business"
        permissions = (
            ("view_business", "Can view business"),
            ("manage_business", "Can manage business"),
        )

    def __unicode__(self):
        return u"%s_%s" % (self.cc_id, self.cc_name)


class UserBusiness(models.Model):
    """
    用户默认业务表
    """
    user = models.CharField(u"user", max_length=255, unique=True)
    default_buss = models.IntegerField(u"business")

    def __unicode__(self):
        return u'%s-%s' % (self.user, self.default_buss)

    class Meta:
        verbose_name = u"UserBusiness"
        verbose_name_plural = u"UserBusiness"


class BusinessGroupMembership(models.Model):
    business = models.ForeignKey(Business)
    group = models.ForeignKey(Group)

    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = u"BusinessGroupMembership"
        verbose_name_plural = u"BusinessGroupMembership"
        unique_together = ('business', 'group')

    def __unicode__(self):
        return u"B%s:G%s" % (self.business_id, self.group_id)


class LoginLogManager(models.Manager):
    """
    User login log manager
    """

    def record_login(self, _user, _login_browser, _login_ip, host):
        try:
            self.model(
                user=_user,
                login_browser=_login_browser,
                login_ip=_login_ip,
                login_host=host,
                login_time=timezone.now(),
            ).save()
            return (True, u"success")
        except Exception:
            return (False, u"error")


class Loignlog(models.Model):
    """
    User login log
    """

    user = models.ForeignKey(User, verbose_name=u"user")
    login_time = models.DateTimeField(u"login time")
    login_browser = models.CharField(u"login browser", max_length=200, blank=True, null=True)
    login_ip = models.CharField(u"login ip", max_length=50, blank=True, null=True)
    login_host = models.CharField(u"login host", max_length=100, blank=True, null=True)

    objects = LoginLogManager()

    class Meta:
        verbose_name = u"Login Log"
        verbose_name_plural = u"Login Log"
