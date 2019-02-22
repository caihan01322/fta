# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta import constants
from fta.utils import simulate


class AlarmDefManager(object):
    """Get standard alarm_def from DB or NET or Others"""

    def __init__(self):
        self.raw_alarm_def_dict = self.get_alarm_def()
        self.alarm_def_list = self.clean_alarm_def()

    def get_alarm_def(self):
        """
        :return dict: {alarm_def_id: alarm_def_dict}
            alarm_def_dict, key is alarm_def's id
        """
        return simulate.get_alarm_def()

    def clean_alarm_def(self):
        """
        :return list: [alarm_def_dict]
            standard alarm_def_list which has been cleaned
        """
        return [
            {
                dimension: raw_alarm_def_dict["dimension"].get(
                    dimension, raw_alarm_def_dict.get(dimension))
                for dimension in constants.ALARM_MATCH_KEY.keys() + ["id"]
            }
            for raw_alarm_def_dict in self.raw_alarm_def_dict.values()
        ]
