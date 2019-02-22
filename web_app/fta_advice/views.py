# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from common.log import logger
from common.mymako import render_mako_context, render_mako_tostring_context
from fta_solutions_app import cache_utils as cash
from fta_solutions_app import fta_std
from fta_solutions_app.models import Solution, AdviceFtaDef, AdviceDef, AlarmType


def advice_fta_def_list(request, cc_biz_id):
    """
    预警自愈列表
    """
    # 只显示本业务策略 和 全业务中已开启的策略
    advice_fta_list = AdviceFtaDef.objects.filter(
        Q(cc_biz_id=cc_biz_id) | Q(cc_biz_id=0, is_enabled=True)
    )
    fta_ins_dict = AdviceFtaDef.get_related_instance(cc_biz_id)
    context = {
        'advice_fta_list': advice_fta_list,
        'fta_ins_dict': fta_ins_dict,
        'cc_biz_id': cc_biz_id
    }
    return render_mako_context(request, '/fta_advice/advice_fta_def_list.html', context)


def edit_advice_fta_def(request, cc_biz_id, advice_fta_def_id):
    """
    添加/编辑预警自愈页面
    """
    username = request.user.username
    if advice_fta_def_id != '0':
        try:
            advice_fta_def = AdviceFtaDef.objects.get(id=advice_fta_def_id, cc_biz_id=cc_biz_id)
        except Exception:
            return HttpResponse(_(u"id为[%s]的预警自愈定义不存在") % advice_fta_def_id)
        edit = True
        responsible_list = advice_fta_def.responsible.split(';') if advice_fta_def.responsible else []
    else:
        advice_fta_def = None
        edit = False
        responsible_list = []

    # 获取集群、模块、用户信息
    # 业务SET -> 业务模块之间的对应关系
    topo_set_to_module_dict = cash.get_app_topo_set_to_module_dict(cc_biz_id, username)
    # 业务下的 SET 列表
    app_sets = cash._get_app_topo_set_with_cache(cc_biz_id, username)
    # 业务下的模块列表
    app_modules = cash._get_app_module_with_cache(cc_biz_id, username)

    # 业务运维
    maintainers = cash.get_biz_responsible(cc_biz_id, username)
    #  开发商下所有用户
    all_user_info = cash.get_all_user_info(cc_biz_id, username)

    # 获取业务相关的所有建议信息
    advice_def_list = AdviceDef.objects.filter(cc_biz_id__in=[cc_biz_id, 0]).order_by('cc_biz_id')

    # 获取业务相关的资源套餐信息
    solution_list = Solution.objects.filter(cc_biz_id__in=[cc_biz_id, 0]).order_by('cc_biz_id', 'title')

    # 配置建议相关的数据
    source_type_dict = dict(fta_std.SOURCE_TYPE_CHOICES)
    src_type_group = AlarmType.get_source_type_mappings(cc_biz_id, is_handle_alert=True)

    context = {
        'cc_biz_id': cc_biz_id,
        'edit': edit,
        'advice_fta_def': advice_fta_def,
        'responsible_list': responsible_list,
        'topo_set_to_module_dict': topo_set_to_module_dict,
        'app_sets': app_sets,
        'app_modules': app_modules,
        'maintainers': maintainers,
        'all_user_info': all_user_info,
        'advice_def_list': advice_def_list,
        'solution_list': solution_list,
        'source_type_dict': source_type_dict,
        'src_type_group': src_type_group,
    }
    return render_mako_context(request, '/fta_advice/advice_fta_def.html', context)


def save_advice_fta_def(request, cc_biz_id, advice_fta_def_id):
    """
    保存预警定义信息
    """
    result = {'result': True}

    alarm_type = request.POST['alarm_type']
    if not alarm_type:
        result = {'result': False, 'message': _(u"请选择告警类型")}
        return HttpResponse(json.dumps(result))

    interval = request.POST['interval']
    try:
        interval = int(interval)
    except Exception:
        result = {'result': False, 'message': _(u"考察时长请填写正整数")}
        return HttpResponse(json.dumps(result))
    if interval < 1:
        result = {'result': False, 'message': _(u"考察时长请填写正整数")}
        return HttpResponse(json.dumps(result))

    threshold = request.POST['threshold']
    try:
        threshold = int(threshold)
    except Exception:
        result = {'result': False, 'message': _(u"考察阈值请填写正整数")}
        return HttpResponse(json.dumps(result))
    if threshold < 1:
        result = {'result': False, 'message': _(u"考察阈值请填写正整数")}
        return HttpResponse(json.dumps(result))

    timeout = request.POST['timeout']
    try:
        timeout = int(timeout)
    except Exception:
        result = {'result': False, 'message': _(u"超时时间请填写正整数")}
        return HttpResponse(json.dumps(result))
    if timeout < 1:
        result = {'result': False, 'message': _(u"超时时间请填写正整数")}
        return HttpResponse(json.dumps(result))

    new_is_enabled = ('true' == request.POST['is_enabled'])
    # 编辑
    if advice_fta_def_id != '0':
        try:
            old_def = AdviceFtaDef.objects.get(cc_biz_id=cc_biz_id, id=advice_fta_def_id)
        except Exception:
            result = {'result': False, 'message': _(u"id为[%s]的预警自愈定义不存在") % advice_fta_def_id}
            return HttpResponse(json.dumps(result))

        # 修改 advice_def
        advice_def = old_def.advice_def
        advice_def.interval = interval
        advice_def.threshold = threshold
        advice_def.advice = request.POST['advice']
        advice_def.is_enabled = new_is_enabled
        advice_def.save()

        responsible = request.POST['responsible']
        old_def.is_enabled = new_is_enabled
        if request.POST.get('solution') and old_def.handle_type == 'solution':
            old_def.solution_id = request.POST.get('solution')
        else:
            old_def.solution_id = None
        old_def.timeout = request.POST['timeout']
        old_def.description = request.POST['description']
        old_def.cc_biz_id = request.POST['cc_biz_id']
        old_def.responsible = responsible
        old_def.module = request.POST['module']
        old_def.topo_set = request.POST['topo_set']
        old_def.notify = request.POST['notify']
        old_def.module_names = request.POST['module_names']
        old_def.set_names = request.POST['set_names']
        old_def.save()
        result['def_id'] = old_def.id
    # 新建
    else:
        try:
            # 新建关联的 advice_def
            advice_def = AdviceDef.objects.create(
                cc_biz_id=cc_biz_id,
                is_enabled=new_is_enabled,
                subject_type='host',
                check_type='alarm',
                advice_type='biz',
                interval=interval,
                threshold=threshold,
                check_sub_type=alarm_type,
                advice=request.POST['advice'],
            )
            advice_def_id = advice_def.id

            responsible = request.POST['responsible']
            new_def = AdviceFtaDef(
                advice_def_id=advice_def_id,
                cc_biz_id=cc_biz_id,
                is_enabled=new_is_enabled,
                timeout=timeout,
                description=request.POST['description'],
                responsible=responsible,
                module=request.POST['module'],
                topo_set=request.POST['topo_set'],
                module_names=request.POST['module_names'],
                set_names=request.POST['set_names'],
                notify=request.POST['notify'],
                handle_type=request.POST['handle_type']
            )
            if request.POST.get('solution') and new_def.handle_type == 'solution':
                new_def.solution_id = request.POST.get('solution')
            new_def.save()
            result['def_id'] = new_def.id
        except Exception, e:
            logger.exception(u"save AdviceFtaDef error:%s" % e)
            result = {'result': False, 'message': unicode(e)}
    return HttpResponse(json.dumps(result))


def del_advice_fta_def(request, cc_biz_id):
    """
    删除预警定义
    """
    result = {'result': True}
    try:
        AdviceFtaDef.objects.filter(cc_biz_id=cc_biz_id, id=request.POST['id']).delete()
    except Exception, e:
        logger.exception(u"del AdviceFtaDef error:%s" % e)
        result = {'result': False, 'message': unicode(e)}
    return HttpResponse(json.dumps(result))


def get_advice_def(request, cc_biz_id, advice_def_id):
    """
    获取建议定义的详细信息
    """
    try:
        advice_def = AdviceDef.objects.get(
            id=advice_def_id, cc_biz_id=cc_biz_id,
        )
    except Exception:
        advice_def = None

    context = {
        'advice_def_id': advice_def_id,
        'advice_def': advice_def,
    }
    advice_html = render_mako_tostring_context(request, '/fta_advice/advice_fta.part', context)

    return HttpResponse(advice_html)


def block_advice_fta_def(request, cc_biz_id):
    """
    开启、关闭，全业务预警自愈策略
    """
    try:
        with atomic():
            _def = AdviceFtaDef.objects.get(
                id=request.POST['id'], cc_biz_id=0,
            )
            block_list = (_def.exclude or '').split(',')
            if cc_biz_id in block_list:
                block_list.remove(cc_biz_id)
            else:
                block_list.append(cc_biz_id)
            _def.exclude = ','.join(block_list)
            _def.save()
    except Exception, e:
        return HttpResponse(json.dumps({'success': False, 'message': str(e)}))
    return HttpResponse(json.dumps({'success': True}))
