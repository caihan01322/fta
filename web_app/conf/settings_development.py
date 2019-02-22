# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
用于本地开发环境的全局配置
"""

# ===============================================================================
# 数据库设置, 本地开发数据库设置
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 默认用mysql
        'NAME': "bk_fta_solutions",             # 数据库名 (默认与APP_ID相同)
        'USER': 'root',                         # 你的数据库user
        'PASSWORD': '',                         # 你的数据库password
        'HOST': '127.0.0.1',                    # 开发的时候，使用localhost
        'PORT': '3306',                         # 默认3306
    },
}

LOG_LEVEL = "DEBUG"

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings 加入版本管理忽略文件中
try:
    from local_settings import *  # noqa
except ImportError:
    pass
