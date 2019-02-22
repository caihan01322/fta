# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import os

import arrow
import redis.exceptions

from fta import constants, settings
from fta.storage.cache import Cache
from fta.utils import lock, logging, scheduler, send_notice
from fta.utils.i18n import _

logger = logging.getLogger("root")

redis_client = Cache('log')


class LogProcess(object):

    def pull_log(self):
        """read log form local redis"""
        try:
            record = redis_client.brpop("logs", timeout=1)
            if not record:
                raise lock.PassEmpty
        except redis.exceptions.TimeoutError as e:
            logger.info("reading log from redis error: %s" % e)

        self.record_dict = json.loads(record[1])
        self.filename = os.path.abspath(self.record_dict['pathname'])

        # mark a key for log's process
        redis_client.set(str(self.record_dict['process']), constants.MARK_VALUE, settings.FTA_PROCESS_CHECK_TIME)

    def _send_critical(self):
        """send notice for cirtical level log"""
        send_notice.critical(self.record_dict['message'], self.filename, self.record_dict['lineno'])

    def _send_exception(self):
        """send notice for exception level log"""
        send_notice.exception(
            self.record_dict['message'], self.filename, self.record_dict['lineno'], [self.record_dict['exc_info']]
        )

    def _send_error(self):
        """send notice for error level log"""
        send_notice.error(self.record_dict['message'], self.filename, self.record_dict['lineno'])

    def _send_warning(self):
        """send notice for collected warning level log"""
        warning_timeout = 12 * 60 * 60
        redis_client.hincrby("log.warning", "%s:%s" % (self.filename, self.record_dict['lineno']))
        redis_client.expire("log.warning", warning_timeout * 2)
        if lock.redis_lock("log.send_warning", timeout=warning_timeout):
            scheduler.run(module='fta.logging.process', function='_send_warning', delta_seconds=warning_timeout)

    def send_log(self):
        """send notice by log's level & content"""
        if self.record_dict['level'] >= 50:
            self._send_critical()
        elif self.record_dict['level'] == 40 and self.record_dict['exc_info']:
            self._send_exception()
        elif self.record_dict['level'] == 40:
            self._send_error()
        elif self.record_dict['level'] == 30:
            self._send_warning()

    def push_log(self):
        pass

    def start(self, bucket):
        self.record_list = []
        for i in range(bucket):
            try:
                self.pull_log()
            except lock.PassEmpty:
                break
            self.send_log()
            self.push_log()
            self.record_list.append(self.record_dict)


def get_log_file_path(file_name):
    return os.path.abspath(os.path.join(settings.LOG_PATH, file_name))


LOG_FILE_PATH = get_log_file_path("fta.log")


def move_log_by_day():
    """split log file by day"""

    # named fta.log as yestoday
    yestoday = arrow.now().replace(days=-1).format("YYYY-MM-DD")
    yestoday_log_file_path = get_log_file_path("fta.%s.log" % yestoday)
    if not os.path.isfile(yestoday_log_file_path):
        os.rename(LOG_FILE_PATH, yestoday_log_file_path)

    # delete months ago's log file
    month_ago = arrow.now().replace(days=-10).format("YYYY-MM-DD")
    month_ago_log_file_path = get_log_file_path("fta.%s.log" % month_ago)
    month_ago_log_file_path_2 = get_log_file_path("fta.%s.2.log" % month_ago)
    if os.path.isfile(month_ago_log_file_path):
        os.remove(month_ago_log_file_path)
    if os.path.isfile(month_ago_log_file_path_2):
        os.remove(month_ago_log_file_path_2)


def move_log_by_size():
    """split log file by size"""

    today = arrow.now().format("YYYY-MM-DD")
    today_log_file_path = get_log_file_path("fta.%s.2.log" % today)
    if os.path.isfile(LOG_FILE_PATH) and os.path.getsize(LOG_FILE_PATH) > settings.FTA_LOGFILE_MAXSIZE:
        # named fta.log as today_2
        os.rename(LOG_FILE_PATH, today_log_file_path)
        send_notice.error(_("[Fault Auto-recovery] Log exceeds threshold size"))


def clean_log_by_size():
    """Global control log size
    """
    log_files = os.listdir(os.path.dirname(LOG_FILE_PATH))
    fta_logs = {}
    for file in log_files:
        if file.startswith('fta'):
            fta_logs[file] = os.path.getsize(get_log_file_path(file))

    while sum(fta_logs.values()) > settings.FTA_LOGFILE_MAXSIZE_GLOBAL:
        files = sorted(fta_logs.keys())
        if len(files) > 2:
            last_log = files[0]
            os.remove(get_log_file_path(last_log))
            fta_logs.pop(last_log)
            logger.warning(
                "fta log has reached its maximum %s, remove last log file %s" % (
                    settings.FTA_LOGFILE_MAXSIZE_GLOBAL, last_log)
            )


def _send_warning():
    """send warning notice"""
    result = redis_client.hgetall("log.warning")
    lines = sorted([_("%(k)s %(v)s times", k=k, v=v) for k, v in result.items()])
    send_notice._send(lines, "", "", 30)
    redis_client.delete("log.warning")
