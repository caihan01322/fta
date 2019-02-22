# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import (FtaSolutionsAppAlarminstance,
                                FtaSolutionsAppIncidentalarm)
from fta.utils import logging
from fta.utils.i18n import i18n

logger = logging.getLogger("utils")


def make_event_id(source_type, source_id):
    """
    create a event_id for alarm_instance by source_type and source_id
    :param source_type: alarm's source system
    :param source_id: alarm's id in source system
    :return event_id: string, length should by small than 255, limited by MySQL
    """
    if len(source_type) + len(source_id) > 200:
        logger.error(
            "source_type: %s source_id too long (%s): %s",
            source_type, len(source_id), source_id)
    return '%s%s' % (source_type, source_id)


def list_other_alarm_instances(instance_id_list, instance_id):
    """
    list alarm_instance by given list of instance_id
    which is big then given instance_id
    :param instance_id_list: list of instance_id
    :param instance_id: filter by bigger this instance_id
    :return alarm_instance_list: alarm_instance's list
                                 alarm_instance is dict
    """
    instance_id_list = [
        e_id for e_id in instance_id_list if e_id < instance_id]
    return list_alarm_instances(instance_id_list) if instance_id_list else []


def list_alarm_instances(instance_id_list):
    """
    list alarm_instance by given list of instance_id
    :param instance_id_list: list of instance_id
    :return alarm_instance_list: alarm_instance's list
                                 alarm_instance is dict
    """
    alarm_instance_list = session.query(FtaSolutionsAppAlarminstance) \
        .filter(FtaSolutionsAppAlarminstance.id.in_(instance_id_list))
    return orm_2_dict(alarm_instance_list)


def list_alarm_instances_by_incident_id(incident_id):
    """
    list alarm_instance by given incident_id
    :param incident_id: incident's id
    :return alarm_instance_list: alarm_instance's list
                                 alarm_instance is dict
    """
    alarm_instance_ids = [
        ia.alarm_id
        for ia in session.query(
            FtaSolutionsAppIncidentalarm).filter_by(
            incident_id=incident_id).all()]
    return list_alarm_instances(alarm_instance_ids)


def list_alarm_instances_by_incident_id_with_limit(incident_id, limit=5):
    """
    list alarm_instance by given incident_id with limit and desc order
    :param incident_id: incident's id
    :param limit: fetch number
    :return: alarm_instance_list: alarm_instance's list
                                 alarm_instance is dict
    """
    alarm_instance_ids = [
        ia.alarm_id for ia in session.query(FtaSolutionsAppIncidentalarm).
        filter_by(incident_id=incident_id).
        order_by(FtaSolutionsAppIncidentalarm.id.desc()).limit(limit)
    ]

    return list_alarm_instances(alarm_instance_ids)


def get_alarm_instance(instance_id=None, event_id=None):
    """
    get alarm_instance by instance_id or event_id
    must give a instance_id or event_id
    :param instance_id: alarm_instance's id
    :param event_id: alarm's event_id create by function "make_event_id"
    :return alarm_instance: alarm_instance's dict
    """
    assert instance_id or event_id
    if instance_id:
        try:
            alarm_instance = session.query(FtaSolutionsAppAlarminstance) \
                .filter_by(id=instance_id).one()
        except Exception as e:
            logger.error("alarm_instance id %s: %s", instance_id, e)
            raise
    elif event_id:
        try:
            alarm_instance = session.query(FtaSolutionsAppAlarminstance) \
                .filter_by(event_id=event_id).one()
        except Exception as e:
            logger.error("alarm_instance event_id %s: %s", event_id, e)
            raise
    # set alarm language
    i18n.set_biz(alarm_instance.cc_biz_id)

    return orm_2_dict(alarm_instance)
