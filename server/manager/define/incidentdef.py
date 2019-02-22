# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""收敛规则定义模块
"""
import json
import random
import time

from sqlalchemy.orm.exc import NoResultFound

from fta import constants
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppIncidentdef
from fta.utils import logging
from fta.utils.decorator import exception_cache
from fta.utils.i18n import _
from fta.utils.monitors import get_alarm_type, get_description_by_alarm_type

logger = logging.getLogger('converge')


class IncidentDefManager(object):
    """生成一个self.alarm_def_list的字典列表,用于与alarm_list匹配"""

    def __init__(self):
        self.raw_incident_def_dict = self.get_incident_def()
        self.incident_def_list = self.clean_incident_def(
            self.raw_incident_def_dict.values())

    def get_incident_def(self):
        fta_incident_def_list = session.query(
            FtaSolutionsAppIncidentdef
        ).filter_by(is_enabled=True)
        # logger.info('alarm_incident_def:%s', fta_incident_def_list.count())
        incident_def_list = orm_2_dict(fta_incident_def_list)
        return {
            str(incident_def['id']): incident_def
            for incident_def in incident_def_list}

    @exception_cache(timeout=15 * 60, ignore_argv=True)
    def clean_incident_def(self, raw_incident_def_list):
        incident_def_list = []
        raw_incident_def_list.sort(key=lambda x: (x['priority'], x['id']))
        for fta_incident_def in raw_incident_def_list:
            rule = self._clean_incident_def_rule(fta_incident_def['rule'])
            incident_def_list.append({
                'id': fta_incident_def['id'],
                'cc_biz_id': fta_incident_def['cc_biz_id'],
                'exclude_cc_biz_id':
                    (fta_incident_def.get('exclude') or "").split(','),
                'description':
                    IncidentDescription(rule, fta_incident_def).description or
                    fta_incident_def['description'],
                'alarm_type': rule.get('alarm_type'),
                'timedelta': rule.get('timedelta'),
                'count': rule.get('count'),
                'condition': rule.get('condition'),
                'incident_func': rule.get('incident'),
            })
        return incident_def_list

    def _clean_incident_def_rule(self, raw_rule):
        """ fit incident_def condition keys name to new name """
        try:
            rule = json.loads(raw_rule)
        except BaseException:
            return {}

        # collect_alarm have not condition
        if not rule.get('condition'):
            return rule

        # 部分转换字段有些版本是没有的，需要在_get_description_for_condition处理
        translate_dict = {
            "cc_set": "cc_topo_set",
            "cc_biz": "cc_biz_id",
            "idc_unit": "cc_idc_unit",
            "equipment": "cc_equipment",
            "link_net_device": "cc_link_net_device",
            "process": "alarm_process",
            "port": "alarm_port",
        }
        for dimension in rule['condition'].keys():
            if translate_dict.get(dimension):
                rule['condition'][translate_dict[dimension]] = rule['condition'][dimension]
                del rule['condition'][dimension]
        return rule


class IncidentDescription(object):

    def __init__(self, incident_def_rule, fta_incident_def=None):
        self.incident_def_rule = incident_def_rule
        self.fta_incident_def = fta_incident_def

    @property
    def cc_biz_id(self):
        return self.fta_incident_def and self.fta_incident_def.get("cc_biz_id")

    @property
    def description(self):
        if not self.incident_def_rule:
            return ""
        return _("For (%(alarm_type)s) alarm type, if (%(timedelta)s) (%(count)s) alarms appear within (%(condition)s) minute(s), (%(incident)s).",  # noqa
                 alarm_type=u"/".join([
                     get_description_by_alarm_type(
                         alarm_type, cc_biz_id=self.cc_biz_id, default=alarm_type,
                     )
                     for alarm_type in self._get_alarm_type_group_chn(
                         self.incident_def_rule['alarm_type'],
                     )
                 ]),
                 timedelta=self.incident_def_rule['timedelta'],
                 count=self.incident_def_rule['count'],
                 condition=_(" and ").join([
                     self._get_description_for_condition(k, v)
                     for k, v in self.incident_def_rule['condition'].items()]),
                 incident=constants.INCIDENT_FUNC.get(
                     self.incident_def_rule['incident'],
                     self.incident_def_rule['incident']),
                 )

    def _get_alarm_type_group_chn(self, alarm_type_list):
        total = len(set(
            i['alarm_type']
            for i in get_alarm_type(cc_biz_id=self.cc_biz_id)
        ))
        if len(set(alarm_type_list)) == total:
            return [_("all")]
        return alarm_type_list

    def _get_dimension_value_chn(self, dimension, value):
        if value == 'self':
            return _("Same")
        if dimension == 'alarm_type':
            return get_description_by_alarm_type(
                value, cc_biz_id=self.cc_biz_id, default=value,
            )

    def _get_description_for_condition(self, dimension, values):
        if dimension == 'alarm_type':
            values = self._get_alarm_type_group_chn(values)
        return "%s%s" % (
            u"/".join([
                self._get_dimension_value_chn(dimension, v)
                for v in values]),
            constants.ALARM_DIMENSION_KEY.get(dimension, dimension)
        )


def get_or_create_incidentdef(codename='collect_alarm', rule=None, description=''):
    """fake incident
    汇总通知。并非真正的收敛规则，只是为了汇总通知套餐规则告警显示创建 incident 时依赖的 incident_def
    collect_alarm 为汇总专用
    """
    if not rule:
        rule = {}

    context = {
        'cc_biz_id': 0,
        'codename': codename,
        'description': description,
        'priority': '100',
        'rule': json.dumps(rule),
        'exclude': '',
        'is_enabled': True
    }

    def _insert_incident():
        try:
            session.execute(
                FtaSolutionsAppIncidentdef.__table__.insert(), [context])
            logger.info('_insert_incident %s success' % codename)
        except Exception as error:
            logger.error('_insert_incident %s error: %s' % (codename, error))

    try:
        return session.query(FtaSolutionsAppIncidentdef).filter_by(codename=codename).one()
    except NoResultFound:
        logger.warning('get %s incidentdef failed, try to create' % codename)

    try:
        _insert_incident()
    except BaseException:
        time.sleep(random.randint(1, 100) / 100.0)
        _insert_incident()

    return session.query(FtaSolutionsAppIncidentdef).filter_by(codename=codename).one()
