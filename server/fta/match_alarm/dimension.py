# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta import constants, settings
from fta.storage.cache import Cache
from fta.utils import extended_json, logging

logger = logging.getLogger('match_alarm')
redis = Cache("dimension")


class DimensionCalculator(object):
    DimensionExpireHours = getattr(settings, "DIMENSION_EXPIRE_HOURS", 24)

    def __init__(self, alarminstance):
        self.alarminstance = alarminstance

    def calc_dimension(self):
        event_id = str(self.alarminstance['event_id'])
        score = arrow.get(self.alarminstance['source_time']).replace(tzinfo="utc").timestamp
        try:
            origin_alarm = extended_json.loads(self.alarminstance['origin_alarm'], )
        except (TypeError, ValueError, KeyError) as err:
            logger.warning("origin alarm of instance warning: %s", err)
            return
        alarm_base_info = origin_alarm['_match_info']
        for dimension in constants.ALARM_DIMENSION_KEY.keys():
            values = alarm_base_info.get(dimension) or ""
            if not isinstance(values, (list, set)):
                values = [values]
            for value in values:
                self.add_id_by_kv(dimension, value, event_id, score)
            self.del_expire(dimension)

    def add_id_by_kv(self, key, value, event_id, score):
        key = "%s_%s" % (key, value)
        kwargs = {event_id: score}
        redis.zadd(key, **kwargs)
        redis.lpush('zset_key_list', key)
        logger.info("$%s %s save dimension key: %s", event_id, score, key)

    def del_expire(self, dimension):
        redis.zremrangebyscore(
            dimension,
            arrow.utcnow().replace(years=-1).timestamp,
            arrow.utcnow().replace(hours=-self.DimensionExpireHours).timestamp)
