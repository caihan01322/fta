# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
The priority calculation for alarminstance in the "Ready To Converge" queue

: priority aspects order:
    1. by solution_type
        if solution has more meaningful action, then higher

    2. by alarm_type
        if alarm_type is more serious/severe, then higher priority

    3. by source_type

    4. by cc_biz_id
        if biz is high star, then higher

    5. by app module
        if module is critical , then higher

    6. by real time alarm frequency
        if the same alarm is repeating itself, then lower priority

: value calculation:
    Use beanstalkd priority(ranking):
    most urgent: 0 ~ least urgent: 2**32 - 1 = 4294967295.
    Set default is HIGHEST, and multiply the weighting of each aspects
    Firstly classify each aspects to a category,
    and then use the weighting dict
"""

import json

from fta import constants
from fta.storage.cache import Cache
from fta.utils import logging

logger = logging.getLogger('match_alarm')
redis_cache = Cache('redis')

HIGHEST_PRIORITY = 1
LOWEST_PRIORITY = 2 ** 31 - 1  # limit of mysql int column. beanstalk is 2*32

# weighting value should be updated according to any fields update
WEIGHTING_ASPECT_FIELDS = {
    'solution_type': {
        1: [  # advanced
            'diy', 'ijobs', 'uwork', 'uwork_then_ijobs'
        ],
        5: [  # medium
            'analyze'
        ],
        10: [  # simple, other
        ],
    },
    'alarm_type': {
        1: [  # base
            'ping', 'agent',
            'disk-readonly', 'disk-readonly-full', 'disk-full',
            'port-missing', 'process-missing',
            'clock-unsync', 'os-restart',
            'memory-full', 'cpu-high', 'raid'
        ],
        4: [  # customized
            'customized', 'core-dumped'
        ],
        8: [  # biz
            'online', 'login', 'register', 'custom',
            'cpu', 'mem', 'disk', 'net', 'keyword',
            'leaf-biz-watchman', 'JungleAlert', 'location'
        ],
        9: [  # other
        ]
    },
    'source_type': {
        1: [
            ''
        ],
        2: [
            ''
        ],
        3: [
            ''
        ],
        4: [
            'ALERT'
        ],
    },
    'cc_biz_id': {
        1: [  # infra means infrastructure(cc,ijobs,bk,gse...)
        ],
        2: [  # high_start
        ],
        3: [  # mobile
        ],
        4: [  # normal other
        ]
    },
    'app_module': {
        1: [  # critical
        ],
        2: [  # normal
        ]
    },
}

FREQUENCY = {  # amount in 10 minutes
    1: 1,
    5: 2,
    10: 3,
    20: 5,
    50: 8,
    100: 10,
    200: 20,
    500: 100,
    1000: 200,
    2000: 1000,
}


class PriorityCalculator(object):
    def __init__(self, alarminstance):
        """alarminstance必须是字典格式，可以使用orm_2_dict获取"""
        self.alarminstance = alarminstance

    @property
    def priority(self):
        pri = self.calc_aspect_priority() * self.calc_frequency_priority()
        return min(LOWEST_PRIORITY, pri)  # pri should be (0, lowest)

    def calc_aspect_priority(self):
        """
        :note: Calculation must be very fast, to speed up converge queue
        :return: calculate a priority according to many aspects of a alarm
        """
        pri = HIGHEST_PRIORITY
        aspects = {}
        for aspect, weights in WEIGHTING_ASPECT_FIELDS.iteritems():
            weighting = HIGHEST_PRIORITY
            for weight, values in weights.iteritems():
                if self.alarminstance.get(aspect, '--None--') in values:
                    weighting = weight
                    break
                elif not values:
                    weighting = max(weighting, weight)
            aspects[aspect] = weighting
            pri = pri * weighting

        logger.info("$%s aspect priority is %s, detail: %s", self.alarminstance['event_id'], pri, json.dumps(aspects))
        return pri

    def calc_frequency_priority(self):
        """Currently calculate amount of same alarmdef for frequency
        Note: Time window is frozen set of natural 10 min like (6:10~6:20)
        The reason of using natural time window instead of sliding time window:
            1. Reset to default after 10 min,
                so that if a alarm def is flooding,
                there're still some alarm in every 10 min,
                otherwise all alarms may be Qos ignored.
            2. Easier to implement using redis, easy for maintain.
        """

        # use begin_time, not source_time
        # because we just care current fta system load
        time_key = "alarm_freq(ad#{})_10_min_{}".format(
            self.alarminstance['alarm_def_id'],
            self.alarminstance['begin_time'].strftime(constants.STD_DT_FORMAT)[:-4]
        )  # like '2015-01-21 10:1'

        redis_cache.sadd(time_key, self.alarminstance['event_id'])
        redis_cache.expire(time_key, 60 * 30)  # remove after 30 min
        amount = redis_cache.scard(time_key)

        for threshold in sorted(FREQUENCY.keys(), reverse=True):
            if amount >= threshold:
                pri = FREQUENCY[threshold]
                break
        logger.info("{} --->>> {}, freq pri is {}".format(time_key, amount, pri))

        return pri  # if freq is too small, return min threshold
