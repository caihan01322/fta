# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import random

import arrow

from fta import constants, settings
from fta.advice import CONTEXT
from fta.match_alarm.priority import PriorityCalculator
from fta.storage.mysql import orm_2_dict, session
from fta.storage.queue import MessageQueue
from fta.storage.tables import (AdviceFtaDef, FtaSolutionsAppAdvice,
                                FtaSolutionsAppAdvicedef,
                                FtaSolutionsAppAlarminstance,
                                FtaSolutionsAppSolution)
from fta.utils import logging
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.i18n import _, i18n
from project.utils.query_cc import get_cc_info_by_ip

logger = logging.getLogger("advice")

SOLUTION_QUEUE = MessageQueue("beanstalkd", settings.QUEUE_SOLUTION)


class AdviceFtaManager(object):
    """
    预警自愈处理逻辑
    """

    def __init__(self, advice):
        self.advice = advice
        self.raw_alarminstance_id = advice.get('alarminstance_id')
        self.advice_def_id = advice.get('advice_def_id')
        self.cc_biz_id = advice.get('cc_biz_id')
        self.ip = advice.get('subject')
        self.advice_id = advice.get('advice_id')
        self.snap_def = None

    def get_ip_cc_info(self):
        """
        查询ip相关的配置平台的信息，如集群、模块
        从cc中查询实时数据，而不从关联的告警信息中获取快照信息
        """
        cc_info_data = get_cc_info_by_ip(self.cc_biz_id, self.ip)
        cc_info_dict = {
            'set_names': cc_info_data.get('cc_topo_set_name'),
            'module_names': cc_info_data.get('cc_app_module_name')
        }
        return cc_info_dict

    def intersection(self, alarm_value, alarm_def_value):
        if isinstance(alarm_value, (list, set)) and isinstance(alarm_def_value, (list, set)):
            return set(alarm_value) & set(alarm_def_value)
        else:
            return False

    def get_advice_fta_def(self):
        """
        获取相关的预警策略的定义
        """
        advice_fta_def_list = session.query(AdviceFtaDef).filter(
            AdviceFtaDef.is_enabled is True,
            AdviceFtaDef.is_deleted is False,
            AdviceFtaDef.cc_biz_id.in_(['0', self.cc_biz_id])
        ).filter_by(
            advice_def_id=self.advice_def_id
        ).order_by(AdviceFtaDef.cc_biz_id)
        advice_fta_def_list = orm_2_dict(advice_fta_def_list)
        _def_list = []
        for _def in advice_fta_def_list:
            # 非套餐类的不需要处理
            if _def['handle_type'] != 'solution':
                continue

            _cc_biz_id = str(_def['cc_biz_id'])
            # 全业务需要判断，当前业务是否在 exclude 排除的业务中
            if _cc_biz_id == '0':
                if str(self.cc_biz_id) not in _def['exclude'].split(','):
                    _def_list.append(_def)
            else:
                _def_list.append(_def)
        return _def_list

    def match_advice_by_def(self):
        """
        建议是否需要进行自愈处理
        @return example: True/False, solution_id/none
        """
        # 查询业务下的所有预警定义
        advice_fta_def_list = self.get_advice_fta_def()
        # 根据 配置平台的集群、模块属性匹配
        cc_info_dict = self.get_ip_cc_info()

        matched_advice_fta_def_id = None
        matched_advice_def_id = None
        matched_solution_id = None
        for advice_fta_def in advice_fta_def_list:
            for key in ['cc_topo_set_name', 'cc_app_module_name']:
                advice_fta_def_value = advice_fta_def.get(key)
                advice_value = cc_info_dict.get(key)

                is_matched = ((not advice_fta_def_value) or
                              (advice_value and self.intersection(advice_value, advice_fta_def_value)))
                if not is_matched:
                    logger.debug(
                        "advice unmatched_key/advice_fta_def/advice: %s %s %s", key, advice_fta_def_value, advice_value
                    )
                    break
            # else means is matched
            else:
                logger.debug(
                    "advice matched_key/advice_fta_def/advice: %s %s %s", key, advice_fta_def_value, advice_value
                )
                matched_advice_def_id = advice_fta_def.get('advice_def_id')
                matched_solution_id = advice_fta_def.get('solution_id')
                matched_advice_fta_def_id = advice_fta_def.get('id')
                # 保存预警定义的快照信息
                # 预警定义中 cc_biz_id 为 0 全业务时，将其更新为当前的业务id
                if advice_fta_def.get('cc_biz_id') == 0:
                    advice_fta_def['cc_biz_id'] = self.cc_biz_id
                self.snap_def = advice_fta_def
                break
        return matched_advice_fta_def_id, matched_advice_def_id, matched_solution_id

    def make_alarm_by_advice(self):
        """
        根据建议信息生成一条告警信息，方便出发后续的处理流程
        """
        advice_fta_def_id, advice_def_id, solution_id = self.match_advice_by_def()
        advice_def = session.query(FtaSolutionsAppAdvicedef).filter_by(id=advice_def_id).first()
        solution = session.query(FtaSolutionsAppSolution).filter_by(id=solution_id).first()
        if not advice_def or not solution:
            return False

        raw_alarm_info = get_alarm_instance(instance_id=int(self.raw_alarminstance_id))
        i18n.set_biz(raw_alarm_info.get('cc_biz_id'))
        # 从原始告警信息中生成一条触发预警自愈的告警流程
        cur_time_stamp = arrow.utcnow().timestamp
        cur_time_stamp = '%s_%s' % (cur_time_stamp, random.randrange(1000))
        solution_type = solution.solution_type
        if solution_type in ['collect', 'sleep']:
            status = 'for_reference'
            comment = _("Save directly without processing")
        else:
            status = 'converged'
            comment = ''
        event_id = "FTA%s" % cur_time_stamp
        snap_solution = json.dumps(orm_2_dict(solution))
        snap_alarm_def = json.dumps(self.snap_def)
        alram_info = {
            "source_id": cur_time_stamp,
            "source_time": arrow.utcnow().format(constants.STD_ARROW_FORMAT),
            "begin_time": arrow.utcnow().format(constants.STD_ARROW_FORMAT),
            "event_id": event_id,
            "status": status,
            "comment": comment,
            "snap_alarm_def": snap_alarm_def,
            "alarm_def_id": 0,

            "cc_biz_id": raw_alarm_info.get('cc_biz_id'),
            "cc_topo_set": raw_alarm_info.get('cc_topo_set'),
            "cc_app_module": raw_alarm_info.get('cc_app_module'),
            "origin_alarm": raw_alarm_info.get('origin_alarm'),
            "alarm_type": "fta_advice",  # 预警自愈
            "source_type": "FTA",  # 故障自愈

            "ip": self.ip,
            "raw": advice_def.description,  # 告警的原始信息未告警建议的描述
            "snap_solution": snap_solution,
            "solution_type": solution_type,
        }
        try:
            alarm_result = session.execute(FtaSolutionsAppAlarminstance.__table__.insert(), alram_info)
            new_alarminstance_id = alarm_result.inserted_primary_key[0]
            # 将预警自愈的信息关联到建议中
            session.query(FtaSolutionsAppAdvice).filter_by(id=self.advice_id).update({
                'advice_fta_def_id': advice_fta_def_id,
                'alarminstance_id': new_alarminstance_id
            })
        except Exception as e:
            logger.exception("save advice exception: %s" % e)
            return False

        # 将预警产生的告警新推动的处理队列中
        self.push_to_queue(new_alarminstance_id, event_id)
        return True

    def push_to_queue(self, alarm_instance_id, event_id):
        """push alarm to solution queue"""
        CONTEXT.set("id", alarm_instance_id)
        # 计算优先级
        alarm_instance = session.query(FtaSolutionsAppAlarminstance).filter_by(id=alarm_instance_id).first()
        alarm_instance = orm_2_dict(alarm_instance)
        logger.info('alarm_instance:%s' % alarm_instance)
        priority = PriorityCalculator(alarm_instance).priority
        # 推送到 SOLUTION_QUEUE 中
        SOLUTION_QUEUE.put(event_id, priority)
        logger.info("$%s put alarm into beanstalkd: %s", CONTEXT.get('id'), event_id)
        return True


if __name__ == '__main__':
    ad_id = 35
    ad = session.query(FtaSolutionsAppAdvice).filter_by(id=ad_id).first()
    ad = orm_2_dict(ad)
    ad['alarminstance_id'] = 159683

    advice_fta = AdviceFtaManager(ad)
    advice_fta.make_alarm_by_advice()
