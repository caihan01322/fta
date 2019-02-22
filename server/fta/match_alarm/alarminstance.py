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

from fta.converge import converge_func
from fta.match_alarm.priority import PriorityCalculator
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import extended_json, get_first, get_list, logging
from fta.utils.alarm_instance import make_event_id
from fta.utils.decorator import try_exception
from fta.utils.i18n import gettext as _
from fta.utils.i18n import i18n
from manager.define.alarmdef import AlarmDefManager
from manager.define.shield import ShieldManager
from manager.define.solution import SolutionManager

logger = logging.getLogger('match_alarm')


class AlarmInstanceManager(object):

    def __init__(self, alarm_list, alarm_def_dict=None, solution_dict=None, shield_list=None):
        """
        :param alarm_list: raw_alarm_dict list include "_match_info"
        :param alarm_def_dict: all alarm_def's dict key is alarm_def_id
        :param solution_dict: all solution's dict key is solution_id
        """
        self.alarm_list = alarm_list
        self.alarm_def_dict = alarm_def_dict or self.get_alarm_def_dict()
        self.solution_dict = solution_dict or self.get_solution_dict()
        self.shield_list = shield_list or []
        self.alarm_instance_list = []
        for alarm in self.alarm_list:
            try:
                adapted_alarm = self.adapt_to_alarminstance(alarm)
            except Exception as e:
                logger.warning("$%s adapt error: %s", alarm["_match_info"]["source_id"], e)
            else:
                self.alarm_instance_list.append(adapted_alarm)

    def get_alarm_def_dict(self):
        alarm_def_manager = AlarmDefManager()
        return alarm_def_manager.raw_alarm_def_dict

    def get_solution_dict(self):
        solution_manager = SolutionManager()
        return solution_manager.raw_solution_dict

    @try_exception(exception_desc=u"check shield failured")
    def check_shield(self, match_info, dimensions):
        check_fields = {}
        check_fields.update(match_info)
        check_fields.update(dimensions)

        shield_manager = ShieldManager()
        # 屏蔽事件正式从事件库切换到数据库
        shield_list = self.shield_list or shield_manager.shield_list

        for shield in shield_list:
            # check by shield_dict's key which not startswith "_"

            for key, value in shield.items():
                if key.startswith("_"):
                    continue

                alarm_set = set(map(lambda x: unicode(x), get_list(check_fields.get(key, []))))
                shield_set = set(map(lambda x: unicode(x), get_list(value)))
                if not alarm_set & shield_set:
                    break
            else:
                logger.info(
                    "%s shield_by %s",
                    make_event_id(check_fields["source_type"], check_fields["source_id"]),
                    shield["_id"])
                return shield["_description"]

    @try_exception(exception_desc=u"check converge failured")
    def check_converge(self, match_info, converge_conf):
        return converge_func.run("pre_converge", match_info, converge_conf)

    def adapt_to_alarminstance(self, matched_alarm):
        """
        :param matched_alarm: raw_alarm_dict, one of the self.alarm_list
        :return: transform a matched_alarm to an normalized alarminstance
        """
        i18n.set_biz(matched_alarm['_match_info']['cc_biz_id'])

        match_info = matched_alarm['_match_info']
        alarm_def = self.alarm_def_dict[str(match_info['alarm_def_id'])]
        match_info['solution'] = alarm_def['solution_id']
        solution = self.solution_dict.get(str(alarm_def['solution_id']), {})

        # check whether been shieldp
        shield_desc = self.check_shield(match_info, matched_alarm.get("dimensions", {}))
        # check whether been converged
        converge_desc = self.check_converge(match_info, alarm_def.get('converge', '{}'))

        if shield_desc:
            end_time, status, comment = arrow.utcnow().naive, 'shield', shield_desc

        elif converge_desc:
            end_time, status, comment = arrow.utcnow().naive, 'skipped', converge_desc

        # save and collect if solution_type is collect, sleep, None
        elif not solution or solution.get('solution_type') in ('collect', 'sleep'):
            end_time, status, comment = arrow.utcnow().naive, 'for_reference', _('Save directly without processing')

        # else marked initial state
        else:
            end_time, status, comment = None, 'received', ''

        cc_topo_set = match_info.get('cc_topo_set', [])
        if not isinstance(cc_topo_set, (list, tuple)):
            cc_topo_set = [cc_topo_set]
        cc_app_module = match_info.get('cc_app_module', [])
        if not isinstance(cc_app_module, (list, tuple)):
            cc_app_module = [cc_app_module]

        alarminstance = dict(
            # alarm meta info
            source_time=match_info['alarm_time'],
            source_type=match_info['source_type'],
            source_id=match_info['source_id'],
            event_id=make_event_id(match_info['source_type'], match_info['source_id']),
            alarm_def_id=match_info['alarm_def_id'],

            # alarm base variables
            alarm_type=alarm_def['alarm_type'] or get_first(match_info["alarm_type"]),
            solution_type=solution.get('solution_type') if solution else None,
            snap_alarm_def=extended_json.dumps(alarm_def),
            snap_solution=extended_json.dumps(solution) if solution else None,
            origin_alarm=extended_json.dumps(matched_alarm),
            cc_biz_id=match_info['cc_biz_id'],
            raw=match_info['alarm_desc'],
            # 此处应该修改为从 match_info 获取或者从 alarm_def 获取
            level=matched_alarm.get('monitor_level') or 3,

            # alarm extended variables
            ip=match_info.get('host'),
            cc_topo_set=','.join(cc_topo_set),
            cc_app_module=','.join(cc_app_module),

            # fta status
            begin_time=arrow.utcnow().naive,
            end_time=end_time,
            status=status,
            comment=comment,

            # get in run_solution
            failure_type=None,
            approved_user=None,
            approved_time=None,
            approved_comment=None,

            # 告警信息中的上下文
            tnm_alarm=match_info.get('alarm_context', ''),

            inc_alarm_id=None,
            uwork_id=None,

            bpm_task_id=None,
            tnm_alarm_id=None
        )

        # assign a priority for "Converge" queue
        alarminstance['priority'] = PriorityCalculator(alarminstance).priority
        return alarminstance

    def _save(self):
        for i in self.alarm_instance_list:
            try:
                session.execute(FtaSolutionsAppAlarminstance.__table__.insert(), i, )
            except Exception:
                logger.warning("insert alarm instance error: %s", i.get("event_id"), )

    def save(self):
        """insert alarm_instance into mysql"""
        if not self.alarm_instance_list:
            return
        try:
            self._save()
        except BaseException:
            time.sleep(random.randint(1, 100) / 100.0)
            self._save()
