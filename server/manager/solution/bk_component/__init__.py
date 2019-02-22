# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta import settings
from fta.utils import logging
from fta.solution.base import BaseSolution

from project.utils.component import bk
from manager.solution.bk_component.utils import VAR
from manager.solution.bk_component.utils import Hook
from fta.utils.i18n import _

import types
import json

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    直接调用组件套餐

    事实上有三种情况：
    1. 特殊封装的组件，在 bk_component 目录下有实现，则直接调用
    2. 直接调用接口

    :param conf["module_name"]: 组件模块名
    :param conf["task_name"]: 组件任务名
    :param conf["task_kwargs"]: 组件任务参数
    :param conf["retry"]: 是否创建失败重试
    """

    DUMMY_RESULT = {"result": {"result": "True", "message": _("Pseudo execution component success")}}

    def __init__(self, *args, **kwargs):
        super(Solution, self).__init__(*args, **kwargs)

        # get module name
        module_name = self.conf.get("module_name", "")
        if module_name.startswith("bk."):
            module_name = module_name[3:]
        self.module_name = module_name

        # get task name
        self.task_name = self.conf.get("task_name")

        # get task kwargs
        task_kwargs = json.loads(self.conf.get("task_kwargs", "{}"))
        if self.alarm_def.get("operator"):
            task_kwargs["__uin__"] = self.alarm_def.get("operator")
        self.task_kwargs = VAR(self.alarm_instance).render_kwargs(task_kwargs)
        if settings.SOLUTION_DUMMY is not False:
            self.task_kwargs["dummy"] = True
            self._dump()
        logger.info('bk_component_log task_name:%s, task_kwargs:%s', self.task_name, self.task_kwargs)

    def run(self):
        # 如果存在特殊实现的组件，那么直接调用
        customized_component = Hook(self.module_name, self.task_name).obj
        logger.info("bk_component_log" + "-" * 10 + "%s", customized_component)
        if isinstance(customized_component, types.FunctionType):
            logger.info("bk_component_log $%s &%s customized_component",
                        self.alarm_instance["id"], self.node_idx)
            return self.call_custom(customized_component, self.task_kwargs)

        # 如果存在配置的组件，那么直接调用
        if self.module_name in bk._getAttributeNames():
            module = getattr(bk, self.module_name)

            if self.task_name in module._getAttributeNames():
                bk_func = getattr(module, "%s__api" % self.task_name)
                logger.info("bk_component_log $%s &%s call_bk:%s",
                            self.alarm_instance["id"], self.node_idx, bk_func)
                return self.call_bk(bk_func, self.task_kwargs)

    def call_custom(self, customized_component, task_kwargs):
        try:
            customized_component(self.alarm_instance, **task_kwargs)
            self.finish("True")
        except Exception as e:
            logger.warning(
                "bk_component_log $%s &%s call_custom error: %s",
                self.alarm_instance["id"], self.node_idx, e)
            self.finish("False", e)

    def call_bk(self, bk_func, task_kwargs):
        try:
            if settings.SOLUTION_DUMMY is not False:
                return self.set_finished("success", u"伪执行")
            else:
                try:
                    result = bk_func(**task_kwargs)
                except BaseException:
                    # 如果配置了重试，则创建失败时重试一次
                    if self.conf.get("retry"):
                        result = bk_func(**task_kwargs)
                    else:
                        raise
            logger.info(
                "bk_component_log $%s bk_component_callback: %s.%s: %s",
                self.alarm_instance["id"],
                self.module_name, self.task_name, json.dumps(result))
            self.finish("True")
        except Exception as e:
            comment = _("Failed to create BlueKing %(module_name)s component %(task_name)s task: %(error)s",
                        module_name=self.module_name, task_name=self.task_name, error=e)
            logger.exception(
                "bk_component_log $%s bk_component: %s.%s: %s",
                self.alarm_instance["id"],
                self.module_name, self.task_name, e)
            return self.set_finished(
                "failure", comment, failure_type="user_code_failure",
            )

    def finish(self, result, message=""):
        if result == "True":
            comment = _("BlueKing %(module_name)s component %(task_name)s task execution successful",
                        module_name=self.module_name, task_name=self.task_name)
            return self.set_finished(
                "success",
                comment)
        else:
            comment = _("Failed to execute BlueKing %(module_name)s component %(task_name)s task: %(message)s",
                        module_name=self.module_name, task_name=self.task_name, message=message)
            return self.set_finished(
                "failure",
                comment)
