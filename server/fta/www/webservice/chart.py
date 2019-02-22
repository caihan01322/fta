# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

import pygal
from flask import request
from fta.www.utils import response
from fta.www.utils.chart import Data
from fta.www.webservice import fta_simple_page as app


def get_chart_args():
    max_x = int(request.args.get("max_x", 5))
    begin = int(request.args.get("begin", 60 * 60 * 24))
    end = int(request.args.get("end", 0))
    interval = int(request.args.get("interval", 60))
    return max_x, begin, end, interval


@app.route("/chart/<chart_names>/", methods=["GET"])
@response.log
def chart(chart_names):
    chart_name_list = chart_names.split("__")
    max_x, begin, end, interval = get_chart_args()
    bar_chart = pygal.Line(
        height=350, style=pygal.style.LightSolarizedStyle, fill=True,
        show_dots=False, show_minor_x_labels=False)
    bar_chart.title = chart_names.replace("__", ", ")
    for chart_name in chart_name_list:
        key_list, value_list = Data.get_list(chart_name, begin, end, interval)
        bar_chart.x_labels = key_list
        bar_chart.x_labels_major = key_list[::(len(key_list) / max_x) + 1]
        bar_chart.add(chart_name, value_list)
    return bar_chart.render()


@app.route("/chart/<chart_names>/raw/", methods=["GET"])
@response.log
def chart_raw(chart_names):
    chart_name_list = chart_names.split("__")
    max_x, begin, end, interval = get_chart_args()
    result = {}
    for chart_name in chart_name_list:
        result[chart_name] = Data.get_list(chart_name, begin, end, interval)
    return json.dumps(result)
