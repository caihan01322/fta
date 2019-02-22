# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import os

APP_CODE = "__APP_CODE__"
APP_SECRET_KEY = "__APP_TOKEN__"
NO_CIPHER_SECRET = True

PYTHON_HOME = "__BK_HOME__/.envs/fta/bin"
BIN_HOME = "/usr/local/bin/"

WEBSERVER_PORT = __FTA_WEBSERVER_PORT__
APISERVER_PORT = __FTA_APISERVER_PORT__
JOBSERVER_PORT = __FTA_JOBSERVER_PORT__

BK_HOME = "__BK_HOME__"
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
BAK_PATH = "__LOGS_HOME__"
LOGS_HOME = "__LOGS_HOME__"
LOG_PATH = LOGS_HOME

# ENVIRONMENT
ENV = "PRODUCT"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
WCB_DUMMY = False
# SIGNATURE FOR MESSAGE
SIGNATURE = ""

# POLL_ALARM
POLL_INTERVAL = 1  # minutes
POLL_LIST = [
    # add your poll_alarm module here
    'bk_monitor',
    'bk_monitor1',
    'bk_monitor2',
    'custom_monitor',
    # 邮件拉取
    'email_poller',
]

# CRONTAB
DEFAULT_CRONTAB = [
    # (module_name, every) like: ("fta.poll_alarm.main start", "* * * * *")
    # 清空过期的维度信息
    ("fta.converge.dimension clean", "00 12 * * *"),
    # 健康度报告
    ("fta.advice.process", "00 08 * * *"),
    # 更新统计表
    ("project.script.update_cache_table", "*/30 * * * *"),
    ("project.hooks.poll_process", "0 1 * * *"),
    # 更新未接入告警统计表
    ("project.script.unmatched_alarm_analyser", "0 0 * * *"),
]
DEFAULT_SCRIPT_CRONTAB = [
    # (command, every) like: ("./script/manage.sh ci", "30 10 * * *")
]

PYTHON = os.path.join(PYTHON_HOME, "python")
GUNICORN = os.path.join(PYTHON_HOME, "gunicorn")

# SUPERVISOR
SUPERVISOR_SERVER_URL = "unix://%s" % os.path.join(LOGS_HOME, "supervisord.sock")
SUPERVISOR_USERNAME = "fta"
SUPERVISOR_PASSWORD = "admin@fta"

# FTA
WEBSERVER_URL = "http://127.0.0.1:13021"

# BEANSTALKD
BEANSTALKD_HOST = ['__BEANSTALK_IP0__', '__BEANSTALK_IP1__']
BEANSTALKD_PORT = __BEANSTALK_PORT__

# MYSQL
MYSQL_NAME = 'bk_fta_solutions'
MYSQL_USER = "__MYSQL_USER__"
MYSQL_PASSWORD = "__MYSQL_PASS__"
MYSQL_HOST = "__MYSQL_IP0__"
MYSQL_PORT = __MYSQL_PORT__

# REDIS
REDIS_CLUSTER_IP = '__REDIS_CLUSTER_IP0__'

# 使用 Sentinel 集群模式
if REDIS_CLUSTER_IP:
    # for redis cluster
    REDIS_HOST = ['__REDIS_CLUSTER_IP0__',
                  '__REDIS_CLUSTER_IP1__',
                  '__REDIS_CLUSTER_IP2__']
    REDIS_PORT = __REDIS_CLUSTER_PORT__
    REDIS_MASTER_NAME = "__REDIS_MASTER_NAME__"
    CACHE_BACKEND_TYPE = "SentinelRedisCahce"
else:
    REDIS_HOST = ['__REDIS_IP0__']
    REDIS_PORT = __REDIS_PORT__

REDIS_PASSWD = "__REDIS_PASS__"
REDIS_MAXMEMORY = '4gb'
REDIS_MAXLOG = 50000
REDIS_CACHE_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 12,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_DIMENSION_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 13,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_LOG_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 14,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_CALLBACK_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 15,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]
REDIS_LOCALCACHE_CONF = {
    'host': 'localhost',
    'port': REDIS_PORT,
    'db': 12,
    'password': REDIS_PASSWD,
}
REDIS_TEST_CONF = [
    {
        'host': redis_host,
        'port': REDIS_PORT,
        'db': 15,
        'password': REDIS_PASSWD,
    } for redis_host in REDIS_HOST
]


# SUPERVISOR_AUTO_START
START_FTA = True
START_COMMON = True

# SOLUTION
SOLUTION_DUMMY = False

HTTP_SCHEMA = "__HTTP_SCHEMA__"

# 兼容之前的版本，没有这个变量则默认为HTTP部署
HTTP_SCHEMA = HTTP_SCHEMA or "http"

if HTTP_SCHEMA == "https":
    # HTTPS 模式下，页面访问走 https，内部API访问走 http
    PAAS_ADDR = "https://__PAAS_FQDN__:__PAAS_HTTPS_PORT__"
    PAAS_INNER_ADDR = 'http://__PAAS_HOST__:__PAAS_HTTP_PORT__'
    # JOB 页面访问地址
    JOB_ADDR = "https://__JOB_FQDN__:__JOB_HTTPS_PORT__"
else:
    # HTTP 模式下，页面访问和内部API访问都走 http
    PAAS_ADDR = "http://__PAAS_FQDN__:__PAAS_HTTP_PORT__"
    PAAS_INNER_ADDR = PAAS_ADDR
    # JOB 页面访问地址
    JOB_ADDR = "http://__JOB_FQDN__:__JOB_HTTP_PORT__"

# GCLOUD
GCLOUD_ENDPOINT = os.path.join(PAAS_INNER_ADDR, "api/c/self-service-api/")
GCLOUD_DETAIL_ENDPOINT = os.path.join(PAAS_ADDR, "o/bk_sops/",)

# 企业版没有测试环境
APP_URL_PROD = '%s/o/bk_fta_solutions/' % PAAS_ADDR
APP_URL_TEST = APP_URL_PROD

CERT_PATH = "__CERT_PATH__"
LICENSE_HOST = "__LICENSE_HOST__"
LICENSE_PORT = "__LICENSE_PORT__"

DIMENSION_EXPIRE_HOURS = 24
