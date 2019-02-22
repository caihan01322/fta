# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
在后台进行配置，然后在前台直接渲染
"""

import json
from copy import deepcopy
from datetime import timedelta

import arrow
from django.core.cache import cache
from django.db import connection
from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _

import fta_solutions_app.cache_utils as cash
import fta_std
from common.mymako import render_mako_context
from fta_utils.cc import CCBiz
from fta_utils.date_tool import get_date_range, try_parse_datetime
from .models import AlarmDef
from .models import AlarmInstance
from .models import AlarmInstanceArchive
from .models import AlarmType
from .models import Conf
from .models import KPICache

EFF_COUNT = {'ALL': 0, 'EFF': 0, 'RATIO': ''}


def data_report_v2(request, cc_biz_id):
    username = request.user.username
    end_time = timezone.now().strftime("%Y-%m-%d")
    start_time = (timezone.now() + timedelta(days=-30)).strftime("%Y-%m-%d")
    cc_biz_groups = cash._get_cc_biz_by_group(username)
    all_teams = cash._get_all_teams_covered()
    alarm_type_dict = AlarmType.get_description_mappings(cc_biz_id, is_handle_alert=True)
    solution_type_dict = dict(fta_std.SOLUTION_TYPE_CHOICES)
    for _type in fta_std.NO_DISPLAY_SOLUTION_TYPE:
        solution_type_dict.pop(_type)
    solution_type_dict['null'] = _(u'* 无处理 *')

    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    src_type_group = AlarmType.get_source_type_mappings(cc_biz_id, is_handle_alert=True)
    return render_mako_context(request, '/fta_solutions/data_report_v2.html', locals())


def data_v2_counts(request, cc_biz_id):
    data = _count_alarms_by_time(request)
    counts_option['xAxis'][0]['data'] = data['date_list']
    counts_option['series'][0]['data'] = data['success_list']
    counts_option['series'][1]['data'] = data['count_list']

    profit_option['xAxis'][0]['data'] = data['date_list']
    profit_option['series'][0]['data'] = data['consumed_list']
    profit_option['series'][1]['data'] = data['profit_list']

    return HttpResponse(json.dumps([counts_option, profit_option]))


def _count_alarms_by_time(request):
    cc_biz_id = request.GET.get('cc_biz_id', '')
    alarm_type = request.GET.get('alarm_type', '')
    solution_type = request.GET.get('solution_type', '')  # 默认全部, 'null'表示空套餐
    if solution_type == 'null':
        solution_type = None
    biz_team = request.GET.get('biz_team', '')
    source_type = request.GET.get('source_type', '')

    is_off_time = request.GET.get('is_off_time', '')
    is_off_time = True if is_off_time == '1' else False if is_off_time == '0' else ''

    default_time = timezone.now().strftime("%Y-%m-%d")
    start_time = request.GET.get('start_time') or default_time
    end_time = request.GET.get('end_time') or default_time

    try:
        start_date = try_parse_datetime(start_time, is_strat=True)
    except Exception:
        start_date = try_parse_datetime(default_time, is_strat=True)

    try:
        end_date_for_q = try_parse_datetime(end_time)
    except Exception:
        end_date_for_q = try_parse_datetime(default_time)

    cache_key = 'count_by_time&({},{},{},{},{},{},{},{})'.format(
        cc_biz_id, alarm_type, solution_type, biz_team,
        source_type, is_off_time, start_time, end_time)
    data = cache.get(cache_key)

    if not data:
        method = 'day'
        truncate_date = connection.ops.date_trunc_sql(method, 'date')
        qs = AlarmInstanceArchive.objects.all()
        if cc_biz_id:
            qs = qs.filter(cc_biz_id=cc_biz_id)
        if alarm_type:
            qs = qs.filter(alarm_type=alarm_type)
        if solution_type != '':
            qs = qs.filter(solution_type=solution_type)
        if biz_team:
            qs = qs.filter(biz_team=biz_team)
        if source_type:
            qs = qs.filter(source_type=source_type)
        if is_off_time != '':
            qs = qs.filter(is_off_time=is_off_time)

        qs = qs.extra({method: truncate_date})
        qs = qs.filter(date__range=[start_date, end_date_for_q])
        report_counts = qs.values(method).annotate(
            Sum('sub_count'), Sum('sub_profit'), Sum('sub_consumed')
        ).order_by(method)

        success_counts = qs.filter(is_success=True).values(method).annotate(Sum('sub_count')).order_by(method)

        report_dict = {}
        success_dict = {}

        if method == 'day':
            if start_date.year == end_date_for_q.year:
                time_format = "%m-%d"
            else:
                time_format = "%Y-%m-%d"
        if method == 'month':
            time_format = "%Y-%m"

        for single_date in get_date_range(start_date, end_date_for_q):
            key = single_date.strftime(time_format)
            report_dict[key] = {
                'count': 0,
                'profit': 0,
                'consumed': 0
            }
        for count in report_counts:
            report_dict[count[method].strftime(time_format)] = {
                'count': count['sub_count__sum'],
                'profit': int(round(count['sub_profit__sum'] / 60.0)),
                'consumed': int(round(count['sub_consumed__sum'] / 60.0))
            }
        for count in success_counts:
            success_dict[count[method].strftime(time_format)] = count['sub_count__sum']
        report_dict = sorted(report_dict.items())

        date_list, count_list = [], []
        success_list, profit_list, consumed_list = [], [], []

        for key, value in report_dict:
            date_list.append(key)
            count_list.append(value['count'])
            profit_list.append(value['profit'])
            consumed_list.append(value['consumed'])
            success_list.append(success_dict[key] if key in success_dict else 0)

        data = {
            'date_list': date_list,
            'count_list': count_list,
            'profit_list': profit_list,
            'consumed_list': consumed_list,
            'success_list': success_list,
        }

        cache.set(cache_key, data, 10 * 60)

    return data


def _get_biz_in_time():
    try:
        biz_in_time = json.loads(Conf.objects.get(name='BIZ_IN_TIME').value)
    except Exception:
        biz_in_time = {}
    return biz_in_time


def _get_biz_trends():
    trends_begin_date = arrow.now().floor('month').replace(months=-1).naive
    trends_kpi_list = KPICache.objects \
        .filter(date__gte=trends_begin_date, kpi_type=30).order_by('date')
    biz_trends = {}
    for kpi in trends_kpi_list:
        fta_ratio = 100 * kpi.tnm_success / kpi.tnm_total if kpi.tnm_total else 100
        biz_trends.setdefault(str(kpi.cc_biz_id), []).append(fta_ratio)
    return biz_trends


def data_alarms_by_biz(request, cc_biz_id):
    username = request.user.username
    cache_key = 'data_alarms_by_biz'
    data = cache.get(cache_key)
    if not data:
        recs = AlarmInstance.objects.raw('''
            SELECT ad.cc_biz_id as id, COUNT(*) AS count
            FROM fta_solutions_app_alarminstance AS a,
                    fta_solutions_app_alarmdef AS ad
                WHERE a.alarm_def_id=ad.id and ad.cc_biz_id = %s
                GROUP BY ad.cc_biz_id
                ORDER BY count ASC
            ''', [cc_biz_id])
        data = [[CCBiz(username, str(rec.id)).get("ApplicationName", _(u'－－未知－－'), ), rec.count] for rec in recs]
        cache.set(cache_key, data, 50 * 60)

    result = {'result': True, 'data': data}
    return HttpResponse(json.dumps(result))


def data_count_alarm_type(request, cc_biz_id=None):
    cc_biz_id = int(cc_biz_id) if cc_biz_id else cc_biz_id
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')

    cache_key = 'data_count_alarm_type({}-{}-{})'.format(cc_biz_id, start_time, end_time)
    data = cache.get(cache_key)

    if not data:
        qs = AlarmInstanceArchive.objects.all()
        if cc_biz_id:
            qs = qs.filter(cc_biz_id=cc_biz_id)
        if start_time:
            start_date = try_parse_datetime(start_time, is_strat=True)
        else:
            start_date = timezone.now() + timedelta(days=-30)
        if end_time:
            end_date_for_q = try_parse_datetime(end_time)
        else:
            end_date_for_q = timezone.now()
        qs = qs.filter(date__range=[start_date, end_date_for_q])

        data = {t: deepcopy(EFF_COUNT) for t in AlarmType.get_description_mappings(cc_biz_id).iterkeys()}
        data[''] = deepcopy(EFF_COUNT)  # 所有

        for type_count in qs.distinct().values('alarm_type').annotate(Sum('sub_count')):
            data[type_count['alarm_type']]['ALL'] = type_count['sub_count__sum']
        data['']['ALL'] = sum([v['ALL'] for v in data.itervalues()])

        for type_count in qs.filter(is_success=True).distinct().values('alarm_type').annotate(Sum('sub_count')):
            data[type_count['alarm_type']]['EFF'] = type_count['sub_count__sum']
        data['']['EFF'] = sum([v['EFF'] for v in data.itervalues()])

        # calc fta ratio
        for s_id, s_cnt in data.iteritems():
            s_cnt['RATIO'] = '' if s_cnt['ALL'] == 0 else "{:.0%}".format(float(s_cnt['EFF']) / s_cnt['ALL'])

        cache.set(cache_key, data, 10 * 60)

    result = {'result': True, 'message': data}
    return HttpResponse(json.dumps(result))


def data_count_solution_type(request, cc_biz_id=None):
    """
    根据套餐类型做统计，使用最新的AlarmInstanceArchive来做查询
    """
    cc_biz_id = int(cc_biz_id) if cc_biz_id else cc_biz_id
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')

    cache_key = 'data_count_solution_type({}-{}-{})!'.format(cc_biz_id, start_time, end_time)
    data = cache.get(cache_key)

    if not data:
        qs = AlarmInstanceArchive.objects.all()
        if cc_biz_id:
            qs = qs.filter(cc_biz_id=cc_biz_id)
        if start_time:
            start_date = try_parse_datetime(start_time, is_strat=True)
        else:
            start_date = timezone.now() + timedelta(days=-30)
        if end_time:
            end_date_for_q = try_parse_datetime(end_time)
        else:
            end_date_for_q = timezone.now()
        qs = qs.filter(date__range=[start_date, end_date_for_q])

        data = {'': deepcopy(EFF_COUNT)}  # ''代表全部类型的总计

        # 先拿总数
        for type_count in qs.distinct().values('solution_type').annotate(Sum('sub_count')):
            sol_type = type_count['solution_type']
            data[sol_type] = deepcopy(EFF_COUNT)
            data[sol_type]['ALL'] = type_count['sub_count__sum']
        data['']['ALL'] = sum([v['ALL'] for v in data.itervalues()])

        # 再拿成功数
        for type_count in qs.filter(is_success=True).distinct().values('solution_type').annotate(Sum('sub_count')):
            sol_type = type_count['solution_type']
            data[sol_type]['EFF'] = type_count['sub_count__sum']
        data['']['EFF'] = sum([v['EFF'] for v in data.itervalues()])

        # calc fta ratio
        for s_id, s_cnt in data.iteritems():
            s_cnt['RATIO'] = '' if s_cnt['ALL'] == 0 else "{:.0%}".format(float(s_cnt['EFF']) / s_cnt['ALL'])

        cache.set(cache_key, data, 10 * 60)

    result = {'result': True, 'message': data}
    return HttpResponse(json.dumps(result))


def data_count_team(request, cc_biz_id):
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')

    cache_key = 'data_count_team({}-{})!'.format(start_time, end_time)
    data = cache.get(cache_key)

    if not data:
        qs = AlarmInstanceArchive.objects.all()
        if cc_biz_id:
            qs = qs.filter(cc_biz_id=cc_biz_id)
        if start_time:
            start_date = try_parse_datetime(start_time, is_strat=True)
        else:
            start_date = timezone.now() + timedelta(days=-30)
        if end_time:
            end_date_for_q = try_parse_datetime(end_time)
        else:
            end_date_for_q = timezone.now()
        qs = qs.filter(date__range=[start_date, end_date_for_q])

        data = {'': deepcopy(EFF_COUNT)}  # ''代表全部类型的总计

        # 先拿总数
        for type_count in qs.distinct().values('biz_team').annotate(Sum('sub_count')):
            sol_type = type_count['biz_team']
            data[sol_type] = deepcopy(EFF_COUNT)
            data[sol_type]['ALL'] = type_count['sub_count__sum']
        data['']['ALL'] = sum([v['ALL'] for v in data.itervalues()])

        # 再拿成功数
        for type_count in qs.filter(is_success=True).distinct().values('biz_team').annotate(Sum('sub_count')):
            sol_type = type_count['biz_team']
            data[sol_type]['EFF'] = type_count['sub_count__sum']
        data['']['EFF'] = sum([v['EFF'] for v in data.itervalues()])

        # calc fta ratio
        for s_id, s_cnt in data.iteritems():
            s_cnt['RATIO'] = '' if s_cnt['ALL'] == 0 else "{:.0%}".format(float(s_cnt['EFF']) / s_cnt['ALL'])

        cache.set(cache_key, data, 10 * 60)

    result = {'result': True, 'message': data}
    return HttpResponse(json.dumps(result))


def data_alarms_by_time(request, cc_biz_id=None):
    cc_biz_id = int(cc_biz_id) if cc_biz_id else cc_biz_id
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')
    alarm_type = request.GET.get('alarm_type', '')
    solution_type = request.GET.get('solution_type', None)  # 'null'表示空套餐
    team = request.GET.get('team', None)

    end_date_for_q = arrow.get(end_time).ceil('day').naive
    start_date = arrow.get(start_time).naive

    method = 'day'
    time_format = "%Y-%m-%d"
    if start_date.year == end_date_for_q.year:
        time_format = "%m-%d"

    truncate_date = connection.ops.date_trunc_sql(method, 'date')
    qs = AlarmInstanceArchive.objects.all()
    if cc_biz_id:
        qs = qs.filter(cc_biz_id=cc_biz_id)
    if alarm_type:
        qs = qs.filter(alarm_type=alarm_type)
    if team:
        qs = qs.filter(biz_team=team)
    if solution_type:
        solution_type = None if solution_type == 'null' else solution_type
        qs = qs.filter(solution_type=solution_type)
    qs = qs.extra({method: truncate_date})

    qs = qs.filter(date__range=[start_date, end_date_for_q])
    report_counts = qs.values(method).annotate(
        Sum('sub_count')).order_by(method)
    success_counts = qs.filter(is_success=True).values(method).annotate(
        Sum('sub_count')).order_by(method)

    report_dict, success_dict = {}, {}
    key_list, value_list, success_list = [], [], []

    for single_date in get_date_range(start_date, end_date_for_q):
        key = single_date.strftime(time_format)
        report_dict[key] = 0

    for count in report_counts:
        report_dict[count[method].strftime(time_format)] = count['sub_count__sum']
    for count in success_counts:
        success_dict[count[method].strftime(time_format)] = count['sub_count__sum']
    report_dict = sorted(report_dict.items())

    for key, value in report_dict:
        key_list.append(key)
        value_list.append(value)
        success_list.append(success_dict[key] if key in success_dict else 0)

    data = {
        'count': sum(value_list),
        'key': key_list,
        'value': value_list,
        'success_list': success_list
    }

    result = {'result': True, 'message': data}
    return HttpResponse(json.dumps(result))


def data_failure_by_time(request, cc_biz_id=None):
    cc_biz_id = int(cc_biz_id) if cc_biz_id else cc_biz_id
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')

    end_date_for_q = arrow.get(end_time).ceil('day').naive
    start_date = arrow.get(start_time).naive

    method = 'day'
    time_format = "%Y-%m-%d"
    if start_date.year == end_date_for_q.year:
        time_format = "%m-%d"

    qs = AlarmInstanceArchive.objects.filter(is_success=False, date__range=[start_date, end_date_for_q])

    if cc_biz_id:
        qs = qs.filter(cc_biz_id=cc_biz_id)

    truncate_date = connection.ops.date_trunc_sql(method, 'date')
    qs = qs.extra({method: truncate_date})

    day_list = [d.strftime(time_format) for d in get_date_range(start_date, end_date_for_q)]

    series_list = []
    for fail_type, fail_desc in fta_std.FAILURE_TYPE_CHOICES:
        if fail_type == 'user_code_failure':
            q_counts = qs.filter(
                Q(failure_type=None) | Q(failure_type=fail_type)
            ).values(method).annotate(Sum('sub_count')).order_by(method)
        else:
            q_counts = qs.filter(failure_type=fail_type).values(method).annotate(Sum('sub_count')).order_by(method)

        val_dict = {d: 0 for d in day_list}
        val_list = []

        for cnt in q_counts:
            val_dict[cnt[method].strftime(time_format)] = cnt['sub_count__sum']

        val_dict = sorted(val_dict.items())

        for key, value in val_dict:
            val_list.append(value)
        series_list.append({
            'name': unicode(fail_desc),
            'data': val_list
        })

    data = {
        'day_list': day_list,
        'series_list': series_list,
    }
    result = {'result': True, 'message': data}
    return HttpResponse(json.dumps(result))


def data_profit_by_time(request, cc_biz_id=None):
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')
    alarm_type = request.GET.get('alarm_type', '')

    method = 'day'
    truncate_date = connection.ops.date_trunc_sql(method, 'date')
    qs = AlarmInstanceArchive.objects.filter(is_success=True)
    if cc_biz_id:
        qs = qs.filter(cc_biz_id=cc_biz_id)
    if alarm_type:
        qs = qs.filter(alarm_type=alarm_type)

    qs = qs.extra({method: truncate_date})
    end_date_for_q = try_parse_datetime(end_time)
    start_date = try_parse_datetime(start_time, is_strat=True)
    qs = qs.filter(date__range=[start_date, end_date_for_q])
    report_counts = qs.values(method).annotate(Sum('sub_profit')).order_by(method)

    report_dict = {}
    key_list, value_list = [], []
    if method == 'day':
        if start_date.year == end_date_for_q.year:
            time_format = "%m-%d"
        else:
            time_format = "%Y-%m-%d"
    if method == 'month':
        time_format = "%Y-%m"

    for single_date in get_date_range(start_date, end_date_for_q):
        key = single_date.strftime(time_format)
        report_dict[key] = 0

    for count in report_counts:
        report_dict[count[method].strftime(time_format)] = count['sub_profit__sum'] / 60 / 60

    report_dict = sorted(report_dict.items())

    for key, value in report_dict:
        key_list.append(key)
        value_list.append(value)

    count = sum(value_list)

    data = {
        'count': count,
        'key': key_list,
        'value': value_list,
    }

    result = {'result': True, 'message': data}
    return HttpResponse(json.dumps(result))


def data_status(request, cc_biz_id):
    STATUS = ['success', 'almost_success', 'failure', 'skipped', 'for_notice', 'for_reference']
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    cc_biz_id = request.GET.get('cc_biz_id')
    if start_time:
        start_date = try_parse_datetime(start_time, is_strat=True)
    else:
        start_date = timezone.now() + timedelta(days=-30)
    if end_time:
        end_date_for_q = try_parse_datetime(end_time)
    else:
        end_date_for_q = timezone.now()
    kwargs = {'source_time__range': [start_date, end_date_for_q]}
    if cc_biz_id:
        kwargs['cc_biz_id'] = cc_biz_id
    query = AlarmInstance.objects.filter(**kwargs).exclude(solution_type=None)
    all_count = query.count() / 1.0
    raw_result = {
        status: query.filter(status=status).count() / all_count
        if all_count else 0 for status in STATUS}
    success_count = raw_result.get('success', 0) + \
        raw_result.get('almost_success', 0) + \
        raw_result.get('skipped', 0) + \
        raw_result.get('for_notice', 0) + \
        raw_result.get('for_reference', 0)
    failure_count = raw_result.get('failure', 0)
    result = [
        [u'成功', success_count],
        [u'失败', failure_count],
    ]
    return HttpResponse(json.dumps({'result': True, 'data': result}))


def _get_alarm_def_count():
    '''显示已接入的业务的接入的策略的总数'''
    defs = AlarmDef.objects.filter(
        is_enabled=True, category='default'
    ).exclude(
        source_type='LEAF'
    ).values('cc_biz_id').distinct().annotate(count=Count('pk'))
    type_counts = {str(d['cc_biz_id']): d['count'] for d in defs}
    return type_counts


counts_option = {
    'title': {
        'text': _(u'自愈趋势'),
        "x": "center"
    },
    'tooltip': {
        'trigger': 'axis',
        "axisPointer": {"type": "shadow"}
    },
    'legend': {
        'y': 'bottom',
        'data': [_(u'自愈次数'), _(u'成功次数')]
    },
    'toolbox': {
        'show': False,
        'feature': {
            'dataView': {'show': True, 'readOnly': False},
            'magicType': {
                'show': True,
                'type': ['line', 'bar', 'stack', 'tiled']
            },
            'restore': {'show': True},
            'saveAsImage': {'show': True}
        },
    },
    'calculable': True,
    'xAxis': [
        {
            'type': 'category',
            'data': [_(u'周一'), _(u'周二'), _(u'周三'), _(u'周四'), _(u'周五'), _(u'周六'), _(u'周日')],
            'splitLine': {
                'show': False,
                'lineStyle': {
                    'color': '#ddd',
                    'type': 'solid',
                    'width': 1
                }
            }
        }
    ],
    # 'xAxis': {
    #     'categories': [],
    #     'labels': {
    #         'rotation': -45,
    #         'align': 'right',
    #         'style': {
    #             'fontSize': '13px',
    #             'fontFamily': 'Verdana, sans-serif'
    #         }
    #     }
    # },
    # 'yAxis': {
    #     'min' : 0,
    #     'title': {
    #         'text': '次数'
    #     },
    #     'plotLines': [{
    #         'value': 0,
    #         'width': 1,
    #         'color': '#808080'
    #     }]
    # },
    'yAxis': [
        {
            'type': 'value',
            'boundaryGap': [0, 0.1],
            'splitLine': {
                'show': True,
                'lineStyle': {
                    'color': '#ddd',
                    'type': 'solid',
                    'width': 1
                }
            }
            # 'axisLine':{
            #     'show':False
            # }
        }

    ],
    # 'plotOptions': {
    #     'areaspline': {
    #         'fillOpacity': 0.5
    #     },
    #     'line': {
    #         'dataLabels': {
    #             'enabled': True,
    #             'style': {
    #                 'textShadow': '0 0 3px white, 0 0 3px white'
    #             }
    #         }
    #     },
    # },
    'series': [
        {
            'name': _(u'成功次数'),
            'type': 'bar',
            'stack': 'normal',
            'smooth': True,
            'itemStyle': {
                'normal': {
                    'color': '#5b9bd5',
                    'areaStyle': {
                        'type': 'default'
                    }
                }
            },
            'data': [30, 182, 434, 791, 390, 30, 10]
        },
        {
            'name': _(u'自愈次数'),
            'type': 'bar',
            'stack': 'normal',
            'smooth': True,
            'itemStyle': {
                'normal': {
                    'areaStyle': {
                        'type': 'default'
                    }
                }
            },
            'data': [10, 12, 21, 54, 260, 830, 710]
        }
    ]
    # 'series': [{
    #     'name': '自愈次数',
    #     'data': [],
    #     'lineWidth': 3,
    # }, {
    #     'name': '成功次数',
    #     'data': [],
    #     'color': '#8bbc21',
    #     'lineWidth': 0.1,
    # }]
}

profit_option = {
    "title": {
        "text": _(u"收益时间"), "x": "center"
    },
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {
            "type": "shadow"
        },
        "formatter": None
    },
    "legend": {
        "y": "bottom",
        "data": [_(u"自愈耗时（分钟）"), _(u"节省人工时间（分钟）")]
    },
    "toolbox": {
        "show": False,
        "feature": {
            "dataView": {
                "show": True,
                "readOnly": False
            },
            "restore": {
                "show": True
            },
            "saveAsImage": {
                "show": True
            }
        }
    },
    "calculable": True,
    "xAxis": [
        {
            "type": "category",
            "data": [
                "Cosco",
                "CMA",
                "APL",
                "OOCL",
                "Wanhai",
                "Zim"
            ],
            "splitLine": {
                "show": False,
                "lineStyle": {
                    "color": "#ddd",
                    "type": "solid",
                    "width": 1
                }
            }
        }
    ],
    "yAxis": [
        {
            "type": "value",
            "boundaryGap": [0, 0.1],
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": "#ddd",
                    "type": "solid",
                    "width": 1
                }
            }
        }
    ],
    "series": [
        {
            "name": _(u"自愈耗时（分钟）"),
            "type": "bar",
            "stack": "sum",
            "itemStyle": {
                "normal": {
                    "color": "lightgreen",
                    "barBorderWidth": 0,
                    "barBorderRadius": 0,
                    "label": {
                        "show": False,
                        "position": "insideTop",
                        "formatter": None,
                        "textStyle": {
                            "color": "purple"
                        }
                    }
                }
            },
            "data": [40, 80, 50, 80, 80, 70]
        },
        {
            "name": _(u"节省人工时间（分钟）"),
            "type": "bar",
            "stack": "sum",
            "itemStyle": {
                "normal": {
                    "color": "#87cefa",
                    "barBorderWidth": 0,
                    "barBorderRadius": 0,
                    "label": {
                        "show": False,
                        "position": "insideTop",
                        "textStyle": {
                            "color": "skyblue"
                        }
                    }
                }
            },
            "data": [260, 200, 220, 120, 100, 80]
        }

    ]
}
