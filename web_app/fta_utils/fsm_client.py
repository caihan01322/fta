# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

import requests
from django.conf import settings

BASE_URL = settings.FTA_CALL_BACK_URL


def retry(instance_id, node_idx, single_node_mode=False, base_url=BASE_URL):
    """
    所有节点均有重试按钮
    @single_node_mode 默认
    @base_url 默认
    2015.10.26
    """
    url = "%s%s/%s/" % (base_url, instance_id, node_idx)
    data = {} if single_node_mode is False else {"SINGLE_NODE_MODE": single_node_mode}
    data.update({
        'username': '100',
        'app_code': settings.APP_CODE,
        'app_secret': settings.SECRET_KEY
    })
    r = requests.post(url, data=data, verify=False)
    r.raise_for_status()
    if not r.json()["result"]:
        raise Exception(r.json()["message"])


def callback(esb_id, data, base_url=BASE_URL):
    url = "%s%s/" % (base_url, esb_id)
    data.update({
        'username': '100',
        'app_code': settings.APP_CODE,
        'app_secret': settings.SECRET_KEY
    })
    r = requests.post(url, data=data, verify=False)
    r.raise_for_status()


def approve(instance_id, approved, verifier, message, base_url=BASE_URL):
    """
    状态为waiting需要审批
    @approved true/false
    2015.10.26
    """
    approve_fake_esb_id = "waiting_approve_%s_%s" % (instance_id, -1)
    approve_data = {
        "approved": approved,
        "verifier": verifier,
        "message": message
    }
    callback(approve_fake_esb_id, approve_data, base_url)


def convert_solution2graph(solution):
    """
    convert solution dict to graph_json
    :param solution: solution orm obj
    :return graph_json: FSM's std structure
    """
    if solution.solution_type == "graph":
        graph_conf = json.loads(solution.config)
        graph_json = json.loads(graph_conf["real_solutions"])
    elif solution.solution_type == "diy":
        diy_conf = json.loads(solution.config)
        tree_json = json.loads(diy_conf["real_solutions"])
        graph_json = convert_tree2graph(tree_json)
    elif solution.id:
        # create fake graph_json
        graph_json = [({}, solution.id)]
    else:
        graph_json = []
    return graph_json


def convert_tree2graph(tree_json):
    idx_tree2graph_map = {1: 0}
    graph_json = []
    tree_idx_list = sorted(map(int, tree_json.keys()), reverse=True)
    for graph_idx_delta, tree_idx in enumerate(tree_idx_list):
        graph_idx = len(tree_idx_list) - graph_idx_delta
        idx_tree2graph_map[tree_idx] = graph_idx
        status_dict = {}
        if tree_json.get(str(tree_idx * 2)):
            status_dict[idx_tree2graph_map[tree_idx * 2] - 1] = ["success"]
        if tree_json.get(str(tree_idx * 2 + 1)):
            status_dict[idx_tree2graph_map[tree_idx * 2 + 1] - 1] = ["~success"]
        graph_json.insert(0, (status_dict, tree_json[str(tree_idx)]))
    return graph_json
