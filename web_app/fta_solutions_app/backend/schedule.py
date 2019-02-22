# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import random

import requests
from celery import task
from celery.schedules import crontab
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _

from common.log import logger
from fta_solutions_app.backend.utils import get_fta_admin_str
from fta_solutions_app.models import Conf
from fta_utils.cache_update import update_cache as real_update_cache
from project.component import send

"""
这里只放后台定时启动的任务
"""


@task.periodic_task(run_every=crontab(minute="*/30"))
def update_cache():
    '''统一对缓存函数列表进行更新的定时任务'''
    real_update_cache()


@task.periodic_task(run_every=crontab(minute="*"))
def check():
    if cache.get('--close_check--'):
        logger.info("pass check process because of close")
        return True
    safe_key = "--check_process_safe--"
    phone_key = "--check_process_phone--"
    try:
        all_fta_host = json.loads(Conf.objects.get(name="FTA_HOST").value)
    except Exception:
        return False

    fta_admin_str = get_fta_admin_str()
    fta_admin_list = fta_admin_str.split(',') if fta_admin_str else []
    success_count = 0
    for host in all_fta_host:
        try:
            result = requests.get("http://%s:8081/fta/status/process/" % host, timeout=16, verify=False).json()
            error_process = [(name, status) for name, status in result.items() if status not in ["RUNNING", "STOPPED"]]
            if error_process:
                raise Exception(','.join(map(str, error_process)))
            else:
                success_count += 1
        except Exception as e:
            send.wechat(
                fta_admin_str,
                _(u'【自愈%s】检查[%s]后台进程异常: %s') % (settings.RUN_MODE, host, e))
            logger.error("Check backend process failed: %s" % e)
    if success_count > len(all_fta_host) - 2:
        logger.info(safe_key)
        cache.set(safe_key, "--set--", 60 * 5)
    if not cache.get(safe_key):
        if not cache.get(phone_key):
            cache.set(phone_key, '--send--', 60 * 60)
            verifier_list = [v for v in fta_admin_list]
            random.shuffle(verifier_list)
            logger.info("check process send phone %s" % verifier_list)
            if settings.RUN_MODE == "PRODUCT":
                send.phone(verifier_list, u"尊敬的自愈团队,故障自愈连续5分钟检测到两台以上进程状态异常,请关注")
            send.wechat(fta_admin_str, u'【自愈%s】连续5分钟检测到两台以上后台进程状态异常' % settings.RUN_MODE)
    return True
