# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
CONSTANTS for business logic, no need to change for any deployment env.
If it needs to change for different deployment env,
it should be put into settings.
"""
from fta.utils.i18n import lazy_gettext as _

INCIDENT_FUNC = {
    "skip": _("Skip after success"),
    "skip_approve": _("Skip after success, Approve on failure"),
    "pass": _("Skip during processing"),
    "defense": _("Exception defense needs approval"),
    "relevance": _("Collect related events"),
    "trigger": _("Process after convergence"),
    "notify": _("Trigger notification"),
}

INSTANCE_STATUS_DESCRIPTION = {
    "received": _("Received"),
    "waiting": _("In approval"),
    "converging": _("In convergence"),
    "converged": _("Convergence ended"),
    "recovering": _("Processing"),
    "success": _("Success"),
    "almost_success": _("Almost success"),
    "failure": _("Failure"),
    "skipped": _("Skipped"),
    "for_notice": _("Please notice to"),
    "for_reference": _("Please refer to"),
    "authorized": _("Authorized"),
    "unauthorized": _("Unauthorized"),
    "checking": _("Checking"),
    "retrying": _("Retrying"),
    "shield": _("Shield"),
}

INSTANCE_END_STATUS = [
    "success",
    "almost_success",
    "failure",
    "skipped",
    "for_notice",
    "for_reference",
    "authorized",
    "unauthorized",
    "checking",
    "shield",
]

FAILURE_TYPE_CHOICES = (
    ('user_code_failure', _('Processing error (unclassified)')),
    ('framework_code_failure', _('FTA system error')),
    ('timeout', _('Timeout')),
    ('ijobs_failure', _('Job execution error')),
    ('ijobs_create_failure', _('Job creation failed')),
    ('uwork_failure', _('Restart api error')),
    ('gcloud_failure', _('GCloud api error')),
    ('false_alarm', _('False alarm')),
    ('user_abort', _('User termination process')),
)

INSTANCE_FAILURE_STATUS = ["failure"]

INSTANCE_NOT_END_STATUS = list(
    set(INSTANCE_STATUS_DESCRIPTION.keys()) - set(INSTANCE_END_STATUS))

STD_DT_FORMAT = "%Y-%m-%d %H:%M:%S"         # 2015-01-21 10:18:06
SIMPLE_DT_FORMAT = "%H:%M:%S"               # 10:18:06
MINI_DT_FORMAT = "%H:%M"                    # 10:18
STD_ARROW_FORMAT = "YYYY-MM-DD HH:mm:ss"    # 2015-01-21 10:18:06
SIMPLE_ARROW_FORMAT = "HH:mm:ss"            # 10:18:06
MINI_ARROW_FORMAT = "HH:mm"                 # 10:18

MARK_VALUE = "--mark--"
WECHAT_BREAKS = u"\n"
SMS_BREAKS = u"\n"
MAIL_BREAKS = u"<br/>"

# beanstalkd job body大小
JOB_BUCKET = 65535

# Cache默认时间, 24小时
CACHE_TIMEOUT = 60 * 60 * 24

# poll_alarm最大运行时间, 2分钟
JOB_EXCEUTE_TIMEOUT = 60 * 2

# 敏感词, 脱敏使用
SENSITIVE_WORDS = ['app_secret', 'password']

# 错误码
ERROR_01_POLL = "3001010"
ERROR_01_MATCH = "3001020"
ERROR_01_COLLECT = "3001030"
ERROR_01_CONERGE = "3001040"
ERROR_01_API = "3001050"

ERROR_02_ESB = "3002010"
ERROR_02_ESB_MAIL = "3002011"
ERROR_02_ESB_SMS = "3002012"
ERROR_02_ESB_WECHAT = "3002013"
ERROR_02_ESB = "3002010"
ERROR_02_ESB = "3002010"
ERROR_02_THIRD = "3002020"
ERROR_02_MONITOR = "3002030"

ERROR_03_REDIS = "3003010"
ERROR_03_BEANSTALK = "3003020"

try:
    from project import constants
    locals().update(constants.__dict__)
except BaseException:
    print u'!!!!! WARNING: CAN NOT FIND USER SETTINGS !!!!!'
    import sys
    sys.exit(0)
