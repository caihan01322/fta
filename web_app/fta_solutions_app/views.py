# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import copy
import json
import md5
import re
from collections import OrderedDict
from collections import defaultdict
from datetime import timedelta

import arrow
# from django.db import router, transaction
from django.db.transaction import atomic
from django.db.models import Q, Count
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseNotAllowed,
                         HttpResponseBadRequest,
                         JsonResponse)
from django.views.decorators.http import require_POST
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy
from django.utils import timezone

from common.log import logger
from common.mymako import render_mako_context
from common.utils import render_ajax
from fta_solutions_app.forms import AlarmInstFilterForm
from fta_solutions_app.models import (
    AlarmDef, Solution, AlarmInstance, AlarmInstanceLog,
    IncidentDef, IncidentAlarm, Incident, UserAction,
    Advice, AdviceDef, BizConf, Context,
    AlarmType, AlarmApplication,
)
from fta_solutions_app import cache_utils as cash
from fta_solutions_app import fta_std
from fta_utils import fsm_client
from fta_utils.cc import CCBiz
from fta_utils.date_tool import try_parse_datetime
from fta_solutions_app.cache_utils import (get_user_biz)
import settings

from permission.models import UserBusiness
from project.permission.utils import prepare_user_business, _get_user_info
from project.conf.user import get_short_name
from permission import exceptions, utils


def base(request, cc_biz_id=None):
    """
    故障自愈 APP 的 base 框架
    """
    username = request.user.username
    include_url = request.GET.get("include", '')
    is_refresh = request.GET.get('is_refresh', '0')
    try:
        if is_refresh == '1':
            biz_list = prepare_user_business(request, use_cache=False)
        else:
            # 企业版，任何情况都不实用缓存，use_cache 的默认值都为False
            biz_list = prepare_user_business(request)
    except exceptions.Unauthorized:
        return HttpResponse(status=406)
    biz_cc_id_list = [item.cc_id for item in biz_list]

    # 用户已指定业务id，则到具体的业务页面
    if cc_biz_id:
        logo = ''
        cc_biz_names = {unicode(biz.cc_id): unicode(biz.cc_name) for biz in biz_list}
        user_actions = UserAction.objects.filter(username=username, is_guide=True).count()
        if not user_actions:
            is_show_guide = True
            UserAction.objects.create(username=username, is_guide=True)
        else:
            is_show_guide = False
        # 更新用户的默认业务信息
        user, _c = UserBusiness.objects.update_or_create(user=username, defaults={'default_buss': cc_biz_id})
        return render_mako_context(request, '/base.html', locals())

    # 未查询到用户的业务信息，则到提示业务，提示用户去 cc 创建业务
    if not biz_list:
        # 查询用户的开发商信息
        company_info = _get_user_info(request)
        context = {
            "OwenerName": company_info.get('company_name') or _(u'蓝鲸'),
            "OwenerUin": company_info.get('company_code') or _(u'BK助手'),
        }
        return render_mako_context(request, '/fta_solutions/%s' % settings.NO_BIZ_HTML_NAME, context)

    # 查询用户是否已有选定的默认业务，有则跳转到默认业务
    try:
        obj = UserBusiness.objects.get(user=username)
        biz_cc_id = obj.default_buss
        if biz_cc_id not in biz_cc_id_list:
            biz_cc_id = biz_cc_id_list[0]
            obj.default_buss = biz_cc_id
            obj.save()
    except Exception:
        biz_cc_id = biz_list[0].cc_id
        UserBusiness.objects.create(user=username, default_buss=biz_cc_id)
    return HttpResponseRedirect('%s%s/?include=%s' % (settings.SITE_URL, biz_cc_id, include_url))


def show_trip(request, cc_biz_id):
    """
    自愈之旅
    接入一个自愈的快捷套餐 （接入自愈页面）
    完成一个自愈套餐的执行 (自愈详情页面)
    创建一个自愈套餐      （创建套餐页面）
    创建一个收敛规则       （告警收敛页面）
    创建一个对接作业平台的套餐 （创建作业平台套餐页面）
    """
    is_alarm_def = AlarmDef.objects.filter(cc_biz_id=cc_biz_id).count()
    is_solution = Solution.objects.filter(cc_biz_id=cc_biz_id).count()
    is_incident_def = IncidentDef.objects.filter(cc_biz_id=cc_biz_id).count()
    is_job_solution = Solution.objects.filter(cc_biz_id=cc_biz_id, solution_type='ijobs').count()
    is_alarm_instance = AlarmInstance.objects.exclude(
        solution_type=None
    ).exclude(solution_type__in=['collect', 'sleep']).filter(cc_biz_id=cc_biz_id).count()
    context = {
        'is_alarm_def': is_alarm_def,
        'is_solution': is_solution,
        'is_incident_def': is_incident_def,
        'is_job_solution': is_job_solution,
        'is_alarm_instance': is_alarm_instance,
        'cc_biz_id': cc_biz_id
    }
    return render_mako_context(request, '/fta_solutions/trip.part', context)


def alarm_def_list(request, cc_biz_id):
    """
    告警定义列表界面
    """
    alarm_type_dict = AlarmType.get_description_mappings(cc_biz_id)
    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    available_source_types = set(i.source_type for i in AlarmApplication.get_by_cc_biz_id(cc_biz_id))
    # 添加默认告警类型
    available_source_types = available_source_types.union(set(settings.DEFAULT_OPEN_SOURCE_TYPE))
    alarm_list = AlarmDef.objects.filter(cc_biz_id__in=[0, cc_biz_id], )

    biz_resp = {"id": 0}
    try:
        conf = BizConf.objects.get(cc_biz_id=cc_biz_id)
        biz_resp['id'] = conf.id
        biz_resp['responsible'] = conf.responsible if conf.responsible else ''
    except BizConf.DoesNotExist:
        pass
    if not biz_resp.get('responsible', ''):
        username = request.user.username
        biz_resp['responsible'] = CCBiz(username, cc_biz_id).get("Maintainers")

    return render_mako_context(request, '/fta_solutions/alarm_def_list.html', locals())


def block_incident_def(request, cc_biz_id):
    """
    屏蔽收敛规则
    """
    if request.method != 'POST':
        raise HttpResponseNotAllowed
    try:
        with atomic():
            incident_def = IncidentDef.objects.get(id=request.POST['id'], cc_biz_id=0, )
            block_list = (incident_def.exclude or '').split(',')
            if cc_biz_id in block_list:
                block_list.remove(cc_biz_id)
            else:
                block_list.append(cc_biz_id)
            incident_def.exclude = ','.join(block_list)
            incident_def.save()
    except Exception, e:
        return HttpResponse(json.dumps({'success': False, 'message': str(e)}))
    return HttpResponse(json.dumps({'success': True}))


def del_incident_def(request, cc_biz_id):
    """
    删除收敛规则
    """
    if request.method != 'POST':
        raise HttpResponseNotAllowed
    try:
        IncidentDef.objects.filter(id=request.POST['id'], cc_biz_id=cc_biz_id, ).delete()
    except Exception, e:
        return HttpResponse(json.dumps({'success': False, 'message': str(e)}))
    return HttpResponse(json.dumps({'success': True}))


@require_POST
def add_incident_def(request, cc_biz_id):
    """
    添加收敛规则
    """
    # 添加用户输入验证
    post_data = dict(request.POST)

    alarm_type = post_data.get('alarm_type')
    if not alarm_type:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写告警类型")}))

    conditions = post_data.get('condition', [])
    if not conditions:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写收敛纬度")}))

    timedelta = request.POST['timedelta']
    if not timedelta:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写收敛时间")}))

    try:
        timedelta = int(timedelta)
    except Exception:
        timedelta = -1
    if timedelta < 1 or timedelta > 999999999:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"收敛时间请填写 1 到 999999999 的整数")}))

    count = request.POST.get('count')
    if not count:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写收敛条数")}))
    try:
        count = int(count)
    except Exception:
        count = -1
    if count < 1 or count > 999999999:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"收敛条数请填写 1 到 999999999 的整数")}))

    incident = request.POST.get('incident')
    if not incident:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写收敛条处理方式")}))
    # 判断用户输入是否异常
    if incident not in fta_std.INCIDENT_CHN.keys():
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写收敛方式")}))

    description = request.POST.get('description')
    if not description:
        return HttpResponse(json.dumps({'success': False, 'message': _(u"请填写备注")}))

    condition = {}
    for c in conditions:
        k, v = c.split(':')
        condition.setdefault(k, []).append(v)
    if "alarm_type" not in condition and request.POST.get("auto_alarm_type") == '1':
        condition["alarm_type"] = alarm_type
    rule = {
        "alarm_type": alarm_type,
        "timedelta": timedelta,
        "count": count,
        "incident": incident,
        "condition": condition
    }

    try:
        key = md5.new()
        key.update(json.dumps(rule))
        if request.POST.get('id'):
            incident_def = IncidentDef.objects.get(id=request.POST['id'], cc_biz_id=cc_biz_id, )
        else:
            incident_def = IncidentDef()
        incident_def.is_enabled = True
        incident_def.cc_biz_id = cc_biz_id
        incident_def.codename = key.hexdigest()
        incident_def.rule = json.dumps(rule)
        incident_def.description = description
        incident_def.save()
    except Exception, e:
        return HttpResponse(
            json.dumps({'success': False, 'message': unicode(e)}))
    return HttpResponse(json.dumps({'success': True}))


def incident_def_list(request, cc_biz_id):
    """
    收敛规则列表
    """
    DIMENSION_CHN = fta_std.DIMENSION_CHN
    INCIDENT_CHN = fta_std.INCIDENT_CHN
    ALARM_TYPE_CHN = AlarmType.get_description_mappings(cc_biz_id)
    all_alarm_type_total = len([
        i for i in
        AlarmType.objects.all().filter(cc_biz_id__in=[cc_biz_id, 0], is_enabled=True, )
        if cc_biz_id not in i.exclude.split(",")
    ])
    # HOST_ALARM_TYPE.remove('online')
    # HOST_ALARM_TYPE.remove('leaf-biz-watchman')

    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    src_type_group = AlarmType.get_source_type_mappings(cc_biz_id, is_handle_alert=True)

    def _get_alarm_type_group_chn(alarm_type_list):
        if list(set(alarm_type_list)) == all_alarm_type_total:
            return [u"所有"]
        return alarm_type_list

    get_alarm_type_group = _get_alarm_type_group_chn
    inc_def_list = IncidentDef.objects.filter(cc_biz_id__in=(cc_biz_id, 0), is_enabled=True).order_by('priority')
    current_rule = {}
    current_id = request.GET.get('id')
    if current_id:
        current_incident = IncidentDef.objects.get(id=current_id, cc_biz_id=cc_biz_id, )
        current_rule = json.loads(current_incident.rule)
    return render_mako_context(request, '/fta_solutions/incident_def_list.html', locals())


def advice_list(request, cc_biz_id):
    """
    自愈健康度报告
    """
    advice_type = request.GET.get('type', 'fresh')
    fresh_advice_list = Advice.objects.filter(cc_biz_id=cc_biz_id, status='fresh').order_by('-alarm_num')
    followup_advice_list = Advice.objects.filter(cc_biz_id=cc_biz_id, status='followup').order_by('-alarm_num')
    finish_advice_list = Advice.objects.filter(cc_biz_id=cc_biz_id, status='finish').order_by('-alarm_num')

    fresh_advice_dict = defaultdict(list)
    followup_advice_dict = defaultdict(list)
    finish_advice_dict = defaultdict(list)
    for myadvice in fresh_advice_list:
        alarm_type = myadvice.advice_def.check_sub_type
        fresh_advice_dict[alarm_type].append(myadvice)
    for myadvice in followup_advice_list:
        alarm_type = myadvice.advice_def.check_sub_type
        followup_advice_dict[alarm_type].append(myadvice)
    for myadvice in finish_advice_list:
        alarm_type = myadvice.advice_def.check_sub_type
        finish_advice_dict[alarm_type].append(myadvice)

    advice_type_dict = dict(AdviceDef.ADVICE_TYPE_CHOICES)
    subject_type_dict = dict(AdviceDef.SUBJECT_TYPE_CHOICES)

    username = request.user.username
    cc_biz_name = CCBiz(username, str(cc_biz_id)).get("ApplicationName", u"*未知(id:{})*".format(cc_biz_id))

    count_fresh = Advice.objects.filter(cc_biz_id=cc_biz_id, status='fresh').count()
    count_followup = Advice.objects.filter(cc_biz_id=cc_biz_id, status='followup').count()
    count_finish = Advice.objects.filter(cc_biz_id=cc_biz_id, status='finish').count()
    return render_mako_context(request, '/fta_solutions/advice_list.html', locals())


def health(request, cc_biz_id):
    """
    自愈健康度
    """
    end_date = timezone.now().strftime("%Y-%m-%d")
    begin_date = (timezone.now() - timedelta(days=6)).strftime("%Y-%m-%d")
    advice_status = Advice.ADVICE_SHOW_STATUS

    context = {
        'cc_biz_id': cc_biz_id,
        'begin_date': begin_date,
        'end_date': end_date,
        'advice_status': advice_status,
    }
    return render_mako_context(request, '/fta_solutions/health.html', context)


def health_detail(request, cc_biz_id):
    """建议详情
    """
    begin_date = request.GET.get('begin_date')
    end_date = request.GET.get('end_date')
    ip = request.GET.get('ip').strip()
    advice_status = request.GET.get('advice_status')
    filtered = False

    # 查询时间条件
    begin_date = try_parse_datetime(begin_date, is_strat=True)
    end_date = try_parse_datetime(end_date)

    _fresh_advice_list = Advice.objects.filter(cc_biz_id=cc_biz_id, status='fresh').order_by('-create_time')

    if ip:
        _fresh_advice_list = _fresh_advice_list.filter(subject__icontains=ip, )
        filtered = True
    if begin_date:
        _fresh_advice_list = _fresh_advice_list.filter(create_time__gte=begin_date, )
    if end_date:
        _fresh_advice_list = _fresh_advice_list.filter(create_time__lte=end_date, )
    total_count = _fresh_advice_list.count()

    fresh_advice_list = []
    success_count = 0
    failure_count = 0
    not_handle_count = 0
    for _ad in _fresh_advice_list:
        # 未处理
        if _ad.advice_status == 'not_handle':
            not_handle_count += 1
            if advice_status == 'not_handle':
                fresh_advice_list.append(_ad)
        # 失败
        elif _ad.advice_status == 'failure':
            failure_count += 1
            if advice_status == 'failure':
                fresh_advice_list.append(_ad)
        # 成功
        elif _ad.advice_status == 'success':
            success_count += 1
            if advice_status == 'success':
                fresh_advice_list.append(_ad)
    # 不按状态查询
    if not advice_status:
        fresh_advice_list = _fresh_advice_list
    count_fresh = len(fresh_advice_list)

    # 只处理 fresh 分类的套餐
    advice_type = request.GET.get('type', 'fresh')

    advice_type_dict = dict(AdviceDef.ADVICE_TYPE_CHOICES)
    subject_type_dict = dict(AdviceDef.SUBJECT_TYPE_CHOICES)

    ip_list = [a.subject for a in fresh_advice_list if a.advice_def.subject_type == 'host']
    # ip 去重
    ip_list = set(ip_list)
    for a in fresh_advice_list:
        a.frequency = float(a.alarm_num) / a.advice_def.interval
        a.level = "critical" if a.alarm_num > 60 or a.frequency >= 3 else "normal"
        if a.advice_def.interval == 30:
            a.interval_desc = _(u"一个月")
        elif a.advice_def.interval == 7:
            a.interval_desc = _(u"一个星期")
        elif a.advice_def.interval == 1:
            a.interval_desc = _(u"一天内")
        else:
            a.interval_desc = _(u"{}天内").format(a.advice_def.interval)
    status_dict = dict(fta_std.STATUS_CHOICES)
    return render_mako_context(request, '/fta_solutions/health_detail.part', locals())


def handle_advice(request, cc_biz_id, advice_id):
    """线下处理
    """
    try:
        Advice.objects.filter(cc_biz_id=cc_biz_id, id=advice_id).update(
            offline_handle='ok',
            offline_time=timezone.now(),
            offline_user=get_short_name(request.user.username)
        )
        result = {'result': True, 'message': _(u"标记成功")}
        return HttpResponse(json.dumps(result))
    except Exception:
        logger.exception(u"handle_advice[advice_id:%s]error" % advice_id)
        result = {'result': False, 'message': _(u"标记失败")}
        return HttpResponse(json.dumps(result))


def show_offline_advice(request, cc_biz_id, advice_id):
    """线下处理详情
    """
    try:
        advice = Advice.objects.get(cc_biz_id=cc_biz_id, id=advice_id)
    except Exception:
        advice = None
        logger.exception(u"show_offline_advice[advice_id:%s]error" % advice_id)
    return render_mako_context(request, 'fta_solutions/health_offline_advice.html', {'advice': advice})


def solution_list(request, cc_biz_id):
    """
    套餐列表
    """
    solution_list = Solution.objects.filter(cc_biz_id=cc_biz_id, ).order_by('-id')

    solution_types = dict(fta_std.SOLUTION_TYPE_CHOICES)
    now = timezone.now()
    last_week = now - timedelta(days=7)

    date_range = '%s to %s' % (last_week.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d'))
    my_biz = get_user_biz(request.user.username)

    # 查询每个套餐会被多少使用
    alarm_def_count_list = AlarmDef.objects.filter(
        cc_biz_id=cc_biz_id
    ).exclude(solution_id=None).values("solution_id").annotate(Count("solution_id"))
    alarm_def_count_dict = {}
    for a in alarm_def_count_list:
        alarm_def_count_dict[a["solution_id"]] = a["solution_id__count"]
    return render_mako_context(request, '/fta_solutions/solution_list.html', locals())


# def preference(request):
#     """
#     个人偏好界面
#     """
#     return render_mako_context(request, '/fta_solutions/preference.html')


# def intro(request):
#     """
#     引导界面
#     """
#     return render_mako_context(request, '/fta_solutions/intro.html')


def alarm_def(request, cc_biz_id, alarm_def_id):
    """
    接入详情页
    'GSE': ALARM_TYPE_GSE_CHOICES,
    'INC': ALARM_TYPE_TITAN_CHOICES,
    """
    username = request.user.username

    alarm_type_dict = AlarmType.get_description_mappings(cc_biz_id)
    # ？为何不能拷贝 登录 的告警
    alarm_type_dict = {k: v for k, v in alarm_type_dict.iteritems() if k != 'online'}

    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    src_type_group = AlarmType.get_source_type_mappings(cc_biz_id, is_handle_alert=True)

    if alarm_def_id == 'add':
        edit = False
        alarm_def = None
        responsible_list = []
    else:
        edit = True
        alarm_def = AlarmDef.objects.get(Q(cc_biz_id=cc_biz_id) | Q(cc_biz_id=0), id=alarm_def_id)
        responsible_list = alarm_def.responsible.split(';') if alarm_def.responsible else []

    # 业务SET属性 -> 业务SET之间的对应关系
    set_attr_to_topo_set_dict = []
    # 业务SET -> 业务模块之间的对应关系
    topo_set_to_module_dict = cash.get_app_topo_set_to_module_dict(cc_biz_id, username)

    # 业务下的 SET 列表
    app_sets = cash._get_app_topo_set_with_cache(cc_biz_id, username)
    # 业务下的模块列表
    app_modules = cash._get_app_module_with_cache(cc_biz_id, username)
    # 业务的自定义告警特性
    biz_attr_list = []

    # 业务运维
    maintainers = cash.get_biz_responsible(cc_biz_id, username)
    #  开发商下所有用户
    all_user_info = cash.get_all_user_info(cc_biz_id, username)

    solution_list = Solution.objects.filter(cc_biz_id__in=[cc_biz_id, 0], ).order_by('cc_biz_id', 'title')
    return render_mako_context(request, '/fta_solutions/alarm_def.html', dict(
        cc_biz_id=cc_biz_id,
        alarm_def_id=alarm_def_id,
        edit=edit,
        alarm_def=alarm_def,
        app_modules=app_modules,
        app_sets=app_sets,
        set_attr_to_topo_set_dict=set_attr_to_topo_set_dict,
        topo_set_to_module_dict=topo_set_to_module_dict,

        alarm_type_dict=alarm_type_dict,
        src_type_group=src_type_group,
        biz_attr_list=biz_attr_list,
        solution_list=solution_list,
        source_type_dict=source_type_dict,

        maintainers=maintainers,
        all_user_info=all_user_info,
        responsible_list=responsible_list,
    ))


def check_solution_title(request, cc_biz_id, solution_id):
    """
    同一个业务下的套餐名不能重复
    """
    solution_title = request.GET.get('title')
    _is_check, _msg = Solution.check_title(cc_biz_id, solution_title, solution_id)
    result = {'result': _is_check, 'message': _msg}
    return HttpResponse(json.dumps(result))


def solution(request, cc_biz_id, solution_id):
    """
    套餐详情页
    """
    type_to_show = request.GET.get('type_to_show', None)  # 展示的套餐类型

    solutions = {str(s.id): s.title for s in Solution.objects.filter(cc_biz_id__in=["0", cc_biz_id])}
    solutions_list = sorted(solutions.items(), key=lambda x: x[1])

    if solution_id == 'add':
        edit = False
        if not type_to_show:
            type_to_show = 'clean'  # 默认的套餐类型
    else:
        edit = True
        try:
            solution = Solution.objects.get(id=solution_id, cc_biz_id=cc_biz_id)
        except Exception:
            # 套餐不存在则显示新建页面
            edit = False
            type_to_show = 'clean'
        else:
            solution.config = json.loads(solution.config or '{}')

            if type_to_show:
                solution.codename = ''
                solution.config = {}
            else:
                type_to_show = solution.solution_type
                if solution.solution_type == 'bk_component':
                    if solution.config['module_name'] == "bk.tcm":
                        if solution.config['task_name'] == "start_task_with_fixedname":
                            type_to_show = 'tcm'
                    if solution.config['module_name'] == "bk.gcs":
                        if solution.config['task_name'] == "privileges_clone_client":
                            type_to_show = 'gcs_clone'
                    if solution.config['module_name'] == "bk.webplat":
                        if solution.config['task_name'] == "game_area_update":
                            type_to_show = 'webplat_update'
                if solution.solution_type == 'graph':
                    sol_list = []
                    graph = json.loads(solution.config['real_solutions'])
                    for idx, sol in enumerate(graph):
                        temp = copy.deepcopy(sol)
                        text = '#%s [%s] %s' % (idx, temp[1], solutions[str(temp[1])])
                        temp.append(text)
                        sol_list.append(temp)
                    sol_list = json.dumps(sol_list)
    # 一些不想在界面上展示的套餐类型，在这里 pop
    # solution_types = OrderedDict(fta_std.SOLUTION_TYPE_CHOICES)
    # for _type in fta_std.NO_DISPLAY_SOLUTION_TYPE:
    #     solution_types.pop(_type)
    # 套餐分类
    solution_types = fta_std.SOLUTION_TYPE_GROPS
    my_biz = get_user_biz(request.user.username)
    return render_mako_context(request, '/fta_solutions/solution.html', locals())


def solution_form(request, cc_biz_id, solution_type_or_id):
    """
    套餐表单
    """
    solution_type = solution_type_or_id
    # 若为类型，即为加载新建界面，否则为加载一条已存的记录
    if solution_type_or_id not in dict(fta_std.SOLUTION_TYPE_CHOICES):
        solution = Solution.objects.get(id=solution_type_or_id, cc_biz_id=cc_biz_id)
        solution_type = solution.solution_type
        solution.config = json.loads(solution.config or '{}')

    return render_mako_context(
        request,
        '/fta_solutions/solution_forms/{}.html'.format(solution_type),
        locals())


def _solution_copy(username, solution, cc_biz_id):
    """
    拷贝套餐
    """
    error = ""
    solution_config = json.loads(solution.config or '{}')
    if solution_config.get('task_name') == 'start_task_with_fixedname':
        # TCM套餐清除参数
        solution_config = {
            "module_name": solution_config.get("module_name"),
            "task_name": solution_config.get("task_name"),
            "task_kwargs": "{}",
        }
        solution.config = json.dumps(solution_config)
        error = "TCM套餐(%s)需要重新配置" % solution.title_display
    try:
        if solution_config.get("task_name") != "start_task_with_fixedname":
            same_solution = Solution.objects.filter(
                cc_biz_id=cc_biz_id,
                solution_type=solution.solution_type,
                codename=solution.codename,
                config=solution.config)
        # TCM套餐参数被清除，所以根据名字过滤
        else:
            same_solution = Solution.objects.filter(
                cc_biz_id=cc_biz_id,
                solution_type=solution.solution_type,
                codename=solution.codename,
                config=solution.config,
                title=_(u'%s【拷贝】') % solution.title)
        if same_solution:
            new_solution = same_solution[0]
            error_data = _(u"跳过已存在相同的套餐:%s") % (solution.title_display)
            return {"success": False, "id": new_solution.id, "message": error_data}
        else:
            new_solution = Solution(
                creator=username,
                title=_(u'%s【拷贝】') % solution.title,
                cc_biz_id=cc_biz_id,
                solution_type=solution.solution_type,
                codename=solution.codename,
                config=solution.config)
        new_solution.save()
    except Exception, e:
        error = str(e)
    if error:
        return {"success": False, "id": new_solution.id, "message": error}
    return {"success": True, "id": new_solution.id}


def solution_copy(request, cc_biz_id):
    """
    拷贝套餐
    """
    solution_id = request.POST.get('solution_id')
    to_cc_biz_id = request.POST.get('cc_biz_id')
    try:
        utils.get_business_obj(request, to_cc_biz_id)
    except Exception:
        return JsonResponse({"success": False, "message": _(u"无权限")})
    solution = Solution.objects.get(id=solution_id, cc_biz_id__in=[cc_biz_id, 0], )
    solution_config = json.loads(solution.config or '{}')
    errors = []
    copyed_solution_id = []
    if solution.solution_type == 'diy':
        # 组合套餐拷贝所有子套餐
        real_solutions = json.loads(solution_config['real_solutions'])
        for pos, solution_id in real_solutions.items():
            child_solution = Solution.objects.get(id=solution_id, cc_biz_id__in=[cc_biz_id, 0], )

            # 不拷贝官方通用套餐
            if child_solution.cc_biz_id == 0:
                continue

            result = _solution_copy(request.user.username, child_solution, to_cc_biz_id)
            real_solutions[pos] = result['id']
            if not result["id"] in copyed_solution_id and not result['success']:
                errors.append(result['message'])
            copyed_solution_id.append(result["id"])
        solution_config['real_solutions'] = json.dumps(real_solutions)
        solution.config = json.dumps(solution_config)
    if solution.solution_type == 'graph':
        # 组合套餐拷贝所有子套餐
        real_solutions = json.loads(solution_config['real_solutions'])
        for pos, node in enumerate(real_solutions):
            solution_id = node[1]
            child_solution = Solution.objects.get(id=solution_id, cc_biz_id__in=[cc_biz_id, 0], )

            # 不拷贝官方通用套餐
            if child_solution.cc_biz_id == 0:
                continue

            result = _solution_copy(request.user.username, child_solution, to_cc_biz_id)
            real_solutions[pos][1] = result['id']
            if not result["id"] in copyed_solution_id and not result['success']:
                errors.append(result['message'])
            copyed_solution_id.append(result["id"])
        solution_config['real_solutions'] = json.dumps(real_solutions)
        solution.config = json.dumps(solution_config)
    result = _solution_copy(request.user.username, solution, to_cc_biz_id)
    if not result['success']:
        errors.append(result['message'])
    if errors:
        errors = list(set(errors))
        return HttpResponse(json.dumps({'success': False, 'message': '\n'.join(errors)}))
    return HttpResponse(json.dumps({'success': True}))


def alarm_def_copy(request, cc_biz_id):
    """
    拷贝接入
    """
    alarm_type = request.POST.get('alarm_type')
    source_type = request.POST.get('source_type')
    alarm_def_id = request.POST.get('alarm_def_id')
    alarm_def = AlarmDef.objects.get(id=alarm_def_id, cc_biz_id=cc_biz_id)

    try:
        alarm_def.pk = None  # use this to directly clone
        alarm_def.alarm_type = alarm_type
        alarm_def.source_type = source_type
        alarm_def.description = _(u'%s【拷贝】') % alarm_def.description
        alarm_def.save()
    except Exception, e:
        return HttpResponse(json.dumps({"success": False, "message": e}))
    return HttpResponse(json.dumps({"success": True, "new_id": alarm_def.id}))


def graph_copy(request, cc_biz_id):
    try:
        solution_id = request.REQUEST.get("id")
        solution = Solution.objects.get(id=solution_id, cc_biz_id__in=[cc_biz_id, 0], )
        if solution.solution_type == "diy":
            graph_json = fsm_client.convert_solution2graph(solution)
            new_solution = Solution.objects.create(
                config=json.dumps({"real_solutions": json.dumps(graph_json)}),
                cc_biz_id=cc_biz_id,
                creator=request.user.username,
                solution_type="graph",
                title=solution.title + _(u"新版"),
            )
            return HttpResponse(json.dumps({"success": True, "new_id": new_solution.id}))
        return HttpResponse(json.dumps({"success": False, "message": _(u"创建失败: %s") % "solution_type is not diy"}))
    except Exception, e:
        logger.error(e)
        return HttpResponse(json.dumps({"success": False, "message": _(u"创建失败: %s") % e}))


class AlarmInstanceListView(View):
    ALARM_INST_CONDITIONS_MAP = {
        'alarm_type': 'alarm_type',
        'date': 'source_time__range',
        'cc_topo_set': 'cc_topo_set',
        'cc_app_module': 'cc_app_module',
        'status': 'status',
        'ip': 'ip__icontains',
    }
    INCIDENT_CONDITIONS_MAP = {
        'date': 'begin_time__range',
    }
    SOLUTION_TYPES = dict(fta_std.SOLUTION_TYPE_CHOICES)
    STATUS_DICT = OrderedDict(fta_std.STATUS_CHOICES)
    STATUS_COLOR_DICT = dict(fta_std.STATUS_COLOR)
    ALL_INC = '*ALL_INC*'
    INC_TYPE_DICT = OrderedDict(
        {
            ALL_INC: _lazy(u"* 所有收敛"),
            "collect_alarm": _lazy(u"汇总通知"),
        },
        **dict(fta_std.INCIDENT_CHN)
    )

    fanyi_str = _(u"* 所有收敛")

    def __init__(self, *args, **kwargs):
        super(AlarmInstanceListView, self).__init__(*args, **kwargs)
        self.view_model = {}
        self.cc_biz_id = None
        self.username = None

    def get_alarm_conditions(self, alarm_inst_conditions=None, with_form_filter=True, ):
        cleaned_data = self.form.cleaned_data
        conditions = {}
        if with_form_filter:
            conditions = {
                f: cleaned_data[k]
                for k, f in self.ALARM_INST_CONDITIONS_MAP.items()
                if cleaned_data.get(k)
            }
        if alarm_inst_conditions:
            conditions.update(alarm_inst_conditions)

        return conditions

    def get_important_alarm_query(self, alarm_inst_conditions=None, with_form_filter=True, ):
        cleaned_data = self.form.cleaned_data
        alarm_inst_conditions = self.get_alarm_conditions(alarm_inst_conditions, with_form_filter, )
        alarm_type = cleaned_data["alarm_type"]

        # 如果是过滤事件，进行特殊处理
        if alarm_type in self.INC_TYPE_DICT:
            alarm_inst_conditions.pop("alarm_type", None)

        return AlarmInstance.objects.filter(
            cc_biz_id=self.cc_biz_id,
        ).exclude(
            solution_type=None,
        ).exclude(
            source_type="FTA",
        ).filter(**alarm_inst_conditions).order_by('-id')

    def get_incident_query(self, incident_conditions=None):
        cleaned_data = self.form.cleaned_data
        incident_conditions = incident_conditions or {
            f: cleaned_data[k]
            for k, f in self.INCIDENT_CONDITIONS_MAP.items()
            if cleaned_data[k]
        }
        alarm_type = cleaned_data["alarm_type"]
        # 如果是过滤事件，进行特殊处理
        if alarm_type and alarm_type in self.INC_TYPE_DICT:
            if alarm_type != self.ALL_INC:
                incident_conditions["incident_type"] = alarm_type

        return Incident.objects.filter(
            cc_biz_id=self.cc_biz_id,
            is_visible=True,
        ).filter(**incident_conditions).order_by('-begin_time')

    def get_unimportant_alarm_query(self, alarm_inst_conditions=None):
        alarm_inst_conditions = self.get_alarm_conditions(alarm_inst_conditions)
        alarm_inst_conditions = alarm_inst_conditions or {}
        return AlarmInstance.objects.filter(
            source_type="FTA",
            cc_biz_id=self.cc_biz_id,
        ).filter(**alarm_inst_conditions).order_by("-id")

    def export_ip_handler(self, alarm_inst_conditions=None):
        alarm_instance_qs = self.get_important_alarm_query(
            alarm_inst_conditions,
        )
        ip_list = alarm_instance_qs.values_list('ip', flat=True).distinct()
        # ip 去重
        ip_list = set(ip_list)
        return HttpResponse("<br />".join(ip_list))

    def export_unimportant_alarm_handler(self, alarm_inst_conditions=None):
        alarm_inst_conditions = self.get_alarm_conditions(alarm_inst_conditions)
        unimportant_list = self.get_unimportant_alarm_query(
            alarm_inst_conditions,
        )
        alarm_types = AlarmType.get_description_mappings(self.cc_biz_id)
        return render_mako_context(
            self.request, '/fta_solutions/unimportant_alarms.html', {
                "alarm_types": alarm_types,
                "solution_types": self.SOLUTION_TYPES,
                "unimportant_list": unimportant_list,
                "cc_biz_id": self.cc_biz_id,
            }
        )

    def export_unimportant_alarm_count_handler(self, alarm_inst_conditions=None):
        alarm_inst_conditions = self.get_alarm_conditions(alarm_inst_conditions)
        unimportant_list = self.get_unimportant_alarm_query(alarm_inst_conditions, )
        return HttpResponse(str(unimportant_list.count()))

    def export_default_handler(self):
        username = self.username
        form = self.form
        cc_biz_id = self.cc_biz_id
        request = self.request

        alarm_type_dict = AlarmType.get_description_mappings(cc_biz_id, is_handle_alert=True, )

        set_list = cash._get_app_topo_set_with_cache(cc_biz_id, username)
        set_names = {
            s['SetName']: s.get('SetChnName') or s.get('SetName')
            for s in set_list
        }
        incident_desc = cash.list_incident_desc()

        cc_toposet = cash._get_app_topo_set_with_cache(cc_biz_id, username) if cc_biz_id else []
        cc_appmodules = cash._get_app_module_with_cache(cc_biz_id, username) if cc_biz_id else []
        cc_topo_set = form.cleaned_data.get('cc_topo_set', None)
        cc_app_module = form.cleaned_data.get('cc_app_module', None)
        alarm_type = form.cleaned_data['alarm_type']
        begin_date, end_date = form.cleaned_data['date']

        # 分页参数
        default_page_size = 200
        try:
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", default_page_size))

            if page < 1:
                page = 1
            if page_size < 1:
                page_size = default_page_size
        except Exception:
            page = 1
            page_size = default_page_size

        alarm_instance_qs = self.get_important_alarm_query()
        instance_count = alarm_instance_qs.count()

        # 只查询当前页面的告警数据
        paginator = Paginator(alarm_instance_qs, page_size)
        try:
            alarm_instance_qs = paginator.page(page)
        except PageNotAnInteger:
            alarm_instance_qs = paginator.page(1)
        except EmptyPage:
            alarm_instance_qs = paginator.page(paginator.num_pages)
        alarm_ids_in_cur_page = list(alarm.id for alarm in alarm_instance_qs)

        incidents_qs = self.get_incident_query()

        incidents = {x.pk: x for x in incidents_qs}

        inc_alarms = list(IncidentAlarm.objects.filter(
            incident_id__in=incidents.keys(),
            alarm_id__in=alarm_ids_in_cur_page))
        alarm_ids_in_inc = [ia.alarm_id for ia in inc_alarms]
        inc_ids = set([ia.incident_id for ia in inc_alarms])

        # 过滤掉0个关联告警的事件（实际上不应该存在，但收敛模块异常时可能出现）
        incidents = {
            _id: inc
            for _id, inc in incidents.iteritems()
            if _id in inc_ids and inc.begin_time is not None
        }
        # 收敛过滤条件处理，不查询独立告警
        if self.alarm_type in self.INC_TYPE_DICT:
            standalone_alarms = []
            standalone_alarm_ids = []
        else:
            standalone_alarms = list(
                i for i in alarm_instance_qs
                if ((i.source_time is not None) and (i.pk not in alarm_ids_in_inc))
            )
            standalone_alarm_ids = [a.pk for a in standalone_alarms]

        all_alarm_ids = list(set(alarm_ids_in_inc + standalone_alarm_ids))

        _records = sorted(
            standalone_alarms + incidents.values(),
            key=lambda x: (
                x.source_time
                if isinstance(x, AlarmInstance)
                else x.begin_time
            ),
            reverse=True,
        )

        alarms_qs = self.get_important_alarm_query({"pk__in": all_alarm_ids, }, with_form_filter=True)
        if cc_biz_id:
            alarms_qs = alarms_qs.filter(cc_biz_id=cc_biz_id)
        alarms = {x.pk: x for x in alarms_qs}

        for _id, inc in incidents.iteritems():
            alarm_ids = [ia.alarm_id for ia in inc_alarms if ia.incident_id == _id]
            inc.alarms = []
            for alarm_id in alarm_ids:
                if alarms.get(alarm_id):
                    inc.alarms.append(alarms[alarm_id])

            worlds = [set_names.get(a.cc_topo_set) or a.cc_topo_set for a in inc.alarms]
            worlds = set([w for w in worlds if w])
            inc.involved_worlds = ','.join(worlds)

            incidents[_id] = inc

        records = []
        for record in _records:
            if isinstance(record, AlarmInstance):
                records.append(alarms[record.pk])
                continue
            record = incidents.get(record.pk)
            if not record and not record.alarms:
                continue
            records.append(record)

        prev_date = arrow.get(begin_date).replace(days=-1)
        next_date = arrow.get(end_date).replace(days=1)

        begin_date = begin_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        prev_date = prev_date.strftime('%Y-%m-%d')
        next_date = next_date.strftime('%Y-%m-%d')

        # 判断业务是否已经接入到自愈
        if AlarmDef.objects.filter(cc_biz_id__in=[0, cc_biz_id]).exists():
            is_in_fta = True
        else:
            is_in_fta = False
        return render_mako_context(
            request, '/fta_solutions/alarm_instance_list.html',
            {
                "alarm_type_dict": alarm_type_dict,
                "inc_type_dict": self.INC_TYPE_DICT,
                "alarm_type": alarm_type,
                "cc_topo_set": cc_topo_set,
                "cc_toposet": cc_toposet,
                "cc_appmodules": cc_appmodules,
                "cc_app_module": cc_app_module,
                "status_dict": self.STATUS_DICT,
                "cc_biz_id": cc_biz_id,
                "records": records,
                "incident_desc": incident_desc,
                "begin_date": begin_date,
                "end_date": end_date,
                "form": form,
                "set_names": set_names,
                "is_in_fta": is_in_fta,
                "instance_count": instance_count,
                "alarm_records": alarm_instance_qs,
            }
        )

    EXPORT_HANDLERS = {
        "ip": export_ip_handler,  # 导出 ip
        "unimportant_alarm": export_unimportant_alarm_handler,  # 预警页面
        "unimportant_alarm_count": export_unimportant_alarm_count_handler,  # 预警的数目
        "default": export_default_handler,  # 自愈详情
    }

    def get(self, request, cc_biz_id=None):
        """
        告警详情列表

        本详情列表不显示套餐类型为空/汇总/等待 的
        这些都是仅存档的不重要告警，显示没有意义
        """
        self.username = request.user.username
        self.cc_biz_id = cc_biz_id
        self.form = form = AlarmInstFilterForm(request.GET)

        if not form.is_valid():
            return HttpResponseBadRequest()

        handler = self.EXPORT_HANDLERS.get(form.cleaned_data['export'] or "default")
        self.alarm_type = form.cleaned_data["alarm_type"]
        if not handler:
            return HttpResponseBadRequest()

        return handler(self)


def _render_unimportant_alarms(request, cc_biz_id, alarm_inst_conditions):
    # 此处查询空必须使用这个直接的条件，而不是放在in，因为in会把None当场字符串
    unimportant_list = AlarmInstance.objects.filter(
        source_type="FTA",
        cc_biz_id=cc_biz_id,
    ).filter(**alarm_inst_conditions).order_by("-id")
    alarm_types = AlarmType.get_description_mappings(cc_biz_id)
    solution_types = dict(fta_std.SOLUTION_TYPE_CHOICES)
    return render_mako_context(request, '/fta_solutions/unimportant_alarms.html', locals())


def alarm_instance_page(request, cc_biz_id, alarm_instance_id):
    """
    单页的告警流程页面
    2015.10.28

    graph = [
        ({1: ['~success']}, u'155'),
        ({2: ['~success'], 3: ['failure']}, u'1134'),
        ({5: ['success']}, u'1961'),
        ({4: ['success']}, u'1958'),
        ({5: ['success']}, u'1962'),
        ({6: ['~success']}, u'807'),
        ({7: ['~success']}, u'433'),
        ({8: ['success']}, u'367'),
        ({9: ['success']}, u'1958'),
        ({10: ['~success']}, u'1968'),
        ({11: ['success']}, u'480'),
        ({12: ['success']}, u'361'),
        ({13: ['success']}, u'1965'),
        ({}, u'360')
    ]
    """
    alarm = AlarmInstance.objects.get(id=alarm_instance_id, cc_biz_id=cc_biz_id)
    alarm_type_dict = AlarmType.get_description_mappings(cc_biz_id)
    status_dict = dict(fta_std.STATUS_CHOICES)
    status_color_dict = dict(fta_std.STATUS_COLOR)
    username = request.user.username
    cc_biz_names = CCBiz(username=username).items("ApplicationID", "ApplicationName")

    # 告警定义
    raw_alarm_def = json.loads(alarm.snap_alarm_def)

    # 查询所有的套餐，包含不在页面上展示的
    solutions = Solution.default_objects.filter(cc_biz_id__in=[alarm.cc_biz_id, 0])
    solutions_name_dict = {str(s.id): s.title for s in solutions}

    # 如果是个组合套餐绘制处理流程图
    solution = Solution(**json.loads(alarm.snap_solution or "{}"))

    # 查询每个节点的状态信息
    path_str = alarm.alarm_log_list.filter(step_name='node_path')
    node_status_dict = get_graph_status(alarm.id, path_str[0].content) if path_str else {}
    for k, v in node_status_dict.items():
        node_status_dict[k] = v if v in ["success", "running"] else "failure"

    real_solutions = []
    # logger.info("graph: %s" % graph)
    # logger.info("result: %s" % result)
    for idx, g in enumerate(solution.graph):
        graph_list = list(g)
        solution_id = str(graph_list[1])
        graph_list.append("#%s [%s] %s" % (idx, solution_id, _(solutions_name_dict.get(solution_id, u"已删除"))))
        graph_list.append(node_status_dict.get(idx, "noway"))
        real_solutions.append(graph_list)

    return render_mako_context(request, '/fta_solutions/alarm_instance_page.mako', locals())


def get_graph_status(alarm_instance_id, node_path):
    # 获得执行有哪些路径
    node_path_list = re.findall(r"=(\d*:*\d*)=", node_path)
    node_path = [p.replace(":", "-") for p in node_path_list]
    node_status_dict = {int(p.split("-")[0]): "running" for p in node_path}

    context_node_id = {"-".join(map(str, [alarm_instance_id, p])): int(p.split("-")[0]) for p in node_path}
    context_list = Context.objects.filter(key__in=context_node_id.keys(), field="result").all()

    node_status_dict.update({context_node_id[context.key]: json.loads(context.value) for context in context_list})
    return node_status_dict


def stop_flow(request, cc_biz_id):
    """
    强制停止告警处理流程
    2015.11.26
    """
    id = request.REQUEST.get("id", 0)
    try:
        alarm = AlarmInstance.objects.get(id=id, cc_biz_id=cc_biz_id, )
        alarm.status = "failure"
        alarm.failure_type = "user_abort"
        alarm.comment = _(u"[%s]强制终止了处理流程") % request.user.username
        alarm.save()
        AlarmInstanceLog.objects.create(alarm_instance_id=alarm.id, content=alarm.comment, level=20)
    except Exception, e:
        return render_ajax(False, unicode(e))
    return render_ajax(True)


def retry_flow(request, cc_biz_id):
    """
    重试执行告警处理流程
    2015.10.29
    """
    id = request.REQUEST.get("id", 0)
    node_idx = request.REQUEST.get("node_index", 0)
    try:
        # alarm = AlarmInstance.objects.get(id=id, cc_biz_id=cc_biz_id, )
        AlarmInstance.objects.get(id=id, cc_biz_id=cc_biz_id, )
        fsm_client.retry(id, node_idx)
    except Exception, e:
        return render_ajax(False, unicode(e))
    return render_ajax(True)


def approve_flow(request, cc_biz_id):
    """
    执行审批的流程
    2015.10.29
    """
    id = request.REQUEST.get("id", 0)
    approve = request.REQUEST.get("approve", "false")
    message = request.REQUEST.get("message", 0)
    logger.info("approve_flow: %s" % request.REQUEST)
    try:
        # alarm = AlarmInstance.objects.get(id=id, cc_biz_id=cc_biz_id, )
        AlarmInstance.objects.get(id=id, cc_biz_id=cc_biz_id, )
        approve = approve == "true"
        fsm_client.approve(id, approve, request.user.username, message)
    except Exception, e:
        return render_ajax(False, unicode(e))
    return render_ajax(True)
