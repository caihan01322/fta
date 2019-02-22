# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import os

# 本地社区版蓝鲸智云页面访问地址 eg: http://paas.bk.com
PAAS_ADDR = ''

# 本地社区版蓝鲸智云内网地址 如果不确认 可以和PAAS_ADDR保持一致  eg: http://paas.bk.com
PAAS_INNER_ADDR = ''

# 本地社区版JOB页面访问地址 eg: http://job.bk.com
JOB_ADDR = ''

# 故障自愈app_code 请不要改动 和开发者中心里的Smart里的官方应用"故障自愈"的app_code保持一致
APP_CODE = 'bk_fta_solutions'

# 故障自愈app_token 可以通过蓝鲸智云开发者中心admin管理页面获取
APP_SECRET_KEY = ''

# 通知人列表 填写后本地开发环境所有的信息都将发给此通知人列表中的用户
VERIFIER = [""]

# 根目录设置
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAK_PATH = LOG_PATH = LOGS_HOME = os.path.join(ROOT_PATH, "logs")

# 本地python运行环境 eg: /usr/local/python2.7/bin/
PYTHON_HOME = ""  # replace your python path
PYTHON = os.path.join(PYTHON_HOME, "python")
GUNICORN = os.path.join(PYTHON_HOME, "gunicorn")

# ENVIRONMENT
ENV = "LOCAL"
LOG_LEVEL = "DEBUG"
WCB_DUMMY = True

# SIGNATURE FOR MESSAGE
SIGNATURE = "【%s %s】" % (','.join(VERIFIER), ENV)

# POLL_ALARM
POLL_INTERVAL = 1  # minutes
POLL_LIST = [
    # add your poll_alarm module here
    'bk_monitor',
]

# CRONTAB
DEFAULT_CRONTAB = [
    # (module_name, every) like: ("fta.poll_alarm.main start", "* * * * *")
    # 更新未接入告警统计表
    ("project.script.unmatched_alarm_analyser", "0 0 * * *"),
]
DEFAULT_SCRIPT_CRONTAB = [
    # (command, every) like: ("./script/manage.sh ci", "30 10 * * *")
]

SUPERVISOR_SERVER_SOCK = os.path.join(LOGS_HOME, "supervisord.sock")
SUPERVISOR_SERVER_URL = "unix://%s" % SUPERVISOR_SERVER_SOCK
SUPERVISOR_USERNAME = "fta"
SUPERVISOR_PASSWORD = "admin@fta"

# FTA
WEBSERVER_PORT = 13021
APISERVER_PORT = 13031
JOBSERVER_PORT = 13041
WEBSERVER_URL = "http://127.0.0.1:%s" % WEBSERVER_PORT

# BEANSTALKD
BEANSTALKD_HOST = ['']
BEANSTALKD_PORT = 14711

# MYSQL
MYSQL_NAME = 'bk_fta_solutions'
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_HOST = ''
MYSQL_PORT = 3306

# REDIS
REDIS_HOST = ['']
REDIS_PASSWD = ''
REDIS_PORT = 6379
REDIS_MAXLOG = 10000
REDIS_CACHE_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 1,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_DIMENSION_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 1,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_LOG_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 1,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_CALLBACK_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 1,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_LOCALCACHE_CONF = {
    'host': 'localhost',
    'port': REDIS_PORT,
    'db': 1,
    'password': REDIS_PASSWD,
}
REDIS_TEST_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 1,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]

# SOLUTION
SOLUTION_DUMMY = False

# GCLOUD
GCLOUD_ENDPOINT = os.path.join(PAAS_INNER_ADDR, "api/c/self-service-api/")
GCLOUD_DETAIL_ENDPOINT = os.path.join(PAAS_ADDR, "o/bk_sops/", )

# 故障自愈页面访问地址
APP_URL_PROD = APP_URL_TEST = '%s/o/bk_fta_solutions/' % PAAS_ADDR

DIMENSION_EXPIRE_HOURS = 24
