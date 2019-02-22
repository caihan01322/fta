# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import hashlib

import arrow

from fta.converge import CONTEXT, converge_func
from fta.converge.dimension import DimensionHandler
from fta.converge.incident import IncidentManager
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppAlarminstance, FtaSolutionsAppIncidentalarm
from fta.utils import extended_json, func_timer, logging

logger = logging.getLogger('converge')


class IncidentDefHandler(object):
    """handle converge incident by incident_def dict && alarm_instance dict"""

    def __init__(self, incident_def, alarm_instance):
        """
        :param incident_def: dict
            {
                'id': int,  # incident_def_id
                'cc_biz_id':  int,  # biz_id
                'exclude_cc_biz_id':  list,  # exclude biz_id_list
                'alarm_type': [alarm_type, ],
                'timedelta': int,  # minutes
                'condition': dict,  # {"dimension_key": ["dimension_value", ]}
                'count': int,  # how many alarm will triggle
                'incident_func' function_name,  # see converge_func.py
                'description': string,  # incident_def's description
            }
        :param alarm_instance: alarm_instance_dict
        """

        # check whether illegal by incident_def's condition
        self.is_illegal = False
        if not incident_def['condition']:
            self.is_illegal = True
            self.incident_def = {'description': 'illegal incident_def'}
            logger.warning(
                "$%s illegal incident_def #%s: %s",
                alarm_instance['id'],
                incident_def['id'],
                incident_def['condition'])
            return

        # check timedelta and count
        if incident_def['timedelta'] <= 0:
            self.incident_def = {'description': 'illegal incident_def, timedelta <= 0'}
            self.is_illegal = True
            logger.warning(
                "$%s illegal incident_def #%s: timedelta %s <= 0",
                alarm_instance['id'],
                incident_def['id'],
                incident_def['timedelta'])
            return

        if incident_def['count'] <= 0:
            self.incident_def = {'description': 'illegal incident_def, count <= 0'}
            self.is_illegal = True
            logger.warning(
                "$%s illegal incident_def #%s: count %s <= 0",
                alarm_instance['id'],
                incident_def['id'],
                incident_def['count'])
            return

        # get converge define info && alarm info
        self.incident_def = incident_def
        self.alarm_instance = alarm_instance
        self.alarm_base_info = extended_json.loads(
            alarm_instance['origin_alarm'])['_match_info']
        self.alarm_base_info['solution'] = extended_json.loads(
            alarm_instance['snap_solution'])['id']

        # incident_range
        self.start_time = arrow.get(self.alarm_instance['source_time']).replace(
            tzinfo="utc").replace(minutes=-1 * int(self.incident_def['timedelta']))
        self.start_timestamp = self.start_time.timestamp

        # incident_description
        self.dimension = self.get_dimension(safe_length=128)  # orm field length

    def run(self):

        if self.is_illegal:
            return False

        match_alarm_list = []
        incident_manager = IncidentManager({
            "incident_def_id": self.incident_def['id'],
            "cc_biz_id": self.alarm_instance['cc_biz_id'],
            "dimension": self.dimension,
            "incident_type": self.incident_def['incident_func'],
            "description": self.incident_def['description'],
        }, match_alarm_list)
        incident = incident_manager.get_incident(self.start_time.naive)
        # check by incident_def['cc_biz_id']
        if self.check_cc_biz_id():
            # check by incident_def['exclude_cc_biz_id']
            if self.check_exclude_cc_biz_id():
                # check by incident_def['alarm_type']
                if self.check_alarm_type():
                    # get matched alarm by incident_def['timedelta'] &&
                    # get matched alarm by incident_def['condition']
                    match_alarm_list.extend(self.get_match_alarm(incident))
                else:
                    logger.info("$%s unmatch alarm_type", CONTEXT.get('id'))
            else:
                logger.info("$%s unmatch exclude_cc_biz_id", CONTEXT.get('id'))
        else:
            logger.info("$%s unmatch cc_biz_id", CONTEXT.get('id'))
        # check by incident_def['count']
        match_alarm_count = len(match_alarm_list)
        if not incident and match_alarm_count > int(self.incident_def['count']):
            # create incident record
            logger.info("$%s create incident", CONTEXT.get('id'))
            try:
                incident = incident_manager.create_incident(self.start_time.naive)
            except Exception as error:
                logger.exception("create incident failed：%s", error)
                return False
        if not incident:
            return False

        incident_manager.converge(incident['id'])
        incident_manager.connect_alarm()
        # run converge_func by incident_def['converge_func']
        return converge_func.run(
            self.incident_def['incident_func'],
            incident, self.alarm_instance, match_alarm_list,
            incident_manager.is_created, self.incident_def)

    def _get_dimension_value(self, value):
        """cut off dimension_value to avoid dimension-string too long"""
        if isinstance(value, list):
            if len(value) >= 4:
                h = hashlib.md5(unicode(value)).hexdigest()[:5]
                value = [value[0], "%s.%s" % (h, len(value) - 2), value[-1]]
            dimension_value = ','.join(map(str, value))
        else:
            dimension_value = value
        return dimension_value

    def get_dimension(self, safe_length=0):
        """
        get std dimension for DimensionHandler from incident_def['condition']
        """
        incident_dimension = ["#%s" % self.incident_def['id']]
        for key, values in self.incident_def['condition'].items():
            # replace "self" to real value
            for index, value in enumerate(values):
                if value == 'self':
                    values[index] = self.alarm_base_info[key]
                incident_dimension.append("|%s:%s" % (key, self._get_dimension_value(values[index])))
        dimension = "".join(incident_dimension)
        if not safe_length or len(dimension) <= safe_length:
            return dimension

        sha1 = hashlib.sha1(dimension)
        dimension = "!sha1#%s" % sha1.hexdigest()
        return dimension[:safe_length]

    def check_cc_biz_id(self):
        """check by incident_def['cc_biz_id']"""
        return str(self.incident_def['cc_biz_id']) == "0" \
            or str(self.incident_def['cc_biz_id']) == str(self.alarm_base_info['cc_biz_id'])

    def check_exclude_cc_biz_id(self):
        """check by incident_def['exclude_cc_biz_id']"""
        return str(self.alarm_base_info['cc_biz_id']) not in self.incident_def['exclude_cc_biz_id']

    def check_alarm_type(self):
        """check by incident_def['alarm_type']"""
        return set(self.alarm_base_info['alarm_type']) & set(self.incident_def['alarm_type'])

    @func_timer.timer
    def get_match_alarm(self, incident=None):
        """
        get matched alarm by
        incident_def['timedelta'] && incident_def['condition']
        """
        event_id_list = DimensionHandler(
            self.dimension,
            self.incident_def['condition'],
            self.start_timestamp).get_by_condition()
        match_alarm_id_list = [
            a[0] for a in session.query(
                FtaSolutionsAppAlarminstance.id,
            ).filter(
                FtaSolutionsAppAlarminstance.event_id.in_(event_id_list),
            ).all()
        ] if event_id_list else []
        if match_alarm_id_list:
            queries = session.query(
                FtaSolutionsAppIncidentalarm.alarm_id
            ).filter(
                FtaSolutionsAppIncidentalarm.alarm_id.in_(match_alarm_id_list, )
            )
            if incident:
                queries = queries.filter(FtaSolutionsAppIncidentalarm.incident_id != incident['id'], )
            converged_alarm_id_list = [a[0] for a in queries]
            match_alarm_id_list = list(set(match_alarm_id_list) - set(converged_alarm_id_list), )
        logger.info(
            "$%s dimension alarm list: %s, %s, %s",
            CONTEXT.get('id'), self.dimension,
            match_alarm_id_list, event_id_list)
        return match_alarm_id_list
