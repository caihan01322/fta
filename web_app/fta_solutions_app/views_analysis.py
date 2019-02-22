# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import logging
from collections import OrderedDict
from datetime import timedelta

import arrow
from django.db import connection
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET

import cache_utils as cash
from common.django_utils import strftime_local
from common.mymako import render_mako_context
from fta_solutions_app import fta_std
from fta_solutions_app.activity_log import (
    OBJECT_TYPE, OPERATOR_TYPE_VALUES, ActivityLogClient,
)
from fta_solutions_app.cache_utils import get_all_user_info
from fta_solutions_app.models import (
    OutOfScopeArchive, AlarmInstanceArchive,
    Incident, IncidentAlarm, Advice, AlarmType,
)
from fta_utils.cc import CCBiz
from fta_utils.date_tool import get_date_range, try_parse_datetime
from fta_utils.utils import func_catch

logger = logging.getLogger(__name__)

"""
views_analysis和views_data主要区别是:
analysis包括了未接入的告警数据
"""


@require_GET
def index(request, cc_biz_id=0):
    """
    自愈趋势图表，0代表全业务
    """
    username = request.user.username
    if cc_biz_id:
        cc_biz_name = CCBiz(username, str(cc_biz_id)).get("ApplicationName", _(u"*未知(id:{})*").format(cc_biz_id))
    else:
        cc_biz_name = _(u"全业务")

    alarm_type_dict = OrderedDict({'': _(u'全部')}, **AlarmType.get_description_mappings(cc_biz_id))

    kwargs_query = {}
    if cc_biz_id:
        kwargs_query['cc_biz_id'] = cc_biz_id

    sol_type_list = AlarmInstanceArchive.objects.filter(**kwargs_query).distinct().values_list('solution_type',
                                                                                               flat=True)
    SOL_TYPES = dict(fta_std.SOLUTION_TYPE_CHOICES)
    for _type in fta_std.NO_DISPLAY_SOLUTION_TYPE:
        SOL_TYPES.pop(_type)
    SOL_TYPES['sleep'] = _(u"不处理(仅通知)")  # 特殊套餐特别备注

    teams = cash._get_cc_biz_by_group(username).keys()
    teams = filter(lambda t: t, teams)

    end_time = strftime_local(timezone.now(), "%Y-%m-%d")
    start_time = strftime_local((timezone.now() + timedelta(days=-30)), "%Y-%m-%d")

    # 今日自愈次数
    solution_count_today = get_solution_count_by_day(cc_biz_id)
    # 今日收敛次数
    convergs_count_today = get_convergs_count_by_day(cc_biz_id)
    # 健康诊断建议
    advice_count = get_advice_count(cc_biz_id)
    # 30 天节省人工耗时
    consumes_30days = get_consumes_by_30day(cc_biz_id)
    # 自愈小组手
    suggest_count = OutOfScopeArchive.get_suggest_count(cc_biz_id)
    return render_mako_context(request, '/fta_solutions/analysis.html', locals())


@func_catch(logger.exception)
def operational_audit_detail(request, cc_biz_id):
    query_parmas = dict(app_code=cc_biz_id)
    query_parmas.update({
        k: request.GET[k]
        for k in ["user", "content", "operator_type"]
        if k in request.GET
    })

    object_ = request.GET.get("object")
    if object_:
        query_parmas["object_"] = OBJECT_TYPE[object_]
    end_time = try_parse_datetime(request.GET.get("end_time"))
    if end_time:
        query_parmas["end_time"] = end_time
    start_time = try_parse_datetime(request.GET.get("start_time"), is_strat=True)
    if start_time:
        query_parmas["start_time"] = start_time

    logs = ActivityLogClient.search_log(**query_parmas).order_by("-activity_time")
    limit = request.GET.get("limit", "40")
    if limit.isdigit():
        limit = int(limit)
        limit = limit if limit > 0 else 40  # 40 items perpage

    page = request.GET.get("page", "0")
    if page.isdigit():
        page = int(page)
        page = page if page > 0 else 1
    else:
        page = 1
    index = (page - 1) * limit

    page_logs = logs[index: index + limit]
    operators = get_all_user_info(cc_biz_id, request.user.username)
    data = {
        "index": index,
        "limit": limit,
        "operators": operators.items(),
        "operator_types": dict(OPERATOR_TYPE_VALUES),
        "objects": dict(OBJECT_TYPE),
        "total": logs.count(),
        "details": [ActivityLogClient.instance_to_dict(i) for i in page_logs],
        "queries": {
            "index": index,
            "limit": limit,
            "user": request.GET.get("user"),
            "object": request.GET.get("object"),
            "format": request.GET.get("format"),
            "operator_type": request.GET.get("operator_type"),
            "content": request.GET.get("content"),
            "start_time": start_time or start_time,
            "end_time": end_time or end_time,
        }
    }
    format_ = request.GET.get("format", "html")
    if format_ == "json":
        return JsonResponse(data)
    else:
        return render_mako_context(request, 'fta_solutions/operational_audit_detail.html', data, )


def out_of_scope_trend(request, cc_biz_id):
    # 图表数据：业务按天的未接入趋势图
    filter_enddate = arrow.now().floor('day')
    filter_date = filter_enddate.replace(days=-30)

    date_counts = OutOfScopeArchive.objects.filter(
        cc_biz_id=cc_biz_id, created_on__range=[filter_date.date(), filter_enddate.date()]
    ).distinct().values('created_on').annotate(Sum('sub_count'))

    date_counts = {d['created_on']: d['sub_count__sum'] for d in date_counts}

    categories = []
    data_column1 = [_(u'单天未接入数')]
    for day in get_date_range(filter_date, filter_enddate):
        # get_date_range 函数已经处理了时区的信息
        categories.append(day.strftime('%m-%d'))
        data_column1.append(date_counts.get(day, 0))

    return HttpResponse(json.dumps({'categories': categories, 'data_column1': data_column1}))


def get_solution_count_by_day(cc_biz_id):
    """
    今日自愈次数
    """
    qs = AlarmInstanceArchive.objects.filter(cc_biz_id=cc_biz_id)

    # 只筛选当天的时间
    end_time = timezone.now().strftime("%Y-%m-%d")
    start_time = (timezone.now() + timedelta(days=-1)).strftime("%Y-%m-%d")
    qs = qs.filter(date__range=[start_time, end_time])
    solution_list = qs.values('date').annotate(Sum('sub_count'))

    count = 0
    for solution in solution_list:
        count += solution.get('sub_count__sum', 0)

    return count


def get_convergs_count_by_day(cc_biz_id):
    """
    今日收敛事件数
    """
    incident_conditions = {
        'is_visible': True,
        'cc_biz_id': cc_biz_id,
    }
    incidents_qs = Incident.objects.filter(**incident_conditions)
    # 只筛选当天的时间
    now_time = strftime_local(timezone.now(), '%Y-%m-%d')
    start_time_for_q = try_parse_datetime(now_time, is_strat=True)
    incidents_qs = incidents_qs.filter(begin_time__gte=start_time_for_q)

    incidents = {x.pk: x for x in incidents_qs}
    inc_alarms = list(IncidentAlarm.objects.filter(
        incident_id__in=incidents.keys(),
        # cc_biz_id=cc_biz_id,  # no cc_biz_id field
    ))
    inc_ids = set([ia.incident_id for ia in inc_alarms])

    # 过滤掉0个关联告警的事件（实际上不应该存在，但收敛模块异常时可能出现）
    incidents = {_id: inc for _id, inc in incidents.iteritems() if _id in inc_ids}
    incidents_count = len(incidents)
    return incidents_count


def get_advice_count(cc_biz_id):
    """
    该业务所有的健康诊断建议
    """
    fresh_advice_list = Advice.objects.filter(
        cc_biz_id=cc_biz_id, status='fresh',
        create_time__gt=timezone.now() - timedelta(days=7))
    ad_count = 0
    for _ad in fresh_advice_list:
        if _ad.advice_status == 'not_handle' or _ad.advice_status == 'failure':
            ad_count += 1
            # if (_ad.advice_fta_handle_type == 'advice' and
            #    _ad.offline_handle == 'no'):
            #     ad_count += 1
            # elif (_ad.advice_fta_handle_type == 'solution' and
            #       _ad.alarminstance and
            #       _ad.alarminstance.status == 'failure'):
            #     ad_count += 1
    return ad_count


def get_consumes_by_30day(cc_biz_id):
    """
    30天节省人工耗时
    """
    method = 'day'
    truncate_date = connection.ops.date_trunc_sql(method, 'date')
    start_time = (timezone.now() + timedelta(days=-30)).strftime("%Y-%m-%d")

    qs = AlarmInstanceArchive.objects.filter(cc_biz_id=cc_biz_id)
    qs = qs.extra({method: truncate_date})
    qs = qs.filter(date__gte=start_time, is_success=True)

    report_counts = qs.values(method).annotate(Sum('sub_profit'))
    consumed = 0
    for consume in report_counts:
        profit = consume.get('sub_profit__sum', 0) / 60.0 / 60.0
        profit = int(round(profit))
        consumed += profit

    return consumed
