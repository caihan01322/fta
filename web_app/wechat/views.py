# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import json
import re

import xmltodict
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from common.log import logger
from common.mymako import render_json, render_mako_context
from common.utils import render_ajax
from fta_solutions_app import fta_std
from fta_solutions_app.models import AlarmInstance, Advice, AlarmType, Conf
from fta_utils import fsm_client
from fta_utils.component import bk
from project.conf.decorators import login_exempt
from wechat.auth.utils import get_user_bizs, is_app_in_user_bizs, is_wehcat_super_approver
from wechat.exceptions import APIError
from wechat.models import Approve
from wechat.msg_crypt.WXBizMsgCrypt import WXBizMsgCrypt

STATE_NAME_MAP = dict(fta_std.STATUS_CHOICES)


def _get_login_url():
    """
    微信登录页面
    """
    wechat_app_url = Conf.get('WECHAT_APP_URL')
    return '%saccounts/login/' % wechat_app_url


@login_exempt
@csrf_exempt
def entry(request):
    """微信处理入口
    """
    msg_crypt = WXBizMsgCrypt(
        Conf.get('WECHAT_TOKEN'),
        Conf.get('WECHAT_ENCODING_AES_KEY'),
        Conf.get('WECHAT_CORPID'))
    msg_signature = request.GET.get('msg_signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')

    if request.method == 'GET':
        echostr = request.GET.get('echostr')
        result = msg_crypt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        return HttpResponse(result[1])
    else:
        logger.info('wechat request raw body: %s' % request.body)
        result = msg_crypt.DecryptMsg(request.body, msg_signature, timestamp, nonce)
        logger.info('wechat request decrypt body: %s, %s' % result)
        if result[0] != 0:
            return HttpResponse('403')

        json_obj = xmltodict.parse(result[1])
        msg_type = json_obj['xml']['MsgType']

        # 只处理text请求
        if msg_type != 'text':
            return HttpResponse('403')

        # from_user = json_obj['xml']['FromUserName']
        from_user = user_transfer(json_obj['xml']['FromUserName'])
        content = json_obj['xml']['Content']

        match = re.match(r'(?P<action>\w+) (?P<obj_id>\d+_\d+)$', content)
        if not match:
            return HttpResponse('403')

        action, obj_id = match.groups()
        if action not in ['TY', 'BH']:
            return HttpResponse('403')

        obj = Approve.objects.filter(obj_id=obj_id, status='WAITING').first()
        if not obj:
            return HttpResponse('403')

        if from_user not in obj.to_users:
            return HttpResponse('403')

        try:
            obj.callback(action, from_user)
        except Exception as error:
            logger.error(u"微信审批异常: %s" % error)
            return HttpResponse('500')
        return HttpResponse('200')


@login_exempt
@csrf_exempt
def create_approve(request):
    """创建审批单API
    包含：自愈故障替换API
    """
    try:
        token = request.META.get('HTTP_TOKEN')
        if token != Conf.get('WECHAT_API_TOKEN'):
            raise APIError(u"token不正确")
        try:
            data = json.loads(request.body)
        except Exception:
            raise APIError(u"POST不是合法JSON")

        message = data.get('message')
        if not message:
            raise APIError(u"字段【message】不能为空")

        verifier = data.get('verifier')
        if not verifier:
            raise APIError(u"字段【verifier】不能为空")

        callback_url = data.get('callback_url', '')

        obj_id = data.get('obj_id')
        if not obj_id:
            raise APIError(u"字段【obj_id】不能为空")

        obj = Approve(message=message, obj_id=obj_id, approve_users=verifier, callback_url=callback_url)
        # 保存
        obj.save()
        # 发送微信消息
        obj.send_message()
        content = {'result': True, 'message': u"创建审批单成功", 'data': {'approve_id': obj.id}}
        return render_json(content)

    except APIError as error:
        content = {'result': False, 'message': '%s' % error}
        return render_json(content)
    except Exception as error:
        logger.error(u'create_approval error: %s' % error)
        content = {'result': False, 'message': u"创建审批单异常"}
        return render_json(content)


@csrf_exempt
@login_exempt
@login_required(login_url=_get_login_url())
def todo(request):
    """
    待办事项页面，会把需要审批的告警列出
    """
    username = request.user.username
    now = timezone.now()
    date = now - datetime.timedelta(minutes=45)
    wechat_static_url = Conf.get('WECHAT_STATIC_URL')

    # get approve list of all biz
    approve_list = AlarmInstance.objects.filter(
        status='waiting',
        approved_time=None,
    )
    # 非超级管理员，则只展示用户业务相关的审批信息
    if not is_wehcat_super_approver(username):
        # 获取用户的业务列表
        user_bizs = get_user_bizs(username)
        approve_list = approve_list.filter(cc_biz_id__in=user_bizs)

    alarm_type_maps = {}
    for a in approve_list:
        if a.cc_biz_id not in alarm_type_maps:
            alarm_type_maps[a.cc_biz_id] = AlarmType.get_description_mappings(
                a.cc_biz_id,
            )
        alarm_type_map = alarm_type_maps[a.cc_biz_id]
        a.alarm_type = alarm_type_map[a.alarm_type]
        a.cc_biz_name = a.cc_biz_id

    return render_to_response('wechat/todo.html', RequestContext(request, locals()))


@csrf_exempt
@login_exempt
@login_required(login_url=_get_login_url())
def alarm_detail_fta(request, alarm_instance_id):
    """
    通过自愈告警记录id来查询告警信息
    """
    username = request.user.username
    try:
        inst = AlarmInstance.objects.get(id=alarm_instance_id)
    except AlarmInstance.DoesNotExist:
        return HttpResponseNotFound()
    else:
        # 判断用户是否有操作权限
        if not is_app_in_user_bizs(username, inst.cc_biz_id):
            return render_mako_context(request, 'wechat/wx_error.html', {'message': u"您没有该操作的权限"})

        alarm = json.loads(inst.origin_alarm)
        _append_instance_info(alarm, inst)
        wechat_static_url = Conf.get('WECHAT_STATIC_URL')

        return render_to_response('wechat/alarm_detail.html', RequestContext(request, locals()))


@csrf_exempt
@login_exempt
@login_required(login_url=_get_login_url())
def approve_flow(request):
    """
    执行审批的流程
    """
    username = request.user.username
    id = request.REQUEST.get("id", 0)
    approve = request.REQUEST.get("approve", "false")
    message = request.REQUEST.get("message", 0)
    logger.info("approve_flow: %s" % request.REQUEST)
    try:
        alarm = AlarmInstance.objects.get(id=id)
        # 判断用户是否有操作权限
        if not is_app_in_user_bizs(username, alarm.cc_biz_id):
            logger.error(u"wechat approve_flow username:%s, cc_biz_id:%s" %
                         (username, alarm.cc_biz_id))
            return render_ajax(False, u"您没有该操作的权限")

        # 通过message判断
        if message == 'approved':
            approve = True
            message = u"准许执行自愈套餐-（%s）微信操作" % request.user.username
        else:
            approve = False
            message = u"拒绝执行-（%s）微信操作" % request.user.username
        alarm.approved_user = request.user.username
        alarm.approved_comment = message
        alarm.approved_time = timezone.now()
        alarm.save()
        fsm_client.approve(id, approve, request.user.username, message)
    except Exception, e:
        logger.exception(u"wechat approve_flow")
        return render_ajax(False, unicode(e))
    return render_ajax(True)


def _append_instance_info(alarm, inst):
    """
    append info of alarm_instance onto alarm dict
    """

    alarm['state'] = STATE_NAME_MAP.get(inst.status)
    alarm['failure_type'] = inst.failure_type
    alarm['id'] = inst.id
    alarm['raw'] = inst.raw
    alarm['comment'] = inst.comment
    alarm['alarm_type'] = inst.alarm_type
    alarm['create_time'] = inst.source_time_show
    # alarm['log'] = inst.alarminstancelog_set.filter(level__gte=10)
    alarm['log'] = inst.alarm_log_list.filter(level__gte=10)
    for log in alarm['log']:
        try:
            json_log = json.loads(log.content)
        except Exception:
            json_log = ''
        log.json_content = json_log
    alarm['alarm_instance_id'] = inst.id
    alarm['source_id'] = inst.source_id
    alarm['bpm_task_id'] = inst.bpm_task_id if inst.bpm_task_id else u'无'
    alarm['inc_alarm_id'] = inst.inc_alarm_id if inst.inc_alarm_id else u'无'
    alarm['cc_biz_id'] = inst.cc_biz_id
    alarm['origin_alarm'] = inst.origin_alarm
    alarm['cc_topo_set'] = inst.cc_topo_set
    alarm['cc_app_module'] = inst.cc_app_module
    # alarm['uwork_id'] = inst.uwork_id
    subject = None
    if inst.ip:
        alarm['ip'] = inst.ip
        subject = alarm['ip']
    if inst.alarm_type in fta_std.ALARM_TYPE_ONLINE:
        subject = alarm['cc_topo_set']
    if subject:
        advice_dict = {}
        advices = Advice.objects.filter(
            subject=subject, status='fresh',
            create_time__gt=timezone.now() - datetime.timedelta(days=7))
        for advice in advices:
            if not advice_dict.get(advice.advice_def.id):
                advice_dict[advice.advice_def.id] = advice
        alarm['advice'] = advice_dict.values()


def user_transfer(wx_user):
    try:
        users = get_all_user()
        for user in users:
            if user["wx_userid"] and user["wx_userid"] == wx_user:
                return user["username"]
    except Exception as e:
        logger.error(u"微信帐号[%s]转换为用户失败: %s" % (wx_user, e))
        return ""


def get_all_user():
    try:
        result = bk.bk_login.get_all_user()
        data = result.get("data")
        return data
    except Exception as e:
        logger.error(u"获取所有用户失败: %s" % e)
        return {}
