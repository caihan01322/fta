# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
# PollAlarm for BKMP(BlueKing Monitoring Platform)
import json

import arrow
from project.utils.component import bk

from fta import constants
from fta.poll_alarm.process import BasePollAlarm
from fta.utils import get_time, lock, logging, split_list
from manager.utils.query_cc import (get_bkmonitor_app_info,
                                    handle_alarm_source_empty,
                                    handle_alarm_source_exception,
                                    handle_alarm_source_success)

logger = logging.getLogger("poll_alarm")


class BKMPPollAlarm(BasePollAlarm):
    """拉取 BKMP 告警, 并补充告警相关属性用于匹配"""

    def __init__(self, force_begin_time=None, force_end_time=None, minutes=None, delta_minutes=0):
        """
        :param force_begin_time: 指定拉取的告警的开始时间
        :param force_end_time: 指定拉取的告警的结束时间
        :param minutes: 指定拉取一天中的哪一分钟(一天的第一分钟为1，共24*60分钟)
        :param delta_minutes: 指定拉取与当前分钟相差多久的时间的告警
        """
        self.delta_minutes = delta_minutes
        self.str_begin_time, self.str_end_time = get_time.get_time(
            minutes=minutes, delta_minutes=delta_minutes, interval=-10)
        self.str_begin_time = force_begin_time or self.str_begin_time
        self.str_end_time = force_end_time or self.str_end_time
        self.biz_service_ids = {}
        self.hosts_info = {}
        self.qos_dict = {}
        self._db_module = {}
        self._db_responsible = []
        super(BKMPPollAlarm, self).__init__()

    def get_origin_alarm(self, alarm):
        origin_alarm = json.loads(alarm['origin_alarm'])
        origin_alarm['bk_match_info'] = origin_alarm['_match_info']
        return origin_alarm

    def pull_alarm(self):
        """拉取告警"""

        lock_bkmp_polling(
            self.str_begin_time, self.str_end_time,
            self.delta_minutes, group="BKMP"
        )

        params = {
            'page_size': 0,
            'source_time__gte': self.str_begin_time,
            'source_time__lte': self.str_end_time,
            '_method': 'GET',
            'user_status__in': 'notified,unnotified',
        }
        app_info = get_bkmonitor_app_info()
        app_id = app_info.get('app_id', '')
        self.alarm_list = []
        try:
            data = bk.data.get_alarms(**params)
        except Exception as e:
            # 记录告警源异常信息
            handle_alarm_source_exception(app_id, e)
            import traceback
            logger.error(
                '%s BEGIN-END %s - %s (%s)',
                constants.ERROR_02_MONITOR, self.str_begin_time, self.str_end_time[-8:], traceback.format_exc())
        else:
            if isinstance(data, (list, tuple)):
                self.alarm_list = map(self.get_origin_alarm, data)

            # 从告警源中没有拉取到告警，也要记录到db总
            if len(self.alarm_list) == 0:
                handle_alarm_source_empty(app_id)
            else:
                handle_alarm_source_success(app_id)

        logger.info(
            'BEGIN-END %s - %s (%s)',
            self.str_begin_time, self.str_end_time[-8:], len(self.alarm_list))

    def push_alarm(self):
        """推送告警进行匹配"""
        super(BKMPPollAlarm, self).push_alarm()

    def is_host_alarm(self, alarm):
        """是否为单机告警"""
        return alarm["bk_match_info"]["category"] in ["performance", "base_alarm"]

    def get_plat_info(self, alarm):
        """
        获取单机告警中的plat_id, company_id, ip等字段
        """
        plat_id = alarm["bk_match_info"].get('cc_plat_id')
        plat_id = int(plat_id)

        company_id = alarm["bk_match_info"].get('cc_company_id')
        try:
            company_id = int(company_id)
        except BaseException:
            company_id = None

        ip = alarm["bk_match_info"].get("host") or ""
        return plat_id, company_id, ip

    # ------------- clean_xxx method will be called to get info to do matching

    def clean_host(self, alarm):
        return alarm["bk_match_info"]["host"]

    def clean_source_id(self, alarm):
        """
        获取告警源 ID
        :param alarm: 原始告警字典
        :return source_type: 告警源的告警 ID
        """
        return alarm["bk_match_info"]["source_id"]

    def clean_source_type(self, alarm):
        """
        获取告警源
        :param alarm: 原始告警字典
        :return source_type: 告警源的名称
        """
        return 'ALERT'

    def clean_source_time(self, alarm):
        """source_time already is utc time
        """
        return alarm['source_time']

    def clean_alarm_attr_id(self, alarm):
        return alarm.get("monitor_id", "unknow")

    def clean_alarm_source_id(self, alarm):
        return alarm['alarm_source_id']

    def clean_alarm_type(self, alarm):
        monitor_type = alarm['monitor_type']
        monitor_target = alarm['bk_match_info']['monitor_target']
        if self.is_host_alarm(alarm):
            alarm_type = '%s_%s' % (monitor_type, monitor_target)
        else:
            alarm_type = monitor_type
        logger.info('alarm_type_log alarm_type:%s', alarm_type)
        return [alarm_type]

    def clean_alarm_time(self, alarm):
        """告警发生的时间，格式：YYYY-MM-DD HH:mm:ss
        """
        return alarm['bk_match_info']['alarm_time']

    def clean_alarm_desc(self, alarm):
        monitor_source_name = alarm['bk_match_info']['monitor_source_name']
        message = alarm['bk_match_info']['alarm_desc']
        if monitor_source_name:
            return '%s: %s' % (monitor_source_name, message)
        else:
            return message

    def clean_cc_biz_id(self, alarm):
        return alarm['bk_match_info']['cc_biz_id']

    def clean_cc_topo_set(self, alarm):
        if 'dimensions' in alarm and isinstance(alarm['dimensions'], dict):
            dimensions = alarm['dimensions']
            return split_list(dimensions.get('SetName', '') or dimensions.get('SetID', ''))
        return []

    def clean_cc_app_module(self, alarm):
        if 'dimensions' in alarm and isinstance(alarm['dimensions'], dict):
            dimensions = alarm['dimensions']
            return split_list(dimensions.get('ModuleName', '') or dimensions.get('ModuleID', ''))
        return []

    def clean_cc_company_id(self, alarm):
        _, company_id, _ = self.get_plat_info(alarm)
        return company_id

    def clean_cc_plat_id(self, alarm):
        plat_id, _, _ = self.get_plat_info(alarm)
        return plat_id


def lock_bkmp_polling(str_begin_time, str_end_time, delta_minutes, group):
    begin_time = arrow.get(str_begin_time)
    minutes = (begin_time - begin_time.floor('day')).seconds / 60
    id_ = int(begin_time.format("YYMMDD") + str(minutes))
    if not lock.redis_lock("--lock_%s_%s-%s-%s" % (group, str_begin_time, str_end_time, delta_minutes)):
        raise lock.LockError("poll_%s: %s pass" % (group, id_))
