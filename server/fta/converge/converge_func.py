# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
这个文件包含了收敛的几种模式
函数参数的统一说明：
:param incident: dict 当前事件的实例字典
:param alarm_instance: dict 当前告警的实例字典
:param match_alarm: [alarm_instance_id] 收敛事件相关的告警 ID 列表
:param created: True/False 是否是新创建的收敛事件
:param incident_def: dict 收敛的配置
"""

import datetime
import json
from collections import Counter

import arrow

from fta import constants
from fta.converge import CONTEXT
from fta.converge.incident import IncidentAlarmManager, IncidentManager
from fta.storage.cache import Cache
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppIncident
from fta.utils import get_list, hooks, lock, logging, people, scheduler, send_converge
from fta.utils.alarm_instance import (
    get_alarm_instance, list_alarm_instances_by_incident_id, list_other_alarm_instances
)
from fta.utils.monitors import get_description_by_alarm_type

redis_cache = Cache("redis")
logger = logging.getLogger(__name__)


def incident_skip(incident, alarm_instance, match_alarm,
                  created, incident_def):
    """
    成功后跳过

    触发规则后，如果有满足规则的其他告警自愈成功，则跳过当前告警。
    失败的话则继续自愈处理。

    可用于实现失败重试。
    """
    other_alarm_instances = list_other_alarm_instances(
        match_alarm, alarm_instance['id'])
    if not other_alarm_instances:
        logger.info('$%s not other_alarm_instances', CONTEXT.get('id'))
        return False
    for alarm_instance in other_alarm_instances:
        if alarm_instance['status'] in constants.INSTANCE_NOT_END_STATUS:
            return 'sleep'  # 等待的告警还在处理，继续等待
    for alarm_instance in other_alarm_instances:
        if (alarm_instance['status'] in constants.INSTANCE_END_STATUS) \
                and (alarm_instance['status'] not in constants.INSTANCE_FAILURE_STATUS):
            return 'skip'  # 等待的告警处理结束且非失败，跳过当前告警处理
    return False  # 等待的告警处理失败，不收敛


def incident_skip_approve(incident, alarm_instance, match_alarm, created, incident_def):
    """
    成功后跳过,失败时审批

    触发规则后，如果有满足规则的其他告警自愈成功，则跳过当前告警。
    失败的话则发送审批由用户判断是否继续执行自愈处理。
    """
    other_alarm_instances = list_other_alarm_instances(match_alarm, alarm_instance['id'])
    if not other_alarm_instances:
        logger.info('$%s not other_alarm_instances', CONTEXT.get('id'))
        return False
    result = incident_skip(incident, alarm_instance, match_alarm, created, incident_def)
    if result is False:
        return 'waiting'
    return result


def incident_pass(incident, alarm_instance, match_alarm, created, incident_def):
    """
    执行中跳过

    触发规则后，如果有满足规则的其他告警正在自愈，或刚结束自愈 5 分钟，
    则跳过当前告警。

    可用于避免重复告警
    """
    other_alarm_instances = list_other_alarm_instances(match_alarm, alarm_instance['id'])
    if not other_alarm_instances:
        logger.info('$%s not other_alarm_instances', CONTEXT.get('id'))
        return False
    for alarm_instance in other_alarm_instances:
        if not alarm_instance.get('end_time'):
            return 'skip'  # 等待的告警正在执行，收敛
        alarm_time = alarm_instance['source_time']
        if alarm_instance['end_time'] > (alarm_time - datetime.timedelta(minutes=5)):
            return 'skip'  # 等待的告警结束不超过5分钟，收敛
    return False


def incident_wait(incident, alarm_instance, match_alarm, created, incident_def):
    """
    执行中等待

    触发规则后，如果有满足规则的其他告警正在自愈，
    则等其他告警自愈完成后再继续处理当前告警。

    可用户互斥的告警处理，或有先后顺序依赖的告警处理。
    """
    other_alarm_instances = list_other_alarm_instances(match_alarm, alarm_instance['id'])
    if not other_alarm_instances:
        logger.info('$%s not other_alarm_instances', CONTEXT.get('id'))
        return False
    for alarm_instance in other_alarm_instances:
        if not alarm_instance.get('end_time'):
            return 'sleep'  # 等待的告警正在执行，等待
    return False


def incident_notify(incident, alarm_instance, match_alarm, created, incident_def):
    """
    触发通知

    触发规则后，不影响处理，发送通知。

    可用于配置阀值告知。
    """
    verifier = people.get_verifier(alarm_instance['id'])
    if created:
        try:
            send_converge.notify(
                verifier,
                alarm_instance['cc_biz_id'],
                alarm_instance['alarm_type'],
                len(match_alarm)
            )
        except Exception as e:
            logger.error("$%s %s", CONTEXT.get('id'), e)
    return False  # 继续跑原有逻辑，不收敛


def incident_defense(incident, alarm_instance, match_alarm, created, incident_def):
    """
    异常防御需审批

    触发规则后，会打电话通知用户，让用户审批决定是否收敛。
    如果超时未审批则会收敛跳过，不处理。
    如果 30 分钟内发生相同规则的异常防御事件，会被汇集到同一个收敛事件中。

    可用于防御大规模告警的异常，如发布未屏蔽，网络问题，机房故障等等。
    通过人工判断大量的告警是否需要处理。
    """

    # bug fix, check match_alarm
    other_alarm_instances = list_other_alarm_instances(match_alarm, alarm_instance['id'])
    if not other_alarm_instances:
        logger.info('$%s not other_alarm_instances', CONTEXT.get('id'))
        return False

    # 获取 30 分钟内的异常防御事件
    redis_incident_key = 'converge_defense_%s' % incident['dimension']
    logger.info('redis_incident_key: %s', redis_incident_key)
    incident_id = redis_cache.get(redis_incident_key)
    logger.info('incident_id: %s', incident_id)
    # 如果 30 分钟内有相同维度的事件，则关联事件与告警
    if incident_id:
        IncidentAlarmManager.connect(incident_id, [alarm_instance['id']])
        IncidentManager.converge(incident_id)
        logger.info(
            "$%s converge_defense(%s) %s find %s",
            alarm_instance['id'],
            incident['id'], incident['dimension'], incident_id)
    # 否则把当前收敛当做第一条传承下去
    else:
        incident_id = incident['id']
    redis_cache.set(redis_incident_key, incident_id)
    redis_cache.expire(redis_incident_key, 30 * 60)  # 延期 30 分钟

    verifier = people.get_verifier(alarm_instance["id"])
    # 以发送人(第一位)/业务为key作通知收敛
    key = "incident_%s-%s" % (verifier[0] if verifier else "", alarm_instance['cc_biz_id'])
    if lock.redis_lock(key, 30 * 60, extend=True):
        send_converge.defense(
            ','.join(verifier),
            alarm_instance['cc_biz_id'],
            alarm_instance['alarm_type'],
            len(match_alarm))
    return 'waiting'  # 等待审批，不做收敛处理，在 run_solution 判断是否审批通过


def incident_relevance(incident, alarm_instance, match_alarm, created, incident_def):
    """
    汇集相关事件

    触发规则后，不影响处理，只是把满足收敛规则的告警汇集在一起展示为同一个事件。

    在界面上把相关的告警汇集在一起展示，能更好自定义告警间的关联性。
    """
    return False  # 不收敛，关联事件，不影响处理


def incident_trigger(incident, alarm_instance, match_alarm, created, incident_def):
    """
    收敛后处理

    与其他收敛规则相反。未触发规则时，配置的告警类型不处理。触发规则后，才开始处理。

    可以等告警数量超过一定阀值后才处理告警。
    或者一定时间内同时出现 A 告警和 B 告警的时候再开始处理。
    """
    if created:  # 对于一个收敛事件，只不收敛一次
        return False  # 不收敛
    return 'skip'  # 不符合 trigger 类型触发条件时，跳过当前告警处理


def incident_collect(incident, alarm_instance, match_alarm, created, incident_def):
    """
    超出后汇总

    触发规则后，超出数量的告警将会收敛不处理，并发送汇总通知

    如果告警在一定时间内不断出现，超过某个阀值可以认为其有异常，
    则不再自愈，触发通知。
    """
    if created:
        verifier = people.get_verifier(alarm_instance["id"])
        first_time = get_alarm_instance(sorted(match_alarm)[0])["begin_time"]
        time = arrow.get(first_time).replace(minutes=int(incident_def['timedelta']) + 5).naive
        scheduler.run(
            module='fta.converge.converge_func',
            function='_end_incident_collect',
            args=(verifier, incident['id']),
            time=time)
    if len([a_id for a_id in match_alarm if a_id <= alarm_instance['id']]) >= incident_def['count']:
        return 'skip'
    return False


def _end_incident_collect(verifier, incident_id):
    """
    发送收敛汇总的通知
    :param incident_id: 收敛事件的 ID
    """

    # 获取所有事件关联的alarm_instance_list
    alarm_instance_list = list_alarm_instances_by_incident_id(incident_id)

    # 拼接收敛事件中的全部告警类型
    alarm_type_list = list(set([
        get_description_by_alarm_type(
            alarm_instance['alarm_type'],
            cc_biz_id=alarm_instance['cc_biz_id'],
            default=alarm_instance['alarm_type'],
        ) for alarm_instance in alarm_instance_list
    ]))

    # 拼接收敛事件中的全部业务
    cc_biz_id_list = list(set([str(alarm_instance['cc_biz_id']) for alarm_instance in alarm_instance_list]))

    send_converge.collect(verifier, cc_biz_id_list, alarm_type_list, len(alarm_instance_list), incident_id)


def incident_universality(incident, alarm_instance, match_alarm,
                          created, incident_def):
    """
    共性分析

    触发规则后，将会分析告警的共性特点。
    超过两个业务会触发通知分析结果。

    对于异常的批量告警，帮助定位告警的共性特点。
    """
    scheduler.run(
        module="fta.converge.converge_func",
        function="_end_incident_universality",
        args=(incident["id"],),
        time=arrow.utcnow().replace(minutes=5).naive,
        id_=incident["id"])
    return False  # 仅作共性分析，不收敛


def _end_incident_universality(incident_id, re_universality=False):
    """
    共性告警的结束通知
    :param re_universality: 标识是否为补录
    """
    dimensions = {}

    # 获取所有事件关联的alarm_instances
    alarm_instance_list = list_alarm_instances_by_incident_id(incident_id)

    incident_begin_time = session.query(FtaSolutionsAppIncident).filter_by(id=incident_id).one().begin_time

    # 得出所有 filter dimension 的 set
    for alarm_instance in alarm_instance_list:
        origin_alarm = json.loads(alarm_instance["origin_alarm"])
        for dimension in constants.UNIVERSALITY_DIMENSION_KEY.keys():
            if not origin_alarm["_match_info"].get(dimension):
                continue
            dimension_value = [
                constants.CC_PROPERTY_NAME.get(dimension, {}).get(value, value)
                for value in get_list(origin_alarm["_match_info"][dimension])
            ]
            dimensions.setdefault(dimension, Counter()).update(dimension_value)

    # 计算出共性维度
    common_dimension = {}
    for dimension, dimension_counter in dimensions.items():
        sorted_dimension_counter = sorted(dimension_counter.items(), key=lambda x: x[1], reverse=True)
        for dimension_value, dimension_count in sorted_dimension_counter:
            dimension_rate = dimension_count * 100 / len(alarm_instance_list)
            # 认为占比34%以上的维度值为共性
            if dimension_rate >= 34:
                common_dimension.setdefault(dimension, []).append((dimension_value, dimension_rate))

    # 获取共性维度的相关事件
    universality_analyze = hooks.HookManager("converge_func").get("universality_analyze", lambda *args, **kwargs: [])
    related_event_list = universality_analyze(incident_id, common_dimension, incident_begin_time, re_universality)
    logger.info(
        u"共性告警(incident_id: %s)的相关事件ID: %s", incident_id,
        ",".join([str(i.event_raw_id) for i in related_event_list]))

    # 发送共性告警通知
    send_converge.universality(alarm_instance_list, common_dimension, related_event_list, incident_id, re_universality)


def incident_pre_converge(match_info, converge_conf):
    return None


def run(func_name, *args, **kwargs):
    """根据函数名决定运行真正的函数"""
    real_func_name = "incident_%s" % func_name
    hook = hooks.HookManager("converge_func")
    try:
        func = hook.get(real_func_name)
    except BaseException:
        func = globals()[real_func_name]
    result = func(*args, **kwargs)
    logger.info("$%s run incident_%s: %s", CONTEXT.get("id"), func_name, result)
    return result
