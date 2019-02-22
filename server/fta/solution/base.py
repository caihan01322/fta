# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import importlib
import inspect
import json
import time

from fta import constants, settings
from fta.storage.cache import Cache
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import hooks, instance_log, logging, remove_blank
from fta.utils.context import Context
from fta.utils.continuation import (WaitCallback, wait_callback,
                                    wait_esb_callback, wait_polling_callback)
from fta.utils.i18n import _, lazy_gettext
from fta.utils.timeout import get_timeout_time
from manager.define.solution import SolutionManager

logger = logging.getLogger("solution")

redis_cache = Cache("redis")

WCB_DUMMY = getattr(settings, "WCB_DUMMY", False)
hook = hooks.HookManager("fsm")

UNSET_RESULT = "--unset_result--"


class MetaSolution(type):
    """
    Solution Hook实现
    """

    def __new__(cls, name, bases, nmspc):
        klass = type.__new__(cls, name, bases, nmspc)
        # discover project.solution.[module].Solution
        klass = MetaSolution.__hook__(klass)
        return klass

    @staticmethod
    def __hook__(cls):
        """hook project solution
        注意: 不能直接继承manager.solution.[module].Solution
        """
        if 'manager' not in cls.__module__:
            return cls
        try:
            module = cls.__module__.replace('manager', 'project')
            solution_mod = importlib.import_module(module)
            klass = getattr(solution_mod, cls.__name__)

            # hook can get original class
            setattr(klass, '__origin__', cls)
            # init new klass with mixin
            klass = type(klass.__name__, (klass, cls), {"__module__": klass.__module__, })
            logger.info('get %s solution class: %s' % (cls, klass))
            return klass
        except (ImportError, AttributeError):
            return cls


class BaseSolution(Context):
    __metaclass__ = MetaSolution

    def __init__(self, alarm_instance, node_idx, run_times=0):
        """
        :param alarm_instance: alarm_instance dict
        :param node_idx: node index in graph_json
        :param run_times: instance's retry counter
        """

        solution_instance_id = self.get_context_id(alarm_instance["id"], node_idx, run_times)
        super(BaseSolution, self).__init__(solution_instance_id)

        self.alarm_instance = alarm_instance
        self.alarm_def = self.get_alarm_def(alarm_instance)
        self.node_idx = node_idx
        self._run_times = run_times

        self.solution = self.get_solution(alarm_instance, node_idx)
        self.conf = json.loads(self.solution["config"] or "{}")

        self.result = self.result or UNSET_RESULT
        self.comment = self.comment or _("Unknown result")

    @property
    def logger(self):
        return Logger(self.alarm_instance["id"], self.node_idx)

    @staticmethod
    def get_context_id(instance_id, node_idx, run_times=None):
        context_desc_list = [instance_id, node_idx] + remove_blank([run_times or Context(instance_id).RUN_TIMES])
        return "-".join(map(str, context_desc_list))

    @staticmethod
    def get_alarm_def(alarm_instance):
        alarm_def = json.loads(alarm_instance["snap_alarm_def"])
        return alarm_def

    @staticmethod
    def get_solution(alarm_instance, node_idx):
        """
        get node solution
        :param alarm_instance: alarm_instance dict
        :param node_idx: node index in graph_json
        """
        solution = json.loads(alarm_instance["snap_solution"])
        graph_json = BaseSolution.convert_solution2graph(solution)
        solution_id = str(graph_json[int(node_idx)][1])
        return SolutionManager().raw_solution_dict[solution_id]

    @staticmethod
    @hook.patch("convert_solution2graph")
    def convert_solution2graph(solution):
        if solution["solution_type"] == "graph":
            graph_conf = json.loads(solution["config"])
            return json.loads(graph_conf["real_solutions"])
        else:
            return [({}, solution["id"])]

    def wait_esb_callback(self, callback_func, esb_id, timeout=0, dummy=WCB_DUMMY, dummy_result={}):
        """
        wait callback by ESB:
        >>> callback_func(self, result=esb_callback_value)

        in fact, it will end process,
        while receive a http callback, exec as a new process

        :param callback_func: func_name, should be Solution's instance function
        :param esb_id: esb_id's task id
        :param dummy: bool, if dummy is True, will not end process
        :param dummy_result: dict, if has dummy_result, return fake callback
        """
        callback_module = self.CALLBACK_MODULE or inspect.getmodule(inspect.stack()[1][0]).__name__
        callback_timeout = timeout or get_timeout_time(self.alarm_instance)
        logger.info(
            "$%s &%s wcb_esb to %s.%s timeout(%s): %s",
            self.alarm_instance["id"], self.node_idx,
            callback_module, callback_func, callback_timeout, esb_id)
        if dummy:
            logger.info("$%s &%s dummy result: %s", self.alarm_instance["id"], self.node_idx, dummy_result)
            return getattr(self, callback_func)(**dummy_result)
        wait_timeout_kwargs = {
            "esb_id_": esb_id,
            "func_": callback_func,
            "timeout_": callback_timeout
        }
        self.comment = _("Wait for ESB callback")
        wait_callback(
            self.alarm_instance["id"], self.node_idx, self._run_times,
            callback_module, "timeout_callback",
            wait_timeout_kwargs, callback_timeout)
        wait_esb_callback(
            self.alarm_instance["id"], self.node_idx, self._run_times,
            callback_module, callback_func, esb_id)

    def wait_polling_callback(self, callback_func, url, kwargs={}, delta_seconds=0, dummy=WCB_DUMMY, dummy_result={}):
        """
        sleep 'delta_seconds' then polling from url with kwargs:
        >>> import requests
        >>> result = requests.post(url, **kwargs)

        callback 'callback_func'. action like:
        >>> time.sleep(delta_seconds)
        >>> callback_func(self, result=result)

        in fact, it will end process,
        then put job into queue delay delta_seconds, exec as a new process

        :param callback_func: func_name, should be Solution's instance function
        :param kwargs: polling's kwargs: requests.post(url, **kwargs)
        :param delta_seconds: callback after delta_seconds
        :param dummy: bool, if dummy is True, will not end process
        :param dummy_result: dict, if has dummy_result, use time.sleep for wait
        """
        callback_module = self.CALLBACK_MODULE or inspect.getmodule(inspect.stack()[1][0]).__name__
        logger.info(
            "$%s &%s wcb_polling to %s.%s wait(%s): %s",
            self.alarm_instance["id"], self.node_idx,
            callback_module, callback_func, delta_seconds, url
        )
        if dummy:
            time.sleep(delta_seconds)
            return getattr(self, callback_func)(**dummy_result)

        self.comment = _("Wait for Polling callback")
        wait_polling_callback(
            self.alarm_instance["id"], self.node_idx, self._run_times,
            callback_module, callback_func,
            url, kwargs, delta_seconds)

    def wait_callback(self, callback_func, kwargs={}, delta_seconds=0, dummy=WCB_DUMMY):
        """
        sleep 'delta_seconds' then callback 'callback_func'. action like:
        >>> time.sleep(delta_seconds)
        >>> callback_func(self, **kwargs)

        in fact, it will end process,
        then put job into queue delay delta_seconds, exec as a new process

        :param callback_func: func_name, should be Solution's instance function
        :param kwargs: callback_func's kwargs: callback_func(self, **kwargs)
        :param delta_seconds: callback after delta_seconds
        :param dummy: bool, if dummy is True, use time.sleep for wait
        """
        callback_module = self.CALLBACK_MODULE or inspect.getmodule(inspect.stack()[1][0]).__name__
        logger.info(
            "$%s &%s wcb to %s.%s wait(%s)",
            self.alarm_instance["id"], self.node_idx,
            callback_module, callback_func, delta_seconds
        )
        if dummy:
            time.sleep(delta_seconds)
            return getattr(self, callback_func)(**kwargs)
        self.comment = _("Wait for callback")
        wait_callback(
            self.alarm_instance["id"], self.node_idx, self._run_times,
            callback_module, callback_func, kwargs, delta_seconds)

    def timeout_callback(self, esb_id_, func_, timeout_):
        logger.info(
            "$%s &%s timeout_callback %s esb_id(%s) timeout(%s)",
            self.alarm_instance["id"], self.node_idx,
            func_, esb_id_, timeout_
        )
        if self.result == UNSET_RESULT:
            self.set_finished("failure", _("Component callback waiting timed out"), failure_type="timeout", )
        else:
            raise WaitCallback("pass_timeout_callback")

    def is_finished(self):
        """
        check whether solution is finished
        :return bool: whether finished
        """
        return getattr(self, "_is_finished", False)

    def update_monitor_status(self):
        key = "solution_monitor_{status}".format(status=self.result)
        redis_cache.incr(key)
        if self.failure_type:
            redis_cache.incr("{key}:{failure_type}".format(key=key, failure_type=self.failure_type, ))

    def set_finished(self, result, comment, failure_type=None):
        """
        mark solution finished
        :param result: solution's result status
        :param comment: solution's result description
        :return result, comment:
        """
        assert result in constants.INSTANCE_END_STATUS
        self._acquire("result", UNSET_RESULT, result)
        self.comment = comment
        self.failure_type = failure_type
        self._is_finished = True
        if failure_type:
            session.query(
                FtaSolutionsAppAlarminstance
            ).filter_by(id=self.alarm_instance["id"], ).update({"failure_type": failure_type})
        elif result == "failure":
            logger.error("failure_type not set for %s", self.alarm_instance["id"], )
        self.logger.info("%s | %s: %s", lazy_gettext(self.solution["title"]), self.result_desc, self.comment)
        self.update_monitor_status()
        return self.result, self.comment

    def set_comment(self, comment, *args):
        instance_log.update_alarm_instance_comment(alarm_instance_id=self.alarm_instance["id"], comment=comment % args)

    @property
    def result_desc(self):
        return constants.INSTANCE_STATUS_DESCRIPTION.get(self.result, self.result)

    def run(self):
        raise Exception('Should have run() method for Solution')


class Logger(object):

    def __init__(self, instance_id, node_idx):
        self.instance_id = instance_id
        self.node_idx = node_idx

    def record(self, level, message, args):
        instance_log.update_alarm_instance_comment(
            alarm_instance_id=self.instance_id,
            comment=message if not args else message % args,
            step_name="graph_solution_%s" % self.node_idx,
            level=level,
            cover=False)

    def debug(self, content, *args):
        self.record(logging.DEBUG, content, args)

    def info(self, content, *args):
        self.record(logging.INFO, content, args)

    def warning(self, content, *args):
        self.record(logging.WARNING, content, args)

    def error(self, content, *args):
        self.record(logging.ERROR, content, args)
