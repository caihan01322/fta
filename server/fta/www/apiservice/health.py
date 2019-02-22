# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
from datetime import datetime

from fta import settings
from fta.www.apiservice import fta_api_page as app
from fta.www.utils import response
from project.utils.component import bk


@app.route("/status/process/")
@response.log
def health():
    monitor = HealthMonitor()
    results = monitor.get_data()
    return json.dumps(results)


class HealthMonitor(object):
    def __init__(self):
        self.status = []

    def get_data(self):
        checkers = {
            "redis": self.check_redis,
            "mysql": self.check_mysql,
            "beanstalk": self.check_beanstalk,
            "supervisor": self.check_supervisor,
            "cc": self.check_cc,
        }
        results = {}
        fine = True

        for namespace, checker in checkers.items():
            error = ""
            details = None
            try:
                error, details = checker()
            except Exception as err:
                error = str(err)
            if error:
                fine = False
            results.update({
                "%s:details" % namespace: details,
                "%s:error" % namespace: error,
            })
        results["ok"] = fine
        results['result'] = fine
        return results

    def check_redis(self):
        from fta.storage.cache import Cache
        redis = Cache('redis')
        cache_key = "fta_health_check"
        error = ""
        can_set = False
        can_expire = False
        try:
            can_set = redis.set(cache_key, 1)
            can_expire = redis.expire(cache_key, 0)
        except Exception as err:
            error = str(err)
        return error, {
            "can_set": can_set,
            "can_expire": can_expire,
        }

    def check_mysql(self):
        from fta.storage import tables
        from fta.storage.mysql import session
        error = ""
        try:
            session.query(tables.FtaSolutionsAppAlarminstancearchive).filter(
                tables.FtaSolutionsAppAlarminstancearchive.date >= datetime.today(),
            ).count()
        except Exception as err:
            error = str(err)
        return error, {}

    def check_beanstalk(self):
        import beanstalkc

        def _get_bean_stats(host, port, queues):
            error_info = ""
            bean = beanstalkc.Connection(host=host, port=port)

            bean_stats = {}
            try:
                main_stats = bean.stats()
            except Exception as e:
                error_info = str(e)
                main_stats = {"exception": str(e)}
            bean_stats['main'] = main_stats

            for q in queues:
                try:
                    q_stats = bean.stats_tube(q)
                except Exception as e:
                    error_info = str(e)
                    q_stats = {"exception": str(e)}
                bean_stats[q] = q_stats
            return error_info, bean_stats

        bean_queues = [
            settings.QUEUE_COLLECT,
            settings.QUEUE_CONVERGE,
            settings.QUEUE_SOLUTION,
            settings.QUEUE_JOB,
            settings.QUEUE_SCHEDULER,
            settings.QUEUE_POLLING,
            settings.QUEUE_MATCH
        ]
        stats = {}
        error = ""

        if isinstance(settings.BEANSTALKD_HOST, (list, set)):
            bean_hosts = settings.BEANSTALKD_HOST
        else:
            bean_hosts = [settings.BEANSTALKD_HOST]

        for host in bean_hosts:
            err, bean_stats = _get_bean_stats(
                host, settings.BEANSTALKD_PORT, bean_queues,
            )
            if err:
                error = err
            key = '%s:%s' % (host, settings.BEANSTALKD_PORT)
            stats[key] = bean_stats
        return error, stats

    def check_supervisor(self):
        from fta.utils.supervisorctl import get_supervisor_client
        error = ""
        result = {}
        proxy = get_supervisor_client()
        for process in proxy.supervisor.getAllProcessInfo():
            name = process.get("name")
            description = process.get("description")
            statename = process.get("statename")
            if statename != "RUNNING":
                error = "%s not running" % name

            result["%s_description" % name] = description
            result["%s_statename" % name] = statename
        return error, result

    def check_cc(self):
        error = ""
        try:
            bk.cc.get_plat_id()
        except Exception as err:
            error = str(err)
        if error.startswith("40"):  # 40x
            error = ""
        return error, {}
