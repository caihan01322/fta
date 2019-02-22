# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa


from fta.utils import hooks, logging
from fta.utils.context import Context

logger = logging.getLogger("solution")
hook = hooks.HookManager("fsm")


class Node(object):

    def __init__(self, idx, node_json):
        self.idx = str(idx)
        self.prefix_status_dict = node_json[0]
        self.solution_id = str(node_json[1])

    def json(self):
        """({idx: ["status1", "status2"]}, solution_id)"""
        return (self.prefix_status, self.solution_id)


class BasicGraph(object):

    def __init__(self, instance_id, graph_json):
        self.instance_id = instance_id
        self.graph_json = graph_json
        self.node_list = [Node(idx, node_json)
                          for idx, node_json in enumerate(graph_json)]

    @staticmethod
    def filter_include_status(status_list):
        return [status_value for status_value in status_list if not status_value.startswith("~")]

    @staticmethod
    def filter_exclude_status(status_list):
        return [status_value[1:] for status_value in status_list if status_value.startswith("~")]

    @classmethod
    def is_include(cls, now_status_list, status_list):
        # 判断当前状态是否没完整包含“是”状态
        if not set(cls.filter_include_status(status_list)).issubset(set(now_status_list)):
            return False
        # 判断当前状态是否包含“非”状态
        if set(cls.filter_exclude_status(status_list)) & set(now_status_list):
            return False
        return True

    def json(self):
        return self.graph_json


class Graph(BasicGraph):
    """graph_json:
    [(
        {
            # 当本节点的执行结果为 status1 或 status2 时，执行 idx1 节点
            idx1: ["status1", "status2"],
            # 且本节点的执行结果为 status1 或 status3 时，执行 idx2 节点
            idx2: ["status1", "status3"],
        },
        # 本节点的套餐
        solution_id
    )]
    """

    def get_sub(self, now_status_dict, latest_idx):
        # 根据最新执行完成的节点及其状态, 获取接下来要执行的节点
        if latest_idx is None:
            return ["0"]
        latest_status = now_status_dict[latest_idx][-1]
        node = self.node_list[int(latest_idx)]
        return [
            str(idx) for idx, status_list in node.prefix_status_dict.items() if
            self.is_include([latest_status], status_list)
        ]


class GraphReverse(BasicGraph):
    """graph_json:
    [(
        {
            # 当 idx1 节点的执行结果为 status1 或 status2
            idx1: ["status1", "status2"],
            # 且 idx2 节点的执行结果为 status1 或 status3
            idx2: ["status1", "status3"],
        },
        # 则执行本节点的套餐
        solution_id
    )]
    """

    def get_sub(self, now_status_dict, latest_idx):
        return [
            node.idx for node in self.node_list if
            not now_status_dict.get(node.idx) and self._is_sub(node, now_status_dict)
        ]

    def _is_sub(self, node, now_status_dict):
        for idx, prefix_status_list in node.prefix_status_dict.items():
            now_status_list = now_status_dict.get(idx)
            # 当前状态没有执行过idx节点,不匹配
            if now_status_list is None:
                return False
            if self.is_include(now_status_list, prefix_status_list) is False:
                return False
        return True


class FSM(object):
    GRAPH = Graph

    def __init__(self, instance_id, graph_json, run_times=0):
        self.instance_id = instance_id
        self.context = self.get_context(instance_id, run_times)
        self.context.now_status_dict = {"0": []}
        self.context.wait_node = self.context.wait_node or []
        self.context.result_list = []
        self.latest_idx = None
        self.graph = self.GRAPH(instance_id, graph_json)

    @classmethod
    def get_context(cls, instance_id, run_times):
        context_id = instance_id if not run_times else str(instance_id) + str(run_times)
        return Context(context_id, postfix="fsm")

    def result_list(self):
        logger.info("$%s result_list: %s", self.instance_id, self.context.result_list)
        return self.context.result_list

    def input_status(self):
        # 获取所有等待完成的节点和接下来要执行的节点
        current_run_node = self.graph.get_sub(self.context.now_status_dict, self.latest_idx)
        self.context.wait_node += current_run_node
        logger.info("$%s input_status: %s, %s", self.instance_id, self.context.wait_node, current_run_node)
        if current_run_node:
            self.context.result_list = []
        else:
            self.context.result_list.append(self.latest_status_value)
        self.context._dump()
        return self.context.wait_node, current_run_node

    def receive(self, idx, status_value):
        # 把最新完成的节点信息保存在上下文中
        self.latest_idx, self.latest_status_value = idx, status_value
        logger.info("$%s receive: %s, %s", self.instance_id, idx, status_value)
        try:
            # 把已经完成的节点从等待列表中移除
            self.context.wait_node.remove(str(idx))
        except Exception as e:
            logger.error("FSM remove wait_node %s from %s: %s", idx, self.context.wait_node, e)
            raise
        self.context.now_status_dict.setdefault(str(idx), []).append(status_value)
        self.context._dump()
        logger.info("$%s now_status_dict: %s", self.instance_id, self.context.now_status_dict)
