# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow
import requests

from fta.poll_alarm.process import BasePollAlarm
from fta.utils import get_time, lock, logging, monitors
from manager.utils.query_cc import (
    get_cc_info_by_ips, get_custom_app_info,
    handle_alarm_source_empty,
    handle_alarm_source_exception,
    handle_alarm_source_success)

logger = logging.getLogger("poll_alarm")


def lock_polling(str_begin_time, str_end_time, delta_minutes, group):
    begin_time = arrow.get(str_begin_time).replace(tzinfo="local")
    minutes = (begin_time - begin_time.floor('day')).seconds / 60
    id_ = int(begin_time.format("YYMMDD") + str(minutes))
    if not lock.redis_lock("--lock_%s_%s-%s-%s" % (group, str_begin_time, str_end_time, delta_minutes)):
        raise lock.LockError("poll_%s: %s pass" % (group, id_))


class CustomPollAlarm(BasePollAlarm):
    """拉取 自定义 告警, 并清洗告警相关属性用于匹配"""

    SOURCE_TYPE = 'CUSTOM'

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
        super(CustomPollAlarm, self).__init__()

    def pull_alarm(self):
        """拉取告警"""
        lock_polling(self.str_begin_time, self.str_end_time, self.delta_minutes, group="custom")

        # 从db中查询拉取告警的链接和请求方式
        app_info = get_custom_app_info()
        app_id = app_info.get('app_id', '')
        if app_info:
            params = {
                'begin_time__gte': self.str_begin_time,
                'begin_time__lte': self.str_end_time,
            }
            self.alarm_list = []
            try:
                if app_info.get('app_method') == 'post':
                    r = requests.post(app_info.get('app_url'), data=params)
                else:
                    r = requests.get(app_info.get('app_url'), params=params)
                resp = r.json()
            except Exception as e:
                handle_alarm_source_exception(app_id, e)
                # 请求异常时更新告警源信息
                logger.exception(
                    'BEGIN-END %s - %s \n%s:%s',
                    self.str_begin_time,
                    self.str_end_time[-8:],
                    app_info.get('app_method'),
                    app_info.get('app_url'))
            else:
                if isinstance(resp.get('data', None), (list, tuple)):
                    self.alarm_list = resp['data']
                    ip_list = self.get_alram_ip_list()
                    # 从配置平台获取 ip 所属的业务、集群、模块信息
                    self.cc_info_by_ips = get_cc_info_by_ips(ip_list)

                # 从告警源中没有拉取到告警，也要记录到db总
                if len(self.alarm_list) == 0:
                    handle_alarm_source_empty(app_id)
                else:
                    handle_alarm_source_success(app_id)

            logger.info(
                'BEGIN-END %s - %s (%s)',
                self.str_begin_time, self.str_end_time[-8:], len(self.alarm_list))

    # ===============================================================================
    # 清洗告警数据，默认拉取到的告警数据如下，可以根据实际的返回做调整
    # {
    # "ip": '10.0.0.1',      // 告警源IP，必须
    # "source_id": "12345",       // 告警源的告警ID，必须
    # "source_time": "12345",       // 告警发生的时间，格式：YYYY-MM-DD HH:mm:ss，必须
    # "alarm_type": "ping",     // 告警类型（按业务存储，不填则统一放到默认分类下），可选
    # "alarm_content": "FAILURE for production/HTTP on machine 10.0.0.1", // 告警详情，可选
    # }
    # ===============================================================================
    def get_alram_ip_list(self):
        ip_list = [data['ip'] for data in self.alarm_list]
        return ip_list

    def clean_host(self, alarm):
        """
        告警源IP,  IP需要录入到配置平台中
        """
        return alarm['ip']

    def clean_source_id(self, alarm):
        """
        告警源的告警ID,全局唯一
        """
        return str(alarm["source_id"])

    def clean_alarm_time(self, alarm):
        """
        告警发生的时间，格式：YYYY-MM-DD HH:mm:ss
        """
        return alarm['source_time']

    def clean_source_time(self, alarm):
        """
        告警发生的时间，格式：YYYY-MM-DD HH:mm:ss
        """
        return alarm['source_time']

    def clean_alarm_type(self, alarm):
        """
        告警类型
        """
        return list(monitors.lookup_alarm_type_list(
            [alarm['alarm_type']],
            cc_biz_id=0, source_type=self.SOURCE_TYPE,
            default="default",
        ))

    def clean_alarm_desc(self, alarm):
        """
        告警详情
        """
        return alarm['alarm_content']

    # ===============================================================================
    # 清洗蓝鲸相关的告警数据,如根据 ip 从配置平台中获取 ip 所属的集群、模块信息
    # ===============================================================================

    def clean_source_type(self, alarm):
        return self.SOURCE_TYPE

    def clean_alarm_source_id(self, alarm):
        return ''

    def clean_alarm_attr_id(self, alarm):
        return ''

    def clean_cc_biz_id(self, alarm):
        ip = self.clean_host(alarm)
        cc_info = self.cc_info_by_ips.get(ip, {})
        return cc_info.get('cc_biz_id', '')

    def clean_cc_topo_set(self, alarm):
        ip = self.clean_host(alarm)
        cc_info = self.cc_info_by_ips.get(ip, {})
        cc_topo_set_name = cc_info.get('cc_topo_set_name', '')
        return cc_topo_set_name.split(",") if cc_topo_set_name else []

    def clean_cc_app_module(self, alarm):
        ip = self.clean_host(alarm)
        cc_info = self.cc_info_by_ips.get(ip, {})
        cc_app_module_name = cc_info.get('cc_app_module_name', '')
        return cc_app_module_name.split(",") if cc_app_module_name else []

    def clean_cc_company_id(self, alarm):
        ip = self.clean_host(alarm)
        cc_info = self.cc_info_by_ips.get(ip, {})
        return cc_info.get('cc_company_id', '0')

    def clean_cc_plat_id(self, alarm):
        ip = self.clean_host(alarm)
        cc_info = self.cc_info_by_ips.get(ip, {})
        return cc_info.get('cc_plat_id', '')

    def push_alarm(self):
        """推送告警进行匹配"""
        super(CustomPollAlarm, self).push_alarm()
