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
import sys

import arrow

from fta import constants, settings
from fta.storage.cache import Cache
from fta.storage.queue import MessageQueue
from fta.utils import hooks, lock, logging, monitors, remove_blank
from fta.www.utils import chart

redis_cache = Cache("redis")

MATCH_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_MATCH)

logger = logging.getLogger("poll_alarm")

hook = hooks.HookManager("poll_process")
poll_check = hook.get("poll_check", lambda: True)
poll_check()


class BasePollAlarm(object):

    def __init__(self):
        self.alarm_list = []
        self.alarm_bucket = ''

    @property
    def alarm_file(self):
        file_name = "%s.alarm.%s" % (type(self).__name__, ".".join(sys.argv[1:]))
        return os.path.abspath(os.path.join(settings.BAK_PATH, file_name))

    def load_alarm(self):
        """Load alarm from alarm file is exists"""
        if not os.path.isfile(self.alarm_file):
            return []
        with open(self.alarm_file) as fp:
            try:
                alarm_data = json.load(fp) or []
            except BaseException:
                logger.exception("%s load local alarm file failed", constants.ERROR_01_POLL)
                alarm_data = []
        logger.info("Load alarm file: %s count(%s)" % (self.alarm_file, len(alarm_data)))
        return alarm_data

    def dump_alarm(self):
        """Dump alarm to alarm file"""
        with open(self.alarm_file, 'w+') as fp:
            json.dump(self.alarm_list, fp)
        logger.info("Dump alarm file: %s" % self.alarm_file)

    def delete_alarm(self):
        """Delete alarm file"""
        if os.path.isfile(self.alarm_file):
            os.remove(self.alarm_file)
        logger.info("Deleted alarm file: %s" % self.alarm_file)

    def pull_alarm(self):
        raise Exception('Should be a pull_alarm method')

    def count_alarm(self):
        """After get alarm, can do some count work here"""
        chart.Data.add_point(
            type(self).__name__, arrow.utcnow().timestamp, len(self.alarm_list))

    def clean_alarm(self):
        """
        Call the clean_xxx method to get fields to do matching.
        The clean_xxx method should return a cleaned xxx value.
        """
        for alarm in self.alarm_list:
            alarm["_match_info"] = {}
            for match_key in constants.ALARM_BASE_KEY:
                match_value = self._get_clean_value(match_key, alarm)
                alarm["_match_info"][match_key] = match_value

    def _get_clean_value(self, clean_key, alarm):
        """
        get clean_value from alarm_dict from clean key
        """

        def clean_method_bak(*args, **kwargs):
            return ""

        clean_method_name = "clean_%s" % clean_key
        clean_method = getattr(self, clean_method_name, clean_method_bak)
        try:
            clean_value = remove_blank(clean_method(alarm))
        except Exception as e:
            clean_value = remove_blank(clean_method_bak(alarm))
            logger.exception("clean_method_error %s: %s", e, alarm)
        return clean_value

    def push_alarm(self):
        """push alarm to MatchAlarm
        beanstalkd协议默认只允许2**16个字节，需要拆分告警队列依次发送
        https://github.com/kr/beanstalkd/blob/master/doc/protocol.txt
        """
        for alarm in self.alarm_list:
            serialized_alarm = json.dumps(alarm)
            self.bucket_send(serialized_alarm)
        self.bucket_send('', push_remain=True)
        logger.info("push alarm to match queue finished(%s)" % len(self.alarm_list))

    def bucket_send(self, serialized_alarm, push_remain=False):
        """发送Match
        用\r\n分隔告警
        """
        # 发送剩余告警
        if push_remain and self.alarm_bucket:
            MATCH_QUEUE.put(self.alarm_bucket)
            self.alarm_bucket = ''
            return True

        # 单个告警大于bucket大小的，直接丢弃
        if len(serialized_alarm) > constants.JOB_BUCKET:
            logger.warning(
                'alarm: %s length(%s) >= bucket(%s), just ignored.',
                serialized_alarm, len(serialized_alarm), constants.JOB_BUCKET)
            return False

        # 批量发送bucket大小的告警
        alarm_bucket = self.alarm_bucket + '\r\n' + serialized_alarm
        if len(alarm_bucket) > constants.JOB_BUCKET:
            MATCH_QUEUE.put(self.alarm_bucket)
            self.alarm_bucket = serialized_alarm
        else:
            self.alarm_bucket = alarm_bucket

    def mark_log(self, status):
        """make a mark in log for debug"""
        module_name = self.__module__.split(".")[-1]
        logger.info("--%s poll_alarm-- %s" % (status, module_name))

    def mark_redis(self):
        """make a mark in redis for alive_watcher"""
        module_name = self.__module__.split(".")[-1]
        redis_cache.set(module_name, "--end poll_alarm--", settings.POLL_INTERVAL * 60 * 3)

    def start(self):
        self.mark_log("begin")
        try:
            self.mark_redis()
            self.pull_alarm()
            self.count_alarm()
            self.alarm_list = self.alarm_list + self.load_alarm()
            if not self.alarm_list:
                raise lock.PassEmpty
            self.dump_alarm()
            self.clean_alarm()
            self.push_alarm()
            # all alarms have been pushed successed, so delete local alarm file
            self.delete_alarm()
        except lock.PassEmpty:
            pass
        except lock.LockError as e:
            logger.info(e)
        self.mark_log("end")


class BaseSourcePollAlarm(BasePollAlarm):
    SOURCE_TYPE = "UNKNOWN"
    DEFAULT_ALARM_TYPE = None

    def clean_host(self, alarm):
        return alarm["ip"]

    def clean_source_id(self, alarm):
        return alarm["source_id"]

    def clean_source_type(self, alarm):
        """
        获取告警源
        :param alarm: 原始告警字典
        :return source_type: 告警源的名称
        """
        return self.SOURCE_TYPE

    def clean_source_time(self, alarm):
        return alarm['source_time']

    def clean_alarm_type(self, alarm):
        """
        获取告警类型
        :param alarm: 原始告警字典
        :return alarm_type_list: 从 alarm 中获取的 alarm_type 的值
        """
        return list(monitors.lookup_alarm_type_list(
            alarm["alarm_type"].split(","),
            cc_biz_id=self.cc_biz_id, source_type=self.SOURCE_TYPE,
            default=self.DEFAULT_ALARM_TYPE or self.SOURCE_TYPE.lower(),
        ))

    def clean_alarm_time(self, alarm):
        return alarm['source_time']

    def clean_alarm_desc(self, alarm):
        return alarm['alarm_content']

    def clean_alarm_source_id(self, alarm):
        return ''

    def clean_alarm_attr_id(self, alarm):
        return ''

    def clean_cc_biz_id(self, alarm):
        return alarm['_CC_HOST_INFO']['ApplicationID']

    def clean_cc_topo_set(self, alarm):
        return alarm['_CC_HOST_INFO']['SetName'].split(",")

    def clean_cc_app_module(self, alarm):
        return alarm['_CC_HOST_INFO']['ModuleName'].split(",")

    def clean_cc_company_id(self, alarm):
        return alarm['_CC_COMPANY_INFO']['CompanyID']

    def clean_cc_plat_id(self, alarm):
        return alarm['_CC_COMPANY_INFO']['PlatID']

    def clean_alarm_context(self, alarm):
        return ''
