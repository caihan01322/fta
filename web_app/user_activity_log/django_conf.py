# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
django setting
"""
from django.conf import settings

# 区分db和es
DB_STORED = 'DB'
ES_STORED = 'ES'
# 默认活动类型为查询
DEFAULT_ACTIVITY_TYPE = 1

# APP CODE
APP_CODE = getattr(settings, 'APP_CODE', 'dafault')

# 上报日志存储类型，现阶段分为ES和DB，默认为DB
LOG_STORED_TYPE = getattr(settings, 'LOG_STORED_TYPE', DB_STORED)

# ES的配置
LOG_ES_ADDRESS = getattr(settings, 'LOG_ES_ADDRESS', None)

# 存储数据的大小
DATA_LIMIT_SIZE = getattr(settings, 'DATA_LIMIT_SIZE', None)

# 上报ES使用的REDIS地址
LOG_REDIS_ADDRESS = getattr(settings, 'LOG_REDIS_ADDRESS', '')
# 端口, 默认6379
LOG_REDIS_PORT = getattr(settings, 'LOG_REDIS_PORT', 6379)
# 密码
LOG_REDIS_PASSWORD = getattr(settings, 'LOG_REDIS_PASSWORD', '')
# 最大链接数, 默认使用600
LOG_REDIS_CONNECTIONS = getattr(settings, 'LOG_REDIS_CONNECTIONS', 600)
# 使用db, 默认使用db: 0
LOG_REDIS_DB = getattr(settings, 'LOG_REDIS_DB', 0)
# 队列名
REDIS_QUEUE_NAME = getattr(settings, 'REDIS_QUEUE_NAME', '')
# 超时时间
REDIS_TIMEOUT = getattr(settings, 'REDIS_TIMEOUT', 1)

# REDIS CONFIGS
REDIS_CONF = {
    'host': LOG_REDIS_ADDRESS,
    'port': LOG_REDIS_PORT,
    'db': LOG_REDIS_DB,
    'password': LOG_REDIS_PASSWORD,
    'max_connections': LOG_REDIS_CONNECTIONS,
    'timeout': REDIS_TIMEOUT
}
