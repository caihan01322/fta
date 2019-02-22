# -*-coding:utf-8-*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta import constants
from fta.advice import send_advice
from fta.advice.advice_func import common_ip_handler
from fta.advice.advicedef import AdviceDefManager
from fta.utils import logging
from fta.utils.i18n import _
from fta.utils.monitors import get_alarm_type

logger = logging.getLogger("advice")

# 新的处理函数请加入到这个映射表中
HANDLER_MAPPER = {
    'DiskUtilization': common_ip_handler,
    'Faild_ping': common_ip_handler,
    'Agent_report_timeout': common_ip_handler,
    'Machine_restart': common_ip_handler,
    'Read_onlyDisk': common_ip_handler,
}


class Advice(object):

    def __init__(self):
        advice_def_manager = AdviceDefManager()
        self.advice_def_list = advice_def_manager.advicedef_list
        self.advice_def_dict = advice_def_manager.raw_advicedef_dict
        logger.info("advice_def list: %s", len(self.advice_def_list))
        self.advices = []

    def make_advice(self, check_time=None):
        check_time = check_time or arrow.utcnow().format(constants.STD_ARROW_FORMAT)
        for advicedef in self.advice_def_list:
            logger.info("run advice_def %s", advicedef["id"])
            check_sub_type = advicedef['check_sub_type']
            handler = HANDLER_MAPPER.get(check_sub_type, common_ip_handler)
            self.advices += handler(advicedef, check_time, check_sub_type.split(','))

    @staticmethod
    def _print_alarm_type(alarm_type, cc_biz_id):
        for i in get_alarm_type(cc_biz_id):
            at = i["alarm_type"]
            at_str = i["description"]
            if at in alarm_type:
                alarm_type = alarm_type.replace(at, at_str)
        alarm_type = alarm_type.replace(',', '/')
        return alarm_type

    @staticmethod
    def _print_interval(interval):
        if interval == 30:
            return _("One month")
        elif interval == 7:
            return _("One week")
        elif interval == 1:
            return _("Within one day")
        else:
            return _("Within %(interval)s day(s)", interval=interval)

    def get_advice_biz_dict(self):
        advices_by_biz = {}
        all_desc = set()
        for ad in self.advices:
            advicedef = self.advice_def_dict[str(ad['advice_def_id'])]

            ad['subject_type'] = advicedef['subject_type']
            ad['interval'] = self._print_interval(advicedef['interval'])
            ad['check_sub_type'] = self._print_alarm_type(advicedef['check_sub_type'], ad["cc_biz_id"], )

            ad['desc'] = u"{}{} {}{}次 {}".format(
                ad['subject_type'], ad['subject'], ad['interval'],
                ad['alarm_num'], ad['check_sub_type'])

            if ad['desc'] in all_desc:  # 避免重复
                continue

            # 建议多行的转换：虽然也可以用linebreaksbr，但没法缩进
            ad['advice'] = advicedef['advice'].replace('\n', '<br>' + '&nbsp;' * 11)
            advices_by_biz.setdefault(ad['cc_biz_id'], []).append(ad)
            all_desc.add(ad['desc'])
        return advices_by_biz

    def push_advice(self):
        if not self.advices:
            return logger.info("Advices doesn't exist.")
        biz_advices_dict = self.get_advice_biz_dict()
        send_advice.mail(biz_advices_dict, self.advice_def_dict)

    def start(self):
        self.make_advice()
        self.push_advice()


# @redis_lock("advice_process", 12*60*60)
def main():
    try:
        advice = Advice()
        advice.start()
    except Exception as e:
        logger.exception(_("Failed to run health report: %s"), e)


if __name__ == "__main__":
    main()
