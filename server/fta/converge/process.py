# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta import constants, settings
from fta.converge import CONTEXT
from fta.converge.incident_def import IncidentDefHandler
from fta.storage.mysql import session
from fta.storage.queue import MessageQueue
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import error_handler, extended_json, lock, logging, send_notice, timeout
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.i18n import _, i18n
from manager.define.incidentdef import IncidentDefManager

logger = logging.getLogger('converge')

CONVERGE_QUEUE = MessageQueue("beanstalkd", settings.QUEUE_CONVERGE)
SOLUTION_QUEUE = MessageQueue("beanstalkd", settings.QUEUE_SOLUTION)


class Converge(object):

    def __init__(self, incident_def_list=None):
        """
        :param incident_def_list: [incident_def_dict, ] see IncidentDefHandler
        """
        self.incident_def_list = incident_def_list or IncidentDefManager().incident_def_list
        self.job = None
        self.comment = ''
        self.status = 'converged'
        self.receive_status = 'received'
        self.alarm_instance = {}

    def pull_alarm(self, event_id=None, alarm_instance=None):
        """
        pull alarm
        :param event_id: get alarm by event_id，for test
        :param alarm_instance: get alarm by dict, for test
        """
        if not event_id and not alarm_instance:
            self.job = CONVERGE_QUEUE.take(timeout=settings.QUEUE_WAIT_TIMEOUT)
            if not self.job:
                raise lock.PassEmpty
            event_id = self.job.body
            logger.info("converge process event_id: %s", event_id)

        # for test
        elif event_id:
            event_id = event_id

        # for test
        if alarm_instance:
            self.alarm_instance = alarm_instance

        else:
            self.receive_status = lock.lock_alarm_instance(event_id, ['received', 'sleep'], 'converging')
            self.alarm_instance = get_alarm_instance(event_id=event_id)

        i18n.set_biz(self.alarm_instance['cc_biz_id'])

        CONTEXT.set("id", self.alarm_instance['id'])

        logger.info("$%s converge event_id: %s", CONTEXT.get('id'), event_id)
        timeout.set_timeout(timeout.get_timeout_time(self.alarm_instance))

    def is_sleep_timeout(self):
        """check wether timeout for 'sleep' status"""
        alarm_def = extended_json.loads(self.alarm_instance['snap_alarm_def'])
        timeout_remain = timeout.get_timeout_time(self.alarm_instance)
        if timeout_remain < int(alarm_def['timeout']) * 60 / 2:
            return True
        return False

    def converge_alarm(self):
        """run converge by incident_def"""

        # check wether timeout for 'sleep' status
        if self.receive_status == 'sleep' and self.is_sleep_timeout():
            self.status = 'skipped'
            self.comment = _("Converged: Skip after timeout in convergent waiting")
            return

        result_dict = {}
        # run every incident_def to get converge result
        for incident_def in self.incident_def_list:
            incident_biz_id = int(incident_def["cc_biz_id"])
            exclude_cc_biz_ids = map(int, (i for i in incident_def["exclude_cc_biz_id"] if i), )
            alarm_biz_id = int(self.alarm_instance["cc_biz_id"])
            if (incident_biz_id == 0 and alarm_biz_id in exclude_cc_biz_ids) \
                    or (incident_biz_id != 0 and incident_biz_id != alarm_biz_id):
                continue
            logger.info("$%s incident_def #%s: BEGIN", CONTEXT.get('id'), incident_def['id'])
            result, description = self.run_incident_def(incident_def)
            logger.info("$%s incident_def #%s: %s END", CONTEXT.get('id'), incident_def['id'], result)
            if result:
                result_dict[result] = description
        logger.info(
            "$%s incident result: %s",
            CONTEXT.get('id'), result_dict)

        # update status && comment by converge result
        if 'skip' in result_dict:
            self.status = 'skipped'
            self.comment = _("Converged: %(comment)s", comment=result_dict['skip'])
            return
        if 'waiting' in result_dict:
            self.status = 'waiting'
            self.comment = _("Convergence to be approved: %(comment)s", comment=result_dict['waiting'])
            return
        if 'sleep' in result_dict:
            self.status = 'sleep'
            return

    def run_incident_def(self, incident_def):
        """call IncidentDefHandler"""
        try:
            incident_def_handler = IncidentDefHandler(incident_def, self.alarm_instance)
            result = incident_def_handler.run()
            description = incident_def_handler.incident_def['description']
            return result, description
        except Exception as error:
            logger.exception("run incident[%s] failed: %s", incident_def, error, )
            return None, ""  # skip this incident

    def push_alarm(self):
        """update status in DB && push into queue"""
        end_time = arrow.utcnow().naive if self.status == 'skipped' else None
        session.query(FtaSolutionsAppAlarminstance).filter_by(event_id=self.alarm_instance['event_id']).update({
            "status": self.status,
            "comment": self.comment,
            "end_time": end_time,
        })
        if self.status == 'sleep' and self.job:
            # put back to converge queue for wait
            self.job.release(delay=60)
            self.job = None
        else:
            self.push_to_queue()

    def push_to_queue(self):
        """push alarm to solution queue"""
        SOLUTION_QUEUE.put(str(self.alarm_instance['event_id']), self.job._priority() if self.job else 1)
        logger.info("$%s put alarm into beanstalkd: %s", CONTEXT.get('id'), self.alarm_instance['event_id'])

    def start(self):
        try:
            self.pull_alarm()
            self.converge_alarm()
            self.push_alarm()
        except timeout.TimeoutError:
            error_handler.timeout(self.alarm_instance)
        except lock.LockError as e:
            logger.info('$%s %s', CONTEXT.get('id'), e)
        except lock.PassEmpty:
            pass
        except Exception as e:
            error_message = u'%s $%s frame_error %s' % (constants.ERROR_01_CONERGE, CONTEXT.get('id'), e)
            send_notice.exception(error_message)
            logger.exception(error_message)
            error_handler.exception(self.alarm_instance)
            raise
        finally:
            if self.job:
                self.job.delete()
            timeout.del_timeout()
            CONTEXT.delete("id")
