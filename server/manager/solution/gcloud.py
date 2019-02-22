# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from datetime import datetime

from fta import settings
from fta.solution.base import BaseSolution
from fta.utils import get_first, logging
from fta.utils.i18n import _
from manager.solution.bk_component import VAR
from project.utils import people
from project.utils.component import bk
from project.utils.query_cc import get_app_by_id

logger = logging.getLogger("solution")


class Solution(BaseSolution):
    """
    游戏云套餐，调用游戏云流程

    :param conf["task_id"]: 任务 ID
    :param conf["task_parameters"]: 任务参数
    :param conf["steps_selected"]: 忽略不执行的步骤
    :param conf["auth_code"]: 授权码
    """
    wait_time = 2

    def get_common_args(self, **kwargs):
        return kwargs

    def get_gclient(self):
        self.cc_biz_id = self.alarm_instance['cc_biz_id']
        gclient = bk.sops
        # 使用v2的API
        gclient._prefix = 'compapi/v2'
        return gclient

    def run(self):
        try:
            app_info = get_app_by_id(self.alarm_instance['cc_biz_id'])
            verifier = app_info['Maintainers'].split(';')
        except BaseException:
            verifier = people.get_verifier(self.alarm_instance["id"])
        self.operator = get_first(verifier)
        self.conf = VAR(self.alarm_instance).render_kwargs(self.conf)

        # 参数按照新的格式组装${key} 格式
        task_parameters = {
            k[7:]: v
            for k, v in self.conf.items()
            if k.startswith("params_")
        }

        try:
            steps_selected = self.conf.get('steps_selected', '')
            if steps_selected:
                steps_selected = steps_selected.split(",")
            else:
                steps_selected = []
            self.start_task(
                self.conf['template'],
                task_parameters,
                steps_selected,
            )
        except Exception as e:
            logger.exception(e)
            return self.set_finished(
                "failure",
                _("Failed to call game cloud custom flow template: %(error)s", error=e),
                failure_type="gcloud_failure",
            )

    def start_task(self, template_id, task_parameters,
                   steps_selected):

        # dummy call
        if settings.SOLUTION_DUMMY is not False:
            return self.set_finished("success", _("Pseudo execution"))

        gclient = self.get_gclient()
        # 快速创建任务
        # not database record, use local time
        task_name = self.conf.get(
            "task_name", _("FTA(%(now)s)", now=datetime.now()),
        )
        # 标准运维限制名字长度为 40
        task_name = task_name[:40]
        create_task_parameters = {
            "bk_username": self.operator,
            "bk_biz_id": self.cc_biz_id,
            "template_id": template_id,  # 任务模板
            "name": task_name,
            "constants": task_parameters,  # 任务参数key-value
        }
        try:
            result = gclient.create_task(
                **create_task_parameters
            )
        except Exception as e:
            return self.set_finished(
                "failure", _("Failed to create Standard OPS task: %(error)s", error=e),
                failure_type="gcloud_failure",
            )

        # execute task
        if not result.get("task_id"):
            return self.set_finished(

                "failure", result.get("message", _("Failed to create Standard OPS task")),
                failure_type="gcloud_failure",
            )
        task_id = result["task_id"]
        logger.info("ready to execute task: %s", task_id)

        return self.execute_task(task_id, self.operator, self.timeout)

    def execute_task(self, task_id, operator, timeout=60 * 60 * 2):
        gclient = self.get_gclient()
        try:
            gclient.start_task(**{
                "bk_username": operator,
                "bk_biz_id": self.cc_biz_id,
                "task_id": task_id,
            })
        except Exception as e:
            return self.set_finished(
                "failure", _("Failed to execute Standard OPS task: %(error)s", error=e),
                failure_type="gcloud_failure",
            )
        return self.wait_gcloud(task_id, operator)

    def wait_gcloud(self, bpm_task_id, operator, timeout=60 * 60 * 2):
        # 标准运维有暂停功能,有些游戏云任务可能会暂停好几天,所以需要设置一个超时时间
        self.timeout = self.timeout or timeout
        self.wait_time = self.wait_time or 10
        self.wait_time = self.wait_time * 1.5
        self.timeout = self.timeout - self.wait_time
        self.operator = operator
        gclient = self.get_gclient()
        result = gclient.get_task_status(**{
            "bk_username": operator,
            "bk_biz_id": self.cc_biz_id,
            "task_id": bpm_task_id,
        })
        logger.info(
            "$%s &%s gcloud task_state: %s",
            self.alarm_instance["id"], self.node_idx, result)
        # if not result['result']:
        #     # 查询任务执行状态失败, 则稍候继续查询
        #     return self.wait_callback(
        #         "wait_gcloud",
        #         kwargs={
        #             "bpm_task_id": bpm_task_id,
        #             "operator": operator,
        #             "timeout": timeout
        #         },
        #         delta_seconds=self.wait_time)

        task_state = result
        # 标准运维任务详情链接
        link = "{gcloud_url}taskflow/execute/{cc_biz_id}/?instance_id={task_id}".format(
            gcloud_url=settings.GCLOUD_DETAIL_ENDPOINT,
            cc_biz_id=self.cc_biz_id,
            task_id=bpm_task_id
        )

        link_html = "<a target='_blank' href='{link}'>{task_id}</a>".format(
            link=link,
            task_id=bpm_task_id,
        )
        if task_state['state'] == 'FINISHED':
            return self.set_finished(
                "success", _("Standard OPS template execution successful [%(link)s]", link=link_html),
            )
        elif task_state['state'] == 'FAILED':
            return self.set_finished(
                "failure",
                _("Standard OPS template execution failed [%(link)s]: %(message)s",
                  link=link_html, message=task_state.get("message", "")),
                failure_type="gcloud_failure",
            )
        elif self.timeout <= 0:
            return self.set_finished(
                "failure",
                _("Standard OPS template execution timeout [%(link)s]: %(message)s",
                  link=link_html, message=task_state.get("message", "")),
                failure_type="timeout",
            )
        return self.wait_callback(
            "wait_gcloud",
            kwargs={
                "bpm_task_id": bpm_task_id,
                "operator": operator,
                "timeout": self.timeout
            },
            delta_seconds=self.wait_time)
