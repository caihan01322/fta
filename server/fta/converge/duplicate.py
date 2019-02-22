# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

import arrow

from fta import constants
from fta.storage.cache import Cache
from fta.utils import get_md5, logging, scheduler, send_message
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.instance_log import mark_alarm_instance_finished

redis = Cache("redis")

logger = logging.getLogger("converge")


def _add_point(dimensions, interval, period, time):
    """
    :param dimensions: dict {"dimension_name": "dimension_value"}
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    :return key: redis_key
    :return end: end index of time window
    :return score: score of time window
    """
    score = arrow.get(time).timestamp / interval
    start = arrow.utcnow().replace(days=-1).timestamp / interval
    end = arrow.utcnow().replace(seconds=-interval * period - interval / 2).timestamp / interval
    key = get_md5(json.dumps(dimensions))
    redis.zadd(key, **{str(score): score})
    redis.zremrangebyscore(key, start, end)
    redis.expire(key, interval * period * 2)
    return key, end, score


def _add_new_point(dimensions, interval, period, count, time):
    """
    :param dimensions: dict {"dimension_name": "dimension_value"}
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    """
    # only not converged item will be added into zset
    key = "new_point" + get_md5(json.dumps(dimensions))
    score = arrow.get(time).timestamp

    if redis.ttl(key) > 0:
        # update expire time
        redis.expire(key, interval * period + 86400)
        # del old data
        redis.zremrangebyscore(key, 0, score - 86400)
    else:
        redis.zadd(key, **{str(score): score})
        redis.expire(key, interval * period + 86400)
        # do not converge
        return True

    if len(redis.zrangebyscore(key, score - interval * period + 1, score, withscores=False)) < count:
        redis.zadd(key, **{str(score): score})
        # do not converge
        return True

    # do converge
    return False


def _add_new_point_old(dimensions, interval, period, count, time):
    """
    :param dimensions: dict {"dimension_name": "dimension_value"}
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    """
    key = "new_point_cnt" + get_md5(json.dumps(dimensions))
    old_count = redis.get(key)
    if old_count:
        # already has alarm in this dimension
        if int(count) > int(old_count):
            ttl_left = redis.ttl(key)
            if ttl_left > 0:
                # not expired, add count
                logger.info(ttl_left)
                redis.incr(key, 1)
                # reset ttl time
                redis.expire(key, ttl_left)
            # do not converge
            return True
        # do converge
        return False
    else:
        # do not converge
        redis.setex(key, interval * period, 1)
        return True


def _get_start_key(key):
    return "%s_id" % key


def _get_marked_key(key):
    return "%s_id_marked" % key


def check_new_duplicate(dimensions, interval=60, period=5, count=1, time=None):
    """
    :param dimensions: dict {"dimension_name": "dimension_value"}
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    """
    time = time or arrow.utcnow().timestamp
    try:
        result = _add_new_point(dimensions, interval, period, count, time)
    except Exception as e:
        logger.exception(e)
        return True
    return result


def check_alarm_desc(alarm_def_id, dimensions, alarm_desc, interval=60, period=15):
    """
    :param alarm_desc: alarm content
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    """
    if not alarm_desc:
        return True
    try:
        key = "duplicate_raw_%s_%s_%s" % (
            alarm_def_id,
            get_md5(json.dumps(dimensions)),
            get_md5(alarm_desc)
        )
        if redis.ttl(key) > 0:
            # update expire time
            redis.expire(key, interval * period)
            return False
        else:
            redis.set(key, "__lock__", interval * period, nx=True)
            # do not converge
            return True
    except BaseException:
        return True


def check_duplicate(dimensions, interval=60, period=15, time=None, check_finished=False, point_id=None):
    """
    decide whether converged by given dimensions
    :param dimensions: dict {"dimension_name": "dimension_value"}
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    :param check_finished: default False,
                           if True will send alarm finished notice
    :param point_id: if check_finished is True, must have point_id
    :return bool: True means do not converge
                  False means do converge
    """
    time = time or arrow.utcnow().timestamp
    key, start, end = _add_point(dimensions, interval, period, time)
    result = len(redis.zrangebyscore(key, start, end, withscores=False)) <= 1
    if check_finished is True and point_id:
        if result is False:
            call_check_finished(key, interval, period, time)
            redis.expire(_get_start_key(key), 24 * 60 * 60)
        else:
            redis.set(_get_start_key(key), point_id, 24 * 60 * 60)
            logger.info("$%s set check finished key: %s", point_id, _get_start_key(key))
    return result


def check_shake(dimensions, interval=60, period=5, count=2, time=None):
    """
    decide whether converged by given dimensions
    :param dimensions: dict {"dimension_name": "dimension_value"}
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param count: check period*interval seconds's point count >= count
    :param time: point's time
    :return bool: True means do not converge
                  False means do converge
    """
    time = time or arrow.utcnow().timestamp
    key, start, end = _add_point(dimensions, interval, period, time)
    return len(redis.zrangebyscore(key, start, end, withscores=False)) > count


def call_check_finished(key, interval, period, time):
    """
    call check_finished by scheduler
    :param key: redis_key of alarm
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    """
    timestamp = arrow.utcnow().replace(tzinfo="utc").timestamp
    check_time = timestamp - timestamp % interval + interval * (period + 1)
    logger.info("check_finished_scheduler at %s", arrow.get(check_time).format(constants.STD_ARROW_FORMAT))
    scheduler.run(
        module="fta.converge.duplicate",
        function="check_finished_scheduler",
        kwargs={"key": key, "interval": interval, "period": period, "time": time},
        time=check_time,
        id_="%s%s" % (key, check_time))


def check_finished_scheduler(key, interval, period, time):
    """
    real call check_finished. if finished, send notify
    :param key: redis_key of alarm
    :param interval: point's interval (seconds)
    :param period: check period*interval seconds
    :param time: point's time
    """
    end = arrow.utcnow().timestamp / interval
    start = arrow.utcnow().replace(seconds=-interval * period - interval / 2).timestamp / interval

    if len(redis.zrangebyscore(key, start, end, withscores=False)) == 0:
        event_id = redis.get(_get_start_key(key))
        if not event_id:
            if not redis.get(_get_marked_key(key)):
                return logger.warning("unknow check_finished key: %s" % key)
            return logger.info("handled check_finished key: %s", key)
        logger.info("$%s mark finished")

        # mark key has been finished
        redis.delete(_get_start_key(key))
        redis.set(_get_marked_key(key), event_id, 24 * 60 * 60)

        alarm_instance = get_alarm_instance(event_id=event_id)

        # mark alarm_instance finished
        mark_alarm_instance_finished(alarm_instance["id"], time)

        # mark alarm_instance status to finished
        alarm_instance["status"] = "finished"

        send_message.notify_info(alarm_instance)
