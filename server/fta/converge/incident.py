# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import random
import time

import arrow
from sqlalchemy.exc import IntegrityError

from fta import constants
from fta.converge import CONTEXT
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppIncident, FtaSolutionsAppIncidentalarm
from fta.utils import logging

logger = logging.getLogger('converge')


class IncidentManager(object):

    def __init__(self, incident_dict, match_alarm_id_list):
        self.incident_dict = incident_dict
        self.match_alarm_id_list = match_alarm_id_list
        self.is_created = False
        self.incident = None

    def create_incident(self, start_time=None):
        self.incident = self._get_or_create_incident()
        if start_time and self.incident.begin_time < start_time:
            logger.info(
                "incident end by start_time %s (%s < %s)", self.incident.id, self.incident.begin_time, start_time
            )
            self.end_incident_by_id(self.incident.id)
            self.incident = self._get_or_create_incident()
        return orm_2_dict(self.incident)

    @classmethod
    def get_fixed_dimension(cls, dimension):
        return "%s fixed at %s %s" % (
            dimension,
            arrow.utcnow().format(constants.STD_ARROW_FORMAT),
            random.randint(100, 999)
        )

    @classmethod
    def _end_incident_by_id(cls, incident_id, fixed_dimension):
        try:
            result = session.query(FtaSolutionsAppIncident).filter_by(id=incident_id).update({
                "end_time": arrow.utcnow().naive,
                "dimension": fixed_dimension
            })
            logger.info("$%s incident end %s: %s", CONTEXT.get("id"), result, fixed_dimension)
            return result
        except IntegrityError:
            logger.warning("$%s %s fixed by other", CONTEXT.get("id"), incident_id)

    @classmethod
    def end_incident_by_id(cls, incident_id):
        logger.info("incident end by id %s", incident_id)
        incident = session.query(
            FtaSolutionsAppIncident).filter_by(id=incident_id).one()
        if not incident.end_time:
            fixed_dimension = cls.get_fixed_dimension(incident.dimension)
            try:
                return cls._end_incident_by_id(incident.id, fixed_dimension)
            except BaseException:
                return cls._end_incident_by_id(incident.id, fixed_dimension)
        logger.info("incident %s already end at %s", incident_id, incident.end_time)
        return None

    def _insert_incident(self):
        try:
            session.execute(
                FtaSolutionsAppIncident.__table__.insert(), [dict(
                    incident_def_id=self.incident_dict['incident_def_id'],
                    cc_biz_id=self.incident_dict['cc_biz_id'],
                    dimension=self.incident_dict['dimension'],
                    description=self.incident_dict['description'],
                    content=self.incident_dict.get('context', "{}"),
                    last_check_time=arrow.utcnow().naive,
                    begin_time=arrow.utcnow().naive,
                    end_time=None,
                    incident_type=self.incident_dict['incident_type'],
                    is_visible=True)]
            )
        except IntegrityError:
            self.is_created = False
        else:
            self.is_created = True

    def get_incident(self, start_time=None):
        try:
            incident = session.query(FtaSolutionsAppIncident).filter_by(dimension=self.incident_dict['dimension']).one()
        except Exception:
            incident = None
        if incident and start_time and incident.begin_time < start_time:
            logger.info("incident end by start_time %s (%s < %s)", incident.id, incident.begin_time, start_time)
            self.end_incident_by_id(incident.id)
            incident = None
        self.incident = incident
        if incident:
            return orm_2_dict(self.incident)
        return {}

    def _get_or_create_incident(self):
        self.is_created = False
        try:
            return session.query(FtaSolutionsAppIncident).filter_by(dimension=self.incident_dict['dimension']).one()
        except Exception:
            pass
        try:
            self._insert_incident()
        except BaseException:
            time.sleep(random.randint(1, 100) / 100.0)
            self._insert_incident()
        logger.info(
            "$%s get_or_create_incident %s is_created=%s",
            CONTEXT.get('id'),
            self.incident_dict['dimension'],
            self.is_created)
        incident = session.query(FtaSolutionsAppIncident).filter_by(dimension=self.incident_dict['dimension']).one()
        return incident

    def connect_alarm(self):
        if self.match_alarm_id_list:
            return IncidentAlarmManager.connect(self.incident.id, self.match_alarm_id_list, )
        description = self.incident_dict.get('description')
        if not description or description == self.incident.description:
            return
        session.query(
            FtaSolutionsAppIncident,
        ).filter(
            FtaSolutionsAppIncident.id == self.incident.id,
        ).update(
            {FtaSolutionsAppIncident.description: description},
        )

    def count_alarm(self):
        return IncidentAlarmManager.count(incident_id=self.incident.id)

    @classmethod
    def converge(cls, incident_id=None):
        hide_incidents, show_incidents = cls.get_related_incidents(incident_id or incident_id)
        cls.triggle_incident(hide_incidents, is_visible=False)
        cls.triggle_incident(show_incidents, is_visible=True)

    @classmethod
    def get_related_incidents(cls, incident_id):
        incident_id = incident_id
        same_incidents = [incident_id]
        hide_incidents = []
        show_incidents = []
        related_alarm_id = [
            a[0] for a in session.query(
                FtaSolutionsAppIncidentalarm.alarm_id).filter_by(
                incident_id=incident_id).distinct()]
        logger.info("$%s related_alarm_id: %s", CONTEXT.get("id"), related_alarm_id)
        related_incident = session.query(
            FtaSolutionsAppIncidentalarm).filter(
            FtaSolutionsAppIncidentalarm.alarm_id.in_(related_alarm_id),
        )
        incidents = {}
        for incident in related_incident:
            incidents.setdefault(incident.incident_id, set()).add(incident.alarm_id)
        logger.info(
            "$%s found incidents from %s: %s",
            CONTEXT.get('id'), incident_id, incidents.keys())
        if incident_id in incidents:
            std_alarms = incidents.pop(incident_id)
        else:
            std_alarms = set(related_alarm_id)
        for other_inc, target_alarms in incidents.items():
            # 真子集的情况下, 不判断状态和先后, 直接隐藏子集
            if std_alarms > target_alarms:
                hide_incidents.append(other_inc)
                show_incidents.append(incident_id)
            elif std_alarms == target_alarms:
                # 全等的情况下, 放在一起全部比较，优先隐藏后面建立的
                same_incidents.append(other_inc)
        same_incidents = sorted(set(same_incidents))
        # 没有显示的收敛，则取全等的收敛最先建立的显示
        if same_incidents and not show_incidents:
            show_incidents.append(same_incidents[0])
            hide_incidents.extend(same_incidents[1:])
        # 否则隐藏相等的收敛
        else:
            hide_incidents.extend(same_incidents)
        logger.info("$%s incident hide %s | show %s", CONTEXT.get('id'), hide_incidents, show_incidents)
        return hide_incidents, show_incidents

    @classmethod
    def triggle_incident(cls, incidents, is_visible):
        incidents = sorted(list(set(map(int, incidents))))
        if not incidents:
            return
        session.query(FtaSolutionsAppIncident).filter(FtaSolutionsAppIncident.id.in_(incidents)).update(
            {FtaSolutionsAppIncident.is_visible: is_visible},
            synchronize_session=False
        )


class IncidentAlarmManager(object):

    @staticmethod
    def count(incident_id=None, alarm_instance_id=None):
        if incident_id:
            return session.query(FtaSolutionsAppIncidentalarm).filter_by(incident_id=incident_id).count()
        elif alarm_instance_id:
            return session.query(FtaSolutionsAppIncidentalarm).filter_by(alarm_id=alarm_instance_id).count()
        else:
            return 0

    @staticmethod
    def index(incident_id, alarm_instance_id):
        incident_alarm = session.query(FtaSolutionsAppIncidentalarm).filter_by(incident_id=incident_id).all()
        alarm_ids = [i.alarm_id for i in incident_alarm]
        return alarm_ids.index(alarm_instance_id)

    @staticmethod
    def connect(incident_id, alarm_instance_id_list):
        try:
            IncidentAlarmManager._connect(incident_id, alarm_instance_id_list)
        except BaseException:
            time.sleep(random.randint(1, 100) / 100.0)
            IncidentAlarmManager._connect(incident_id, alarm_instance_id_list)

    @staticmethod
    def _connect(incident_id, alarm_instance_id_list):
        """注意，不能使用try, except的方式，因为必定有很多重复记录，需要使用mysql IGNORE特性
        """
        session.execute(
            FtaSolutionsAppIncidentalarm.__table__.insert().prefix_with("IGNORE"), [{
                "incident_id": incident_id,
                "alarm_id": alarm_id,
                "is_primary": False
            } for alarm_id in alarm_instance_id_list]
        )
        logger.info("$%s connect %s: %s", CONTEXT.get('id'), incident_id, alarm_instance_id_list)
