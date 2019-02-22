# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import importlib
import json
import re
import types

import arrow

from fta import constants
from fta.utils import logging
from fta.utils.context import Context
from project.utils import get_plat_info, people
from project.utils.query_cc import get_host_info, get_module_id_by_name

logger = logging.getLogger("solution")


class VAR(object):

    """
    查询渲染，将套餐中配置的参数渲染为真实值
    """

    def __init__(self, alarm_instance):
        self.alarm_instance = alarm_instance
        self.context = Context(alarm_instance["id"])
        # alias failover_ip to alarm_ci_name
        self.context.alarm_ci_name = alarm_instance["ip"]
        verifier = people.get_verifier(self.alarm_instance["id"])
        self.context["operator"] = verifier[0] if verifier else ""
        self.context["operators"] = verifier
        # 告警信息中的上下文
        self.context["alarm_context"] = alarm_instance["tnm_alarm"]

    def render_kwargs(self, task_kwargs):
        """输入带变量的参数，返回渲染结果。可以用来测试参数的正确性。"""
        var_str_match = re.compile(r"\$\{\s*[\w\|]+\s*\}")
        var_name_match = re.compile(r"\$\{\s*([\w\|]+)\s*\}")
        for key, value in task_kwargs.items():
            value = json.dumps(value)
            var_str_list = var_str_match.findall(value)
            var_name_list = var_name_match.findall(value)
            for var_name, var_str in zip(var_name_list, var_str_list):
                value = value.replace(var_str, self.get_value(var_name))
            try:
                task_kwargs[key] = json.loads(value)
            except ValueError:
                # 去除引号
                task_kwargs[key] = value[1:-1]
        return task_kwargs

    def get_value(self, var_name):
        if var_name.startswith("cc|"):
            var_value = self.get_value_from_cc(var_name)
        elif var_name.startswith("bpm_context|"):
            var_value = self.get_value_from_context(var_name)
        elif var_name == "__alarm__":
            var_value = self.get_value_from_instance()
        elif var_name.startswith("alarm_context"):
            var_value = self.get_value_from_alarm_context(var_name)
        else:
            var_value = self.context[var_name] or self.alarm_instance.get(var_name) or ""
        if var_name == "source_time":
            var_value = var_value.strftime(constants.STD_DT_FORMAT)
        return unicode(var_value)

    def get_value_from_alarm_context(self, var_name):
        """告警信息中的上下文
        """
        alarm_context = getattr(self.context, "alarm_context") or ""
        if var_name == "alarm_context":
            return alarm_context

        try:
            alarm_context = json.loads(alarm_context)
        except BaseException:
            logger.error(u"alarm_context 解析出错:\n%s" % alarm_context)
            alarm_context = ""

        if not isinstance(alarm_context, dict):
            return ""

        # 上下文为 dict 则可以进一步取 key 的值
        if var_name.startswith("alarm_context|"):
            key_name = var_name.split("|", 1)[1]
            return alarm_context.get(key_name, "")

        return ""

    def get_value_from_context(self, var_name):
        """获取 Context 变量的取值"""
        attr_name = var_name.split("|", 1)[1]
        return getattr(self.context, attr_name) or ""

    def get_value_from_cc(self, var_name):
        """获取 cc 变量的取值"""
        attr_name = var_name.split("|", 1)[1]
        argvs = var_name.split("|")[2:]

        # 获取空闲机模块
        if attr_name == "idle_module_id":
            app_id = self.alarm_instance["cc_biz_id"]
            # do not use i18n
            idle_module_id = get_module_id_by_name(app_id, u"空闲机")
            return idle_module_id

        # 获取故障机模块
        if attr_name == "fault_module_id":
            app_id = self.alarm_instance["cc_biz_id"]
            # do not use i18n
            idle_module_id = get_module_id_by_name(app_id, u"故障机")
            return idle_module_id

        if "alarm_ci_name" in argvs:
            ip = self.context.alarm_ci_name
        elif "ip_bak" in argvs:
            ip = self.context.ip_bak
            attr_name = attr_name.replace("|ip_bak", "")
        else:
            ip = self.context.ip or self.context.alarm_ci_name
        plat_info = get_plat_info(self.alarm_instance)
        host_info = get_host_info(
            plat_info['plat_id'], plat_info['company_id'], ip)

        return host_info.get(attr_name, '') or plat_info.get(attr_name, '')

    def get_value_from_instance(self):
        """获取alarm_instance内容"""
        _instance = {}
        for k, v in self.alarm_instance.items():
            if isinstance(v, datetime.datetime):
                new_v = arrow.get(v).format(constants.STD_ARROW_FORMAT)
                _instance[k] = new_v
            else:
                _instance[k] = v
        return json.dumps(_instance)


class BaseHook(object):

    @staticmethod
    def pre(alarm_instance, **kwargs):
        pass

    @staticmethod
    def post(alarm_instance, esb_id):
        pass

    @staticmethod
    def callback(alarm_instance, result):
        pass


class Hook(object):

    def __init__(self, module_name, task_name):
        try:
            module = importlib.import_module(
                "manager.solution.bk_component.%s" % module_name)
            self.obj = getattr(module, task_name)
        except Exception:
            # logger.exception(e)  # for debug
            self.obj = BaseHook

        if not isinstance(self.obj, types.FunctionType):
            self.pre = self.obj.pre
            self.post = self.obj.post
            self.callback = self.obj.callback
