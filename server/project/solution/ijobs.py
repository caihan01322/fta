# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import re

from fta import settings
from fta.constants import (ALL_BIZ_STEP_ID, CLEAN_TASK_ID,
                           IS_TASKS_RESULT_SPECIAL, TOP_CPU_TASK_ID,
                           TOP_MEM_TASK_ID)
from fta.settings import JOB_ADDR
from fta.solution.base import BaseSolution
from fta.utils import logging
from fta.utils.context import Context
from fta.utils.decorator import try_exception
from fta.utils.i18n import _
from manager.solution.bk_component import VAR
from project.utils.component import bk
from project.utils.query_cc import get_app_by_id

logger = logging.getLogger("solution")


class Solution(BaseSolution):
    """
    jobs 套餐 (没有执行态的概念)

    :param conf["job_task_id"]: ijobs 作业ID
    :param conf["parms"]: ijobs 步骤参数
    :param conf["argv"]: 是否从 ijobs 获取参数
    :param conf["steps"]: 步骤数目
    :param conf["retry_count"]: 重试次数
    :param conf["retry_time"]: 重试时间

    流程：
    run --> init_conf --> create_ijobs -->
    wait_ijobs --> finish_ijobs
    """

    def run(self):
        """
        --> init_conf
        --> create_ijobs
        """

        # 非正式环境跳过
        if settings.SOLUTION_DUMMY is not False:
            return self.set_finished("success", _("Pseudo execution"))

        self.common_ijobs_solution()

    def _get_operator(self):
        """
        获取ijobs的执行者，为该业务的运维
        """
        try:
            biz_id = self.alarm_instance['cc_biz_id']
            app_info = get_app_by_id(biz_id)
            verifier = app_info['Maintainers'].split(';')
        except BaseException:
            logger.exception(_("Error in obtaining maintenance information of business [%(biz_id)s]", biz_id=biz_id))
            verifier = []
        return verifier

    def get_git_server_operator(self):
        """
        获取全业务的业务运维
        """
        operator = []
        try:
            git_server_appid = bk.cc.get_git_server_ip()[0].get('ApplicationID')
            if git_server_appid:
                app_info = get_app_by_id(git_server_appid)
                operator = app_info['Maintainers'].split(';')
        except Exception as e:
            self.comment = _("Error in obtaining full business operator: %(error)s", error=e)
            self.logger.info(self.comment)
        return operator

    def common_ijobs_solution(self):
        # 初始化套餐配置
        self.init_ijobs_conf()

        # 检查是否使用完重试次数
        logger.debug("common_ijobs_solution: retry_count %r ==> %r", self.alarm_instance['id'], self.retry_count)
        if self.retry_count < 0:
            # 重试comment会被base修改，这里重新生成comment
            self.comment = self.get_ijobs_comment(self.alarm_instance['cc_biz_id'], self.task_id, _("Failure"))
            return self.set_finished(
                "failure", self.comment,
                failure_type="ijobs_failure",
            )

        # 扣除一次重试次数
        self.retry_count = self.retry_count - 1

        # 没有填 CC 传参参数，默认认为在故障机上执行
        # 则先检查故障机的 agent 是否正常
        # 如果不想检查，CC 参数不为空即可
        return self.create_ijobs()

    def get_step_ids(self):
        # 跨业务作业的 stepId 不用调用接口直接从配置项中取

        if self.is_platform_task:
            step_id = ALL_BIZ_STEP_ID.get(self.job_task_id)
            return [step_id]

        verifier = self._get_operator()
        if self.operator:
            verifier.insert(0, self.operator)
        for who in verifier:
            try:
                result = bk.job.get_task_detail__api(
                    __uin__=who,
                    app_id=self.conf.get('app_id', self.alarm_instance["cc_biz_id"]),
                    task_id=self.conf.get("task_id"),
                )
                result = map(lambda x: x['stepId'], result['nmStepBeanList'])
            except Exception as e:
                logger.warning("$%S get_step_ids error: %s", self.alarm_instance["id"], e)
                self.comment = _("(%s) Failed in obtaining ijobs task data: %s") % (who, e)
                self.logger.info(self.comment)
                raise e
            else:
                self.operator = who
                return result

    def init_ijobs_conf(self):
        if getattr(self, 'job_task_id', None) is None:

            self.job_task_id = self.conf.get("task_id")
            conf = VAR(self.alarm_instance).render_kwargs(self.conf)
            origin_alarm = json.loads(self.alarm_instance["origin_alarm"])
            plat_id = origin_alarm["_match_info"].get('cc_plat_id')

            logger.debug("job_task_id:%s, init_ijobs_conf: %r", self.job_task_id, self.alarm_instance['id'])

            self.retry_time = int(conf.get("retry_time", "1"))
            self.retry_count = int(conf.get("retry_count", "0"))
            self.parms = conf.get("parms") or None
            self.operator = conf.get("operator") or None
            self.is_platform_task = True if self.operator == '100' else False
            self.ip_address = VAR(self.alarm_instance).get_value("ip")

            steps = int(conf.get("steps") or 0)
            self.step_parms = []
            step_ids = self.get_step_ids()
            if step_ids is None:
                self.comment = _("Jobs return error")
                return self.set_finished(
                    "failure", self.comment,
                    failure_type="ijobs_failure",
                )
            for i in range(steps):
                step_parm = {}
                parm_key = "parms%s" % i
                if parm_key in conf and self.parms:
                    step_parm["scriptParam"] = conf[parm_key]
                step_parm['stepId'] = step_ids[i]
                if self.conf.get("replace_execute_ip", "on") == "on":
                    # 如果设置了替换ip才加这个参数，否则采用默认配置的ip
                    step_parm['ipList'] = "%s:%s" % (plat_id, self.ip_address)
                self.step_parms.append(step_parm)

            self.serialized_step_parms = json.dumps(self.step_parms)
        else:
            self.step_parms = json.loads(self.serialized_step_parms)
            logger.debug("step_parms: %r", self.step_parms)

    def create_ijobs(self):
        """
        --> wait_ijobs
        """
        # 创建 ijobs
        verifier = self._get_operator()
        if self.operator and self.operator != '100':
            verifier.insert(0, self.operator)

        for who in verifier:
            try:
                kwargs = {
                    '__uin__': who,
                    'task_id': self.job_task_id,
                    'steps': self.step_parms,
                }
                # 跨业务作业
                if self.is_platform_task:
                    kwargs.update({
                        'source_app_id': self.alarm_instance['cc_biz_id'],
                        'target_app_id': self.alarm_instance['cc_biz_id'],
                    })
                    self.task_id = bk.job.execute_platform_task__api(**kwargs)["taskInstanceId"]
                else:
                    kwargs.update({
                        'app_id': self.alarm_instance["cc_biz_id"],
                    })
                    self.task_id = bk.job.execute_task__api(**kwargs)["taskInstanceId"]
                logger.info(
                    "$%s create_ijobs: %s %s",
                    self.alarm_instance["id"], self.parms, self.step_parms)
            except Exception as e:
                # 失败
                logger.warning(
                    "$%s create_ijobs error: %s", self.alarm_instance["id"], e)
                self.comment = _("(%s) Failed in creating job task: %s") % (who, e)
                self.logger.info(self.comment)
            else:
                # 成功, 把有权限的用户更新为执行人
                self.operator = who
                return self.wait_ijobs()
        # 所有账号都执行失败, 重试
        self.wait_callback(
            "common_ijobs_solution", delta_seconds=int(self.retry_time))

    def wait_ijobs(self):
        """
        --> wait_ijobs
        --> finish_ijobs
        """
        # ijobs最小刷新间隔
        self.wait_ijobs_time = self.wait_ijobs_time or 12
        # 增加等待时间，最大60秒
        self.wait_ijobs_time = min(int(self.wait_ijobs_time * 1.5), 60)

        job_state = bk.job.on_error_retries(2).get_task_result(
            __uin__=self.operator,
            task_instance_id=self.task_id)['taskInstance']['status']

        if job_state in (1, 2):
            # 重试
            return self.wait_callback(
                "wait_ijobs", delta_seconds=int(self.wait_ijobs_time))
        # 执行成功
        elif job_state == 3:
            # 获取 context 参数
            if self.conf.get("argv"):
                self._get_argv()
            self.comment = self.get_ijobs_comment(self.alarm_instance['cc_biz_id'], self.task_id, _("Success"))
            return self.set_finished("success", self.comment)
        else:
            # 记录失败日志
            self.logger.info(get_failure_log(self.task_id, self.operator))
            self.comment = self.get_ijobs_comment(self.alarm_instance['cc_biz_id'], self.task_id, _("Failure"))
            # 重试
            self.wait_callback(
                "common_ijobs_solution", delta_seconds=int(self.retry_time))

    def _get_argv(self):
        """从 ijobs 日志获取 context 参数"""
        try:
            context = Context(self.alarm_instance["id"])
            get_argv_from_ijobs_log(self.task_id, self.operator, context)
        except Exception as e:
            logger.warning(
                "$%s get ijobs argv error: %s",
                self.alarm_instance["id"], e)

    def get_ijobs_comment(self, app_id, task_id, result_desc):
        """
        拼接结果描述
        """
        if IS_TASKS_RESULT_SPECIAL:
            if self.job_task_id == CLEAN_TASK_ID:
                context = Context(self.alarm_instance["id"])
                job_args = context['ijobs_return_clear_disk_result']

                return (_("Disk cleanup %s: %s") % (result_desc, job_args or '--'))
            if self.job_task_id == TOP_MEM_TASK_ID:
                return (_("Get the processes %s with Top 10 memory utilization") % result_desc)
            if self.job_task_id == TOP_CPU_TASK_ID:
                return (_("Get the processes %s with Top 10 CPU utilization") % result_desc)

        # 作业未创建成功
        if not task_id:
            return _("Failed to create job task")

        return _("Execute Job %(result_desc)s"
                 "<a target='_blank' href='%(link)s'>"
                 "[%(task_id)s]</a>",
                 result_desc=result_desc,
                 link=get_ijobs_link(app_id, task_id),
                 task_id=task_id
                 )


@try_exception(exception_return=_("Failed to obtain ijobs log"))
def __get_failure_log(task_id, operator):
    # 失败则获取执行日志
    job_log = bk.ijobs2.get_task_ip_log(
        __uin__=operator,
        task_instance_id=task_id)
    error_log_list = [
        # 去除日志中的空行，且只取最后5行
        '\n'.join(log['ipLog'][0]['content'].split('\n\n')[-5:])
        for log in job_log
        # 只获取失败步骤的日志
        if log['stepState'] == 4  # 失败
    ]
    error_log = _("job execution failed, log: \n%s") % (
        "\n------\n".join(error_log_list) if error_log_list else _("None"))
    return error_log


@try_exception(exception_return=_("Failed to obtain ijobs log"))
def get_failure_log(task_id, operator):
    # 失败则获取执行日志
    job_log = bk.job.get_task_ip_log(
        __uin__=operator,
        task_instance_id=task_id)
    error_log_list = []
    for step_log in job_log:
        # stepInstanceStatus 4 为执行失败
        # if step_log['stepInstanceStatus'] == 4:
        #     continue
        for ip_log in step_log['stepAnalyseResult']:
            for log in ip_log['ipLogContent']:
                error_log_list.append(
                    '\n'.join(log['logContent'].split('\n\n')[-5:]))
    error_log = _("job execution failed, log: \n%s") % (
        "\n------\n".join(error_log_list) if error_log_list else _("None"))
    return error_log


def get_argv_from_ijobs_log(task_id, operator, context):
    """
    从 ijobs 执行日志中获取变量，并赋值到context中
    :param task_id: ijobs 任务 ID
    :param content: 把匹配到的参数赋值给context
    """
    r = re.compile(r"FTAARGV (\w+):(.*)")
    job_log = bk.job.on_error_retries(2).get_task_ip_log(
        __uin__=operator,
        task_instance_id=task_id)
    for step_log in job_log:
        for ip_log in step_log['stepAnalyseResult']:
            for log in ip_log['ipLogContent']:
                for content_line in log['logContent'].split('\n'):
                    results = r.findall(content_line)
                    for result in results:
                        if result[0] == 'ip_bak':
                            context["%s" % result[0]] = result[1]
                        context["ijobs_%s" % result[0]] = result[1]


def get_ijobs_link(app_id, task_id):
    """
    拼接 ijobs 的任务链接
    :param task_id: ijobs 任务 ID
    """
    ins_url = '%s/?taskInstanceList&appId=%s#taskInstanceId=%s' % (
        JOB_ADDR, app_id, task_id)
    return (ins_url)
