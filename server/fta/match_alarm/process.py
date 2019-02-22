# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
import re

from fta import constants, settings
from fta.match_alarm import dimension
from fta.match_alarm.alarminstance import AlarmInstanceManager
from fta.storage.queue import MessageQueue
from fta.utils import hooks, lock, logging
from manager.define.alarmdef import AlarmDefManager

logger = logging.getLogger('match_alarm')
hook = hooks.HookManager("match_alarm")

MATCH_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_MATCH)
COLLECT_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_COLLECT)
CONVERGE_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_CONVERGE)

hook = hooks.HookManager("match_alarm")
unmatch_alarm_hook = hook.get("unmatch_alarm_hook", (lambda alarm: None), )


class MatchAlarm(object):
    """filter alarm_list by alarm_def_list and ALARM_MATCH_KEY_LIST"""

    # there are 4 function for match check
    MATCH_FUNC = {
        '==': 'equal',
        '<=': 'include',
        '&&': 'intersection',
        're': 'regular',
        '>=': 'exclude',
    }

    def __init__(self, alarm_list=(), alarm_def_list=()):
        """
        :param alarm_list: raw_alarm_dict list include "_match_info"
        :param alarm_def_list: alarm_def_dict list
            include all key in ALARM_MATCH_KEY_LIST
        """

        self.matched_alarm_list = []
        self.alarm_list = list(alarm_list)
        self.job = None
        self.alarm_def_list = alarm_def_list or self.get_alarm_def_list()
        logger.info("Get %d alarms for match" % len(self.alarm_list))

    def get_alarm_def_list(self):
        alarm_def_manager = AlarmDefManager()
        return alarm_def_manager.alarm_def_list

    def pull_alarm(self):
        """pull alarm from queue if you want"""
        self.job = MATCH_QUEUE.take(timeout=settings.QUEUE_WAIT_TIMEOUT)

        if not self.job:
            raise lock.PassEmpty

        # JSON数据格式，反序列化
        try:
            self.alarm_list = map(json.loads, self.job.body.strip().splitlines())
        except Exception as error:
            logger.warning(
                'match alarm pull error:%s, %s, please check job is json serialized',
                error,
                self.job.body)

    def match_alarm(self):
        """
        check whether match for every alarm-alarm_def-match_key
        the match result will be self.matched_alarm_list
        """
        for alarm in self.alarm_list:
            is_matched = False
            self._match_alarm_by_def(alarm)
            if alarm["_match_info"].get("alarm_def_id"):
                self.matched_alarm_list.append(alarm)
                is_matched = True

            if is_matched:
                logger.debug(
                    "Matched alarm(source_id:%s)",
                    alarm["_match_info"].get("source_id"))
            else:
                logger.debug(
                    "UNMatched alarm(source_id:%s)",
                    alarm["_match_info"].get("source_id"))
                unmatch_alarm_hook(alarm)

        logger.info("matched_alarm_list (%s)", len(self.matched_alarm_list))

    def _match_alarm_by_def(self, alarm, origin_alarm_def_id=None,
                            unmatch_log=None):
        """
        match alarm by alarm_def
        alarm["_match_info"]["alarm_def_id"] will be matched alarm_def's id

        :param unmatch_log: default is False
            set True will return a tuple for descript why not matched :
            (match_key, alarm_def_value, alarm_value)
            usually used in debug
        """
        if unmatch_log is None and settings.ENV == "TEST":
            unmatch_log = True

        matched_alarm_def_id = None
        for alarm_def in self.alarm_def_list:
            for match_key, match_func in constants.ALARM_MATCH_KEY.items():
                # get alarm_def_value from alarm_def_dict
                alarm_def_value = alarm_def[match_key]
                # exclude_biz_ids 需要特色处理
                if match_key == 'exclude_biz_ids':
                    alarm_value = str(alarm["_match_info"].get('cc_biz_id'))
                else:
                    # get alarm_value from _match_info_dict in alarm_dict
                    alarm_value = alarm["_match_info"].get(match_key)
                # get the check function
                operator_func_name = self.MATCH_FUNC[match_func]
                operator_func = getattr(self, operator_func_name)
                # rule1. if not alarm_def_value is matched
                # rule2. if not alarm_value is not matched
                # rule3. exec check function return whether matched
                is_matched = (not alarm_def_value) or (alarm_value and operator_func(alarm_value, alarm_def_value))
                if not is_matched:
                    if unmatch_log:
                        logger.debug("unmatched_key/alarm_def/alarm: %s %s %s", match_key, alarm_def_value, alarm_value)
                    break
            # else means is matched
            else:
                if origin_alarm_def_id:
                    # If origin_alarm_def_id is not None, means
                    # probably match multi alarm_def, so we should
                    # check the matched alarm_def_id whether
                    # is origin_alarm_def_id
                    if alarm_def["id"] != origin_alarm_def_id:
                        continue
                # add alarm_def_id to _match_info dict for converge
                alarm["_match_info"]["alarm_def_id"] = alarm_def["id"]
                matched_alarm_def_id = alarm_def["id"]
                break
        return matched_alarm_def_id

    def equal(self, alarm_value, alarm_def_value):
        if isinstance(alarm_value, (list, set)) and isinstance(alarm_def_value, (list, set)):
            return set(alarm_value) == set(alarm_def_value)
        else:
            return unicode(alarm_value) == unicode(alarm_def_value)

    def include(self, alarm_value, alarm_def_value):
        if isinstance(alarm_value, (list, set)) and isinstance(alarm_def_value, (list, set)):
            return set(alarm_value).issubset(set(alarm_def_value))
        else:
            return alarm_value in alarm_def_value

    def intersection(self, alarm_value, alarm_def_value):
        if isinstance(alarm_value, (list, set)) and isinstance(alarm_def_value, (list, set)):
            return set(alarm_value) & set(alarm_def_value)
        else:
            return False

    def regular(self, alarm_value, alarm_def_value):
        try:
            reg = re.compile(r"%s" % alarm_def_value)
            if reg.findall(alarm_value):
                return True
        except Exception as e:
            logger.warning("match regular error: %s %s %s", alarm_value, alarm_def_value, e)
        return False

    def exclude(self, alarm_value, alarm_def_value):
        return not self.include(alarm_value, alarm_def_value)

    def push_alarm(self):

        # save alarm_instance into mysql
        alarm_instance_manager = AlarmInstanceManager(self.matched_alarm_list)
        alarm_instance_manager.save()

        for alarm_instance in alarm_instance_manager.alarm_instance_list:
            if alarm_instance["status"] == "for_reference":
                # push collect alarm_instance into collect queue
                COLLECT_QUEUE.put(str(alarm_instance['event_id']))
                logger.info("put alarm into collect beanstalkd: %s", alarm_instance['event_id'])
            elif alarm_instance['status'] == 'received':
                # push normal alarm_instance into converge queue
                # save dimension to redis for converge
                dimension.DimensionCalculator(alarm_instance).calc_dimension()
                CONVERGE_QUEUE.put(str(alarm_instance['event_id']), int(alarm_instance['priority']))
                logger.info("put alarm into converge beanstalkd: %s", alarm_instance['event_id'])

    def start(self):
        try:
            self.pull_alarm()
            self.match_alarm()
            self.push_alarm()
        except lock.PassEmpty:
            pass
        except Exception as e:
            logger.exception('%s match alarm process error: %s', constants.ERROR_01_MATCH, e)
            raise
        finally:
            if self.job:
                self.job.delete()
