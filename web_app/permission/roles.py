# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.utils.translation import ugettext as _

MAINTAINERS = 'Maintainers'
PRODUCTPM = 'ProductPm'
COOPERATION = 'Cooperation'
OWNER = 'Owner'

# 只要 开发商 和 运维才有访问权限
ALL_ROLES = [MAINTAINERS, OWNER]

ADMIN_ROLES = [MAINTAINERS, OWNER]

CC_ROLES = [
    ("Maintainers", _(u"业务运维")),
    ("ProductPm", _(u"产品接口人")),
]

# 默认通知分组
CC_PERSON_GROUP = [
    {"value": "Maintainers", "text": _(u"业务运维")},
    {"value": "ProductPm", "text": _(u"产品接口人")},
]

DEFAULT_CC_NOTIFY_SET = (
    "Maintainers",
)

# CC角色分组对应的人员信息返回的key
CC_ROLES_OF_GROUP = {
    'Maintainers': ['MaintainersOpenid'],
    'ProductPm': ['ProductPmOpenid'],
}
