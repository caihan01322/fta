# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta import constants
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import (FtaSolutionsAppAlarminstance,
                                FtaSolutionsAppAlarminstancelog)
from fta.utils import logging

logger = logging.getLogger("utils")


def update_alarm_instance_comment(alarm_instance_id, comment,
                                  step_name="", level=20, cover=True):
    """add alarm instance log"""
    logger.info(
        "$%s [%s][%s][%s]: %s",
        alarm_instance_id, step_name, level, cover, comment)
    if cover:
        session.query(FtaSolutionsAppAlarminstance)\
            .filter_by(id=alarm_instance_id).update({"comment": comment})
    session.execute(
        FtaSolutionsAppAlarminstancelog.__table__.insert(), [{
            "alarm_instance_id": alarm_instance_id,
            "content": comment,
            "step_name": step_name,
            "level": level,
            "time": arrow.utcnow().naive}])


def list_alarm_instance_log(alarm_instance_id, step_name="", level=20):
    """add alarm instance log by alarm_instance_id(and step_name)"""
    query = session.query(FtaSolutionsAppAlarminstancelog).filter(
        FtaSolutionsAppAlarminstancelog.alarm_instance_id == alarm_instance_id,
        FtaSolutionsAppAlarminstancelog.level >= level)
    if step_name:
        query = query.filter_by(step_name=step_name)
    return orm_2_dict(query)


def mark_alarm_instance_finished(alarm_instance_id, time):
    session.query(FtaSolutionsAppAlarminstance)\
        .filter_by(id=alarm_instance_id)\
        .update({"finish_time": arrow.get(time).format(
            constants.STD_ARROW_FORMAT)})
