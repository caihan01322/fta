# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.utils import simulate


class IncidentDefManager(object):
    """Get standard incident_def from DB or NET or Others"""

    STD_DIMENSION = [
        "id", "cc_biz_id", "exclude_cc_biz_id",
        "description", "alarm_type", "timedelta",
        "count", "condition", "incident_func"]

    def __init__(self):
        self.raw_incident_def_dict = self.get_incident_def()
        self.incident_def_list = self.clean_incident_def()

    def get_incident_def(self):
        """
        :return dict: {incident_def_id: incident_def_dict}
            all_incident_def_dict, key is incident_def's id
        """
        return simulate.get_incident_def()

    def clean_incident_def(self):
        """
        :return list: [incident_def_dict]
            standard incident_def_list which has been cleaned
        """
        return [
            {
                dimension: raw_incident_def_dict[dimension]
                for dimension in self.STD_DIMENSION
            }
            for raw_incident_def_dict in self.raw_incident_def_dict.values()
        ]
