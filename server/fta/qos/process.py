# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import time
from collections import defaultdict
from functools import reduce

import arrow

from fta import constants, settings
from fta.storage.cache import Cache
from fta.storage.mysql import orm_2_dict, session
from fta.storage.queue import MessageQueue
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import error_handler, extended_json, lock, logging, send
from fta.utils.conf import get_fta_admin_list
from fta.utils.i18n import _, i18n
from fta.utils.monitors import get_description_by_alarm_type

logger = logging.getLogger('qos')
redis_cache = Cache('redis')

QUEUE_STATUS = ["received", "converged"]

COLLECT_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_COLLECT)

FTA_ADMIN_LIST = get_fta_admin_list()


class Qos(object):

    def check_blocked(self, status):
        """
        get block whether happened in sqecial topic by alarm_instance's status
        :param status: which status
        """
        running_instances = session.query(FtaSolutionsAppAlarminstance).filter_by(status=status)
        running_instance_ids = [a.id for a in running_instances]
        logger.info("running alarm[%s](%s): %s", status, running_instances.count(), running_instance_ids)

        redis_key = "QOS_RUNNING_%s" % status
        his_data = redis_cache.get(redis_key) or "[]"
        his_running_instance_ids = json.loads(his_data)
        his_running_instance_ids.insert(0, running_instance_ids)
        his_running_instance_ids = his_running_instance_ids[:settings.BLOCK_TIME_THRESHOLD + 1]
        redis_cache.set(redis_key, json.dumps(his_running_instance_ids))

        if len(his_running_instance_ids) < settings.BLOCK_TIME_THRESHOLD + 1:
            return logger.warning(
                "QOS his_running less than %s: %s", settings.BLOCK_TIME_THRESHOLD, len(his_running_instance_ids)
            )

        blocked_instance_ids = set(his_running_instance_ids[0]) & \
            set(his_running_instance_ids[settings.BLOCK_TIME_THRESHOLD])
        if len(blocked_instance_ids):
            self._mark_alarm_to_notice(status, len(running_instance_ids), blocked_instance_ids)

    def _mark_alarm_to_notice(self, status, tot_count, blocked_instance_ids):
        """
        mark alarm_instance status to 'for_notice' and pass solution
        :param status: which status
        :param blocked_instance_ids: which alarm_instance blocked
        """
        # get blocked_priority
        blocked_instance_list = session.query(
            FtaSolutionsAppAlarminstance
        ).filter(FtaSolutionsAppAlarminstance.id.in_(blocked_instance_ids))
        blocked_priority = reduce(min, [a.priority for a in blocked_instance_list])

        alarm_instance_list = session.query(
            FtaSolutionsAppAlarminstance
        ).filter_by(status=status).filter(FtaSolutionsAppAlarminstance.priority >= blocked_priority)

        # update status && count
        mark_count = 0
        count_dict = {}
        for alarm_instance in alarm_instance_list:
            i18n.set_biz(alarm_instance.cc_biz_id)

            if session.query(
                    FtaSolutionsAppAlarminstance
            ).filter_by(event_id=alarm_instance.event_id).filter_by(status=status).update({
                "status": "for_notice",
                "comment": _("Skip without processing: Flow control due to alarm flocking"),
                "end_time": arrow.utcnow().naive
            }):
                COLLECT_QUEUE.put(str(alarm_instance.event_id))
                count_dict.setdefault(alarm_instance.cc_biz_id, defaultdict(int))[alarm_instance.alarm_type] += 1
                mark_count += 1

        # create the notice message to ADMIN
        # use last alarm_instance language
        alarm_msg = [
            _("[Fault Auto-recovery] [Flow Control]"),
            _("Status: [%(status)s]", status=status),
            _("Total alarms: (%(total_count)s) article(s)", total_count=tot_count),
            _("Alarm discards: (%(mark_count)s) article(s)", mark_count=mark_count),
            _("Alarm discard priority: %(blocked_priority)s", blocked_priority=blocked_priority),
            _("----- Details -----")
        ]
        for cc_biz_id, type_dict in count_dict.items():
            for alarm_type, count in type_dict.items():
                alarm_msg.append(_(
                    "Business [%(cc_biz_id)s] [%(alarm_type)s] (%(count)s)",
                    cc_biz_id=cc_biz_id,
                    alarm_type=alarm_type,
                    count=count))
        logger.warning("Qos block instance_id: %s", ','.join([str(a.id) for a in alarm_instance_list]))
        send.wechat(FTA_ADMIN_LIST, constants.WECHAT_BREAKS.join(alarm_msg))

    def check_timeout(self):
        """check whether have alarm which's exec_time is timeout"""

        # get running_instance by not_end_status
        running_instances = session.query(
            FtaSolutionsAppAlarminstance
        ).filter(FtaSolutionsAppAlarminstance.status.in_(constants.INSTANCE_NOT_END_STATUS))
        running_instance_ids = [a.id for a in running_instances if a.status != "retrying"]  # qos ignore retry
        logger.info("running alarm(%s): %s", running_instances.count(), running_instance_ids)

        for alarm_instance in running_instances:

            # qos ignore retry
            if alarm_instance.status == "retrying":
                continue

            run_time = arrow.utcnow().naive - alarm_instance.source_time
            run_time_minutes = int(run_time.total_seconds()) / 60
            alarm_def = extended_json.loads(alarm_instance.snap_alarm_def)

            # left 5 minutes for check, normal then pass
            if run_time_minutes < (int(alarm_def['timeout']) + 5):
                continue

            # send timeout message to ADMIN
            notice_message = _(
                '[Fault Auto-recovery] [Processing Timeout] [%(cc_biz_id)s][%(alarm_type)s][%(instance_id)s][%('
                'status)s]',
                # noqa
                cc_biz_id=alarm_instance.cc_biz_id,
                alarm_type=get_description_by_alarm_type(
                    alarm_instance.alarm_type,
                    cc_biz_id=alarm_instance.cc_biz_id,
                    default=alarm_instance.alarm_type,
                ),
                instance_id=alarm_instance.id,
                status=alarm_instance.status)
            logger.error(notice_message)

            # force end alarm_instance which is timeouted
            error_handler.timeout(orm_2_dict(alarm_instance))

    def start(self):
        """The Entrance of QOS"""
        # lock time range should small then check's interval
        if lock.redis_lock("--qos_check_blocked--", settings.BLOCK_CHECK_INTERVAL - 5):
            # logger.info(u"get qos check lock success")
            for status in QUEUE_STATUS:
                self.check_blocked(status)
            self.check_timeout()
        time.sleep(settings.BLOCK_CHECK_INTERVAL)
