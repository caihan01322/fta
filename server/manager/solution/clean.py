# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
清理磁盘
taskId：1107  磁盘清理
注：每个参数两边加双引号，防止在shell下扩展
"""
import json

from fta.constants import CLEAN_TASK_PARAM
from fta.utils import logging
from fta.utils.i18n import _
from manager.solution.bk_component import VAR
from manager.solution.ijobs import Solution as MixinIjobsSolution

logger = logging.getLogger("solution")


class Solution(MixinIjobsSolution):

    """
    继承 ijobs 套餐
    {"clean_catalog":"/tmp/data/",
    "clean_date":"self",
    "clean_date_custom":"6",
    "clean_file":"self",
    "clean_file_custom":".txt"
    }

    {"app_id":"15091",
    "ijobs_taskt_id":null,
    "task_id":"1109",
    "ijobs_taski_name":"磁盘清理 (1109)",
    "parms":"",
    "parms0":"\"\"/data/log/\" \"30\" \"*.log\"",
    "retry_time":"10","retry_count":"0","steps":"1"}
    """

    def init_ijobs_conf(self):
        if getattr(self, 'job_task_id', None) is None:
            conf = self.conf
            logger.debug("clean_log %r init_ijobs_conf: %s",
                         self.alarm_instance['id'], conf)

            # 从告警信息中获取相关参数
            origin_alarm = json.loads(self.alarm_instance["origin_alarm"])
            plat_id = origin_alarm["_match_info"].get('cc_plat_id')
            self.ip_address = VAR(self.alarm_instance).get_value("ip")
            self.retry_time = int(conf.get("retry_time", "1"))
            self.retry_count = int(conf.get("retry_count", "0"))

            # 获取套餐配置项中参数，并将其组装为作业平台执行的参数
            clean_catalog = conf['clean_catalog']
            clean_date = conf['clean_date']
            clean_date_custom = conf['clean_date_custom']
            clean_date = clean_date_custom if clean_date == 'self' else clean_date
            clean_file = conf['clean_file']
            clean_file_custom = self.conf['clean_file_custom']
            clean_file = clean_file_custom if clean_file == 'clean_file_custom' else clean_file
            parms0 = "\"%s\" \"%s\" \"%s\"" % (
                clean_catalog, clean_date, clean_file)

            job_conf = CLEAN_TASK_PARAM
            job_conf['parms0'] = parms0
            self.conf = job_conf
            self.job_task_id = job_conf.get("task_id")
            logger.info('clean_log, job_conf:%s', job_conf)

            self.parms = job_conf.get("parms") or None
            self.operator = job_conf.get("operator") or None
            self.is_platform_task = True
            steps = int(job_conf.get("steps") or 0)
            self.step_parms = []
            step_ids = self.get_step_ids()
            for i in range(steps):
                try:
                    step_parm = {}
                    step_parm['scriptParam'] = job_conf.get("parms%s" % i)
                except BaseException:
                    step_parm = {}
                finally:
                    step_parm['stepId'] = step_ids[i]
                    step_parm['ipList'] = "%s:%s" % (plat_id, self.ip_address)
                    self.step_parms.append(step_parm)
            logger.info('clean_log, step_parms:%s', self.step_parms)

            self.serialized_step_parms = json.dumps(self.step_parms)
        else:
            self.step_parms = json.loads(self.serialized_step_parms)
            logger.debug("step_parms: %r", self.step_parms)

    def get_ijobs_comment(self, app_id, task_id, result_desc):
        """拼接结果描述"""
        return _("Disk cleanup %(result_desc)s", result_desc=result_desc)
