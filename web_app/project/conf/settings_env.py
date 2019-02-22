# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
请不要修改该文件
"""
import os

from django.conf.urls import patterns
from django.utils.translation import ugettext_lazy as _

# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# APP_ID不用修改
APP_ID = 'bk_fta_solutions'
# APP_TOKEN需要到官方网站的admin中获取 默认访问http://{BK_PAAS_HOST}/admin/app/app/ 找到名为"故障自愈"的记录，查看详情获取Token字段值
APP_TOKEN = ''
# 蓝鲸智云开发者中心的域名，形如：http://paas.bking.com:80
BK_PAAS_HOST = ""
# 蓝鲸智云作业平台的域名，形如：http://job.bking.com:80
BK_JOB_HOST = ""
# 蓝鲸智云配置平台的域名，形如：http://cmdb.bking.com:80
BK_CC_HOST = ""
# 缓存时间
CACHE_TIME = 5

# ==============================================================================
# 应用运行环境配置信息
# ==============================================================================
ENVIRONMENT = os.environ.get('BK_ENV', 'development')

# 应用基本信息从环境变量中获取，未设置环境变量(如：本地开发)时，则用用户在文件开头的填写的值
APP_ID = os.environ.get('APP_ID', APP_ID)
APP_TOKEN = os.environ.get('APP_TOKEN', APP_TOKEN)
BK_PAAS_HOST = os.environ.get('BK_PAAS_HOST', BK_PAAS_HOST)
BK_PAAS_INNER_HOST = os.environ.get('BK_PAAS_INNER_HOST', BK_PAAS_HOST)
BK_CC_HOST = os.environ.get('BK_CC_HOST', BK_CC_HOST)
BK_JOB_HOST = os.environ.get('BK_JOB_HOST', BK_JOB_HOST)  # 需要根据用户的需求

# 应用访问路径
SITE_URL = '/'
# 运行模式， DEVELOP(开发模式)， TEST(测试模式)， PRODUCT(正式模式)
RUN_MODE = 'DEVELOP'
if ENVIRONMENT.endswith('production'):
    RUN_MODE = 'PRODUCT'
    DEBUG = False
    SITE_URL = '/o/%s/' % APP_ID
elif ENVIRONMENT.endswith('testing'):
    RUN_MODE = 'TEST'
    DEBUG = False
    SITE_URL = '/t/%s/' % APP_ID
else:
    RUN_MODE = 'DEVELOP'
    DEBUG = True
TEMPLATE_DEBUG = DEBUG

# 按环境加载配置文件
ENVIRONMENT = os.environ.get("BK_ENV", "development")
conf_module = "project.conf.settings_%s" % ENVIRONMENT

APP_CODE = APP_ID
APP_SECRET_KEY = SECRET_KEY = APP_TOKEN
NO_CIPHER_SECRET = True
REMOTE_STATIC_URL = 'http://magicbox.bk.tencent.com/static_api/'
# ==============================================================================
# 中间件
# ==============================================================================
MIDDLEWARE_CLASSES_ENV = (
    # 登录鉴权中间件
    'account.middlewares.LoginMiddleware',
)
INSTALLED_APPS_ENV = (
    'account',
    'wechat',
    'fta_admin',
)

# ===============================================================================
# Authentication
# ===============================================================================
AUTH_USER_MODEL = 'account.BkUser'
AUTHENTICATION_BACKENDS = (
    'account.backends.BkBackend',
    'wechat.auth.backends.WeChatBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
LOGIN_URL = "%s/login/?app_id=%s" % (BK_PAAS_HOST, APP_ID)
LOGOUT_URL = '%saccount/logout/' % SITE_URL
LOGIN_REDIRECT_URL = SITE_URL
REDIRECT_FIELD_NAME = "c_url"
# 验证登录的cookie名
BK_COOKIE_NAME = 'bk_token'
# 数据库初始化 管理员列表
ADMIN_USERNAME_LIST = ['admin']
ACCOUNT_URL = 'account.urls'
# ==============================================================================
# logging
# ==============================================================================
# 社区版日志目录
BK_LOG_DIR = os.environ.get('BK_LOG_DIR', '/data/paas/apps/logs/')

# ==============================================================================
# ESB 相关
# ==============================================================================
# esb 模块路径
ESB_MODULE = 'project.blueking.component'
SETTINGS_JS_NAME = 'settings_open.js'
NO_BIZ_HTML_NAME = 'no_biz_open.html'

# ESB 中注册的后台API地址前缀
FTA_API_PREFIX = '%s/api/c/compapi/fta/event/' % BK_PAAS_HOST
FTA_CALL_BACK_URL = '%s/api/c/compapi/fta/callback/' % BK_PAAS_HOST
FTA_STATUS_URL = '%s/api/c/compapi/fta/status/process/' % BK_PAAS_HOST

# ==============================================================================
# 作业平台相关常量
# ==============================================================================
# 磁盘清理作业
CLEAN_TASK_ID = '4'
# 获取占用内存最多的Top10进程
TOP_MEM_TASK_ID = '3'
# 获取占用CPU最多的Top10进程
TOP_CPU_TASK_ID = '2'
# 跨业务作业集合
ALL_BIZ_TASKS = [CLEAN_TASK_ID, TOP_MEM_TASK_ID, TOP_CPU_TASK_ID]
# 跨业务作业执行时指定的业务id
ALL_BIZ_APP_ID = '77770001'
# 磁盘清理的作业脚本参数
CLEAN_TASK_PARAM = {
    "app_id": "77770001",
    "task_id": "4",
    "parms": "",
    "parms0": "%s",
    "argv": "on",
    "retry_time": "",
    "retry_count": "",
    "steps": "1",
    "operator": "100"
}

# ==============================================================================
# 标准运维常量
# ==============================================================================
# 社区版、企业版迁移到新版后，已经废弃
GCLOUD_ENDPOINT = "%s/api/c/self-service-api/" % BK_PAAS_HOST
# 需要修改为新的链接
if RUN_MODE == 'PRODUCT':
    GCLOUD_DETAIL_ENDPOINT = "%s/o/bk_sops/" % BK_PAAS_HOST
else:
    GCLOUD_DETAIL_ENDPOINT = "%s/t/bk_sops/" % BK_PAAS_HOST

# ==============================================================================
# 版本配置项 相关
# ==============================================================================
DEFAULT_OPEN_SOURCE_TYPE = ['']

# 初始化开负责人
FTA_ADMIN_LIST = ['admin']
FTA_BOSS_LIST = []

# url 配置项
URL_ENV = patterns(
    '',
)
OP_URL_PREFIX = ''

# 是否启用celery任务
IS_USE_CELERY = False
CELERY_IMPORTS_ENV = ()

# 管理员是否可以管理所有业务
IS_ADMIN_OPERATE_ALL_BIZ = True

# ==================
# 微信企业号配置项
# ==================
# APP微信端地址(外网可访问)
WECHAT_APP_URL = '%s%swechat/' % (BK_PAAS_HOST, SITE_URL)

# APP微信端静态资源地址(外网可访问)
WECHAT_STATIC_URL = '%s%sstatic/wechat/' % (BK_PAAS_HOST, SITE_URL)

# 微信审批相关的配置信息
WECHAT_CONFIG = [
    {
        'name': 'WECHAT_TOKEN',
        'value': '',
        'description': u"TOKEN"
    },
    {
        'name': 'WECHAT_ENCODING_AES_KEY',
        'value': '',
        'description': u"EncodingAESKey"
    },
    {
        'name': 'WECHAT_CORPID',
        'value': '',
        'description': _(u"微信企业号ID")
    },
    {
        'name': 'WECHAT_SECRET',
        'value': '',
        'description': _(u"微信企业号Secret")
    },
    {
        'name': 'WECHAT_AGENT_ID',
        'value': '',
        'description': _(u"发送消息的AGENT_ID")
    },
    {
        'name': 'WECHAT_API_TOKEN',
        'value': '',
        'description': _(u"创建审批API_TOKEN")
    }
]

# ==================
# 版本配置项
# ==================
HTML_TITLE = _(u"蓝鲸智云故障自愈")
IS_FTA_HELPER = True

# CC_NEW_APP_URL = '%s/#/organization/biz' % BK_CC_HOST
CC_NEW_APP_URL = '%s/#/business' % BK_CC_HOST

SOLUTION_TYPE_IN_ENV = (
    ('gcloud', _(u'标准运维流程')),
    ('http_callback', _(u'HTTP回调')),
)
FAILURE_TYPE_IN_ENV = (
    ('gcloud_failure', _(u'标准运维调用出错')),
    ('http_callback', _(u'回调失败')),
)
DIY_TYPE_IN_ENV = (
    ('diy', _(u'组合套餐')),
    ('get_bak_ip', _(u'获取故障机备机')),
    ('notice', _(u'审批')),
    ('notice_only', _(u'通知')),
    ('sleep', _(u'暂停等待')),
    ('convergence', _(u'自定义收敛防御')),
)
INCIDENT_CHN_IN_ENV = {
    "defense": _(u"异常防御需审批"),
}

SOURCE_TYPE_IN_ENV = (
    ('CUSTOM', _(u'自定义监控')),
    ('ICINGA2', _(u"ICINGA2监控")),
    ('AWS', 'AWS'),
    ('EMAIL', _(u'邮件解析')),
)

SOURCE_TYPE_PAGES_IN_ENV = {
    'icinga2': 'ICINGA2',
    'aws': 'AWS',
    'email': 'EMAIL',
}
