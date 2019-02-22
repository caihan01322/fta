# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""告警定义模块
"""
from fta import constants
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppAlarmdef
from fta.utils import logging, remove_blank
from fta.utils.decorator import exception_cache

logger = logging.getLogger('match_alarm')


class AlarmDefManager(object):

    """生成一个self.alarm_def_list的字典列表，用于与alarm_list匹配"""

    def __init__(self):
        self.raw_alarm_def_dict = self.get_alarm_def()
        self.alarm_def_list = self.clean_alarm_def(
            self.raw_alarm_def_dict.values())

    @exception_cache(timeout=15 * 60, ignore_argv=True)
    def get_alarm_def(self):
        """get alarm def dict from db"""
        alarm_def_list = session.query(FtaSolutionsAppAlarmdef)\
            .filter_by(is_enabled=True)
        logger.info('alarm_def:%s', alarm_def_list.count())
        alarm_def_list = orm_2_dict(alarm_def_list)

        return {str(alarm_def['id']): alarm_def
                for alarm_def in alarm_def_list}

    def clean_alarm_def(self, raw_alarm_def_list):
        """clean alarm def from db raw dict to std alarm_def_dict"""
        alarm_def_list = []
        for fta_alarm_def in raw_alarm_def_list:
            # alarm_def_id = fta_alarm_def['id']
            exclude = fta_alarm_def.get('tnm_attr_id', '')
            exclude_biz_ids = exclude.split(',') \
                if (fta_alarm_def['cc_biz_id'] == 0 and exclude) else []
            alarm_def_list.append({
                'id': fta_alarm_def['id'],
                'source_type': fta_alarm_def['source_type'],
                'category': '',
                'alarm_type': [fta_alarm_def['alarm_type']],
                'alarm_desc': fta_alarm_def.get('reg', ''),
                'alarm_attr_id': [fta_alarm_def['alarm_attr_id']],
                'alarm_process': fta_alarm_def['process'],
                'alarm_responsible': [],
                'cc_biz_id': fta_alarm_def['cc_biz_id'],
                'cc_topo_set': fta_alarm_def.get('set_names', '').split(','),
                'cc_app_module': fta_alarm_def.get('module_names', '').split(','),
                'host': tuple(),
                'cc_plat_id': '',
                'cc_set_category': '',
                'cc_set_envi_type': '',
                'cc_set_service_state': '',
                'exclude_biz_ids': exclude_biz_ids,
            })

        # remove blank data in alarm_def_dict value
        for alarm_def in alarm_def_list:
            for match_key, _ in constants.ALARM_MATCH_KEY.items():
                alarm_def[match_key] = remove_blank(alarm_def[match_key])

        return alarm_def_list
