# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
此模块负责所有告警的自愈处理通知，包括开始，结束，收敛等
"""

import json

import arrow

from fta import constants
from fta.utils import get_time, hooks, logging, people, remove_tag, send
from fta.utils.conf import get_fta_admin_list
from fta.utils.i18n import gettext
from fta.utils.i18n import lazy_gettext as _
from fta.utils.i18n import lazy_join, localtime
from fta.utils.monitors import get_description_by_alarm_type
from fta.utils.rate_limit import SlidingWindow
from fta.utils.rate_limit import check_defense as raw_check_defense

__ALL__ = ['notify_info', 'notify_collect']

logger = logging.getLogger('utils')

HLINE = u'-' * 19  # 用于信息展示区域划分

STATUS_NOTIFY_DICT = {
    "received": "begin",
    "converged": "begin",
    "waiting": "approval",
    "failure": "failure",
    "success": "success",
    "almost_success": "almost_success",
    "skipped": "skipped",
    "for_notice": "notice",
    "for_reference": "success",
    "authorized": "success",
    "unauthorized": "success",
    "checking": "success",
    "finished": "finished",
}

NOTIFY_TYPE = {
    "begin": _("[Auto-recovery start]"),
    "success": _("[Auto-recovery success]"),
    "almost_success": _("[Auto-recovery almost success]"),
    "skipped": _("[Auto-recovery skip]"),
    "timeout": _("[Auto-recovery timeout]"),
    "failure": _("[Auto-recovery failed]"),
    "framework_code_failure": _("[Auto-recovery error occurred]"),
    "approval": _("[Auto-recovery wait approval]"),
    "notice": _("[Auto-recovery flow control skip]"),
    "finished": _("Alarm end notification"),
}

TRANS = {
    "begin": "begin",
    "success": "success",
    "skipped": "success",
    "almost_success": "success",
    "timeout": "failure",
    "failure": "failure",
    "framework_code_failure": "failure",
    "finished": "finished",
}

FAILURE_KIND = ["framework_code_failure", "timeout"]

COLLECT_MESSAGE = lazy_join([
    _("[Auto-recovery summary %(status)s] [%(collect_type)s]"),
    _("Business: %(cc_biz_name)s"),
    _("Alarm type: %(alarm_type)s"),
    _("Description: %(description)s"),
    _("Dimension: %(dimension)s"),
    _("Time: %(time_desc)s"),
    _("%(collect_count)s appears"),
    _("Detail %(url)s")
], u"\n")

DEFENSE_TIME = {
    "wechat": 5 * 60,
    "im": 5 * 60,
    "sms": 5 * 60,
    "mail": 5 * 60,
    "phone": 30 * 60,
}
DEFENSE_COUNT = {
    "wechat": 10,
    "im": 10,
    "sms": 10,
    "mail": 10,
    "phone": 2,
}


def notify_collect(status, verifier,
                   notice_wechat=True, notice_sms=False,
                   notice_mail=False, notice_im=False,
                   notice_phone=False, **kwargs):
    logger.info('notify_collect: %s %s', status, verifier)

    kwargs["time_desc"] = get_time.get_time_range_desc(
        kwargs["begin_time"], kwargs["end_time"], breaks="\n")
    kwargs["status"] = status.upper()

    kwargs['begin_time'] = localtime(kwargs['begin_time']).strftime(constants.SIMPLE_DT_FORMAT)
    kwargs['end_time'] = localtime(kwargs['end_time']).strftime(constants.SIMPLE_DT_FORMAT)

    if notice_wechat:
        notice_collect_wechat(verifier, **kwargs)
    if notice_sms:
        notice_collect_sms(verifier, **kwargs)
    if notice_mail:
        notice_collect_mail(verifier, **kwargs)
    if notice_im:
        notice_collect_im(verifier, **kwargs)
    if notice_phone:
        notice_collect_phone(verifier, **kwargs)


def default_notice_collect_sms(verifier, **kwargs):
    if send.sms(verifier, message=COLLECT_MESSAGE % kwargs) is False:
        send.wechat(verifier, message=COLLECT_MESSAGE % kwargs)


def default_notice_collect_wechat(verifier, **kwargs):
    if send.wechat(verifier, message=COLLECT_MESSAGE % kwargs) is False:
        send.sms(verifier, message=COLLECT_MESSAGE % kwargs)


def default_notice_collect_im(verifier, **kwargs):
    send.im(verifier, message=COLLECT_MESSAGE % kwargs)


def default_notice_collect_mail(verifier, **kwargs):
    send.mail(verifier, message=COLLECT_MESSAGE % kwargs,
              title=_("[Fault Auto-recovery] summary notification"))


def default_notice_collect_phone(verifier, **kwargs):
    if kwargs["status"] == "BEGIN":
        kwargs["collect_count"] = 1
        kwargs["time_desc"] = kwargs["begin_time"]
    message = (
        _("FTA summary notification,"),
        _("Business %(cc_biz_name)s", cc_biz_name=kwargs['cc_biz_name']),
        _("At %(time_desc)s", time_desc=kwargs['time_desc']),
        _("Appears %(collect_count)s ", collect_count=kwargs['collect_count']),
        _("%(alarm_type)s alarm(s)", alarm_type=kwargs['alarm_type'])
    )
    send.phone(verifier, message='\n'.join(message))


def notify_info(alarm_instance, message=""):
    """根据alarm_instance的状态，发送通知"""

    kind = STATUS_NOTIFY_DICT.get(alarm_instance['status'])
    if kind == 'failure' and alarm_instance['failure_type'] in FAILURE_KIND:
        kind = alarm_instance['failure_type']

    if kind is None:
        logger.info('$%s skip notify_info when %s',
                    alarm_instance['id'], alarm_instance['status'])
        return

    fta_admin_list = get_fta_admin_list()
    verifier = people.get_verifier(alarm_instance['id'])
    # 框架错误通知人添加管理员
    if kind in ["framework_code_failure"]:
        copy_verifier = [v for v in verifier]
        copy_verifier.extend(fta_admin_list)
        verifier = copy_verifier
    logger.info('$%s notify_info: %s %s', alarm_instance['id'], kind, verifier)

    alarm_def = json.loads(alarm_instance['snap_alarm_def'])
    notify_conf = json.loads(alarm_def.get('notify', '{}') or '{}')
    conf_type = TRANS.get(kind)

    # 发送短信通知
    if conf_type and notify_conf.get('{}_notify_sms'.format(conf_type)):
        if check_defense(alarm_instance, verifier, 'sms') is False:
            notice_sms(kind, alarm_instance, message, verifier)

    # 发送 IM 通知
    if conf_type and notify_conf.get('{}_notify_im'.format(conf_type)):
        if check_defense(alarm_instance, verifier, 'im') is False:
            notice_im(kind, alarm_instance, message, verifier)

    # 发送电话通知
    if conf_type and notify_conf.get('{}_notify_phone'.format(conf_type)):
        if check_defense(alarm_instance, verifier, 'phone') is False:
            notice_phone(kind, alarm_instance, message, verifier)

    # 发送微信通知
    if conf_type and notify_conf.get('{}_notify_wechat'.format(conf_type)):
        if check_defense(alarm_instance, verifier, 'wechat') is False:
            notice_wechat(kind, alarm_instance, message, verifier)
    else:
        logger.info('$%s skip notify_info when %s', alarm_instance['id'], kind)

    # 发送邮件通知
    if (conf_type and notify_conf.get('{}_notify_mail'.format(conf_type))) \
            or conf_type == "failure":  # 确保失败会发送通知
        if check_defense(alarm_instance, verifier, 'mail') is False:
            notice_mail(kind, alarm_instance, message, verifier)
    else:
        logger.info('$%s skip notify_info when %s', alarm_instance['id'], kind)


def collect_notify_message(
        key, method, status, alarm_type, alarm_attr_id, cc_biz_id, verifier):
    logger.info('collect_notify_message: %s %s', key, verifier)

    scope = arrow.now().timestamp
    slideing_window = SlidingWindow(
        key, DEFENSE_TIME[method], DEFENSE_COUNT[method])
    alarm_instance_list = slideing_window.get_list(scope)
    slideing_window.clear()

    logger.info('collect_notify_message alarm_instance_list:%s' % alarm_instance_list)
    time_desc = get_time.get_time_range_desc(
        alarm_instance_list[0][1],
        alarm_instance_list[-1][1],
        to_local=True)
    alarm_type_desc = get_description_by_alarm_type(
        alarm_type, cc_biz_id=cc_biz_id, default=alarm_type,
    )
    if alarm_attr_id:
        alarm_type_desc += _("(Strategy ID: %(alarm_attr_id)s)", alarm_attr_id=alarm_attr_id)
    status_desc = constants.INSTANCE_STATUS_DESCRIPTION[status]

    lines = [
        _("[Monitoring Notification] [Summary of notifications] "),
        _("Alarm Type: %(alarm_type_desc)s", alarm_type_desc=alarm_type_desc),
        _("Business: %(biz_name)s".format(people.get_biz_name(cc_biz_id))),
        _("Status: %(status_desc)s", status_desc=status_desc),
        _("At: %(time_desc)s", time_desc=time_desc),
        _("Appeared %(alarm_count)s, please log in to system to see details", alarm_count=len(alarm_instance_list)),
        _("-------- [Description] --------"),
        _("(%(defence_count)s same status notifications with the same business "
          "and same type of alarms were issued before. "
          "No more single notifications. This is summary notification.)",
          defense_count=DEFENSE_COUNT[method])
    ]
    if method == "phone":
        message = _("Monitoring exception notification\n"
                    "Business %(cc_biz_id)s %(time_desc)s Appearing batch %(type_desc)s "
                    "alarm %(status_desc)s phone notification，%(count)s notification(s) converged)",
                    cc_biz_id=cc_biz_id,
                    time_desc=time_desc,
                    type_desc=alarm_type_desc,
                    status_desc=status_desc,
                    count=len(alarm_instance_list) - DEFENSE_COUNT[method]
                    )
        send.phone(verifier, message)
    elif method == "mail":
        send.mail(verifier, constants.MAIL_BREAKS.join(lines), lines[0])
    else:
        method_func = getattr(send, method)
        method_func(verifier, constants.WECHAT_BREAKS.join(lines))


def check_defense(alarm_instance, verifier, method):
    """验证告警通知的频率，超出频率设置定时任务发送汇总通知"""
    alarm_def = json.loads(alarm_instance["snap_alarm_def"])
    return raw_check_defense(
        callback_func=collect_notify_message,
        callback_kwargs={"verifier": verifier},
        time=DEFENSE_TIME[method],
        count=DEFENSE_COUNT[method],
        obj_id=alarm_instance["id"],
        key_prefix="notify_message",
        key_args=[method,
                  alarm_instance["status"],
                  alarm_instance["alarm_type"],
                  alarm_def.get('alarm_attr_id') or alarm_def.get('attr_id'),
                  alarm_instance["cc_biz_id"]]
    )


def default_notice_wechat(kind, alarm_instance, message, verifier):

    solution = json.loads(alarm_instance['snap_solution'] or '{}')
    cc_biz_name = alarm_instance['cc_biz_id']
    try:
        cc_biz_name = people.get_biz_name(cc_biz_name)
    except BaseException:
        pass

    lines = [
        NOTIFY_TYPE[kind],
        _("Business: %(biz_name)s", biz_name=cc_biz_name),
        _("Module: %(cc_app_module)s", cc_app_module=_(alarm_instance['cc_app_module'])),
        _("Host: %(ip)s", ip=alarm_instance['ip']),
        HLINE,
        _("Alarm Type: %(alarm_type)s", alarm_type=alarm_instance['alarm_type']),
        _("Alarm Content: %(alarm_raw)s", alarm_raw=alarm_instance['raw']),
        _("Alarm Time: %(source_time)s",
          source_time=localtime(alarm_instance['source_time']).strftime(constants.SIMPLE_DT_FORMAT)),
        HLINE,
        _('Alarm Solution: %(title)s', title=_(solution.get('title')) or _("No processing")),
    ]
    if message:
        lines.append(_("Auto-recovery result: %(message)s", message=message))

    wechat_message = remove_tag(lazy_join(lines, constants.WECHAT_BREAKS))
    send.wechat(','.join(verifier), message=wechat_message)


def default_notice_mail(kind, alarm_instance, message, verifier):
    cc_biz_name = alarm_instance['cc_biz_id']
    try:
        cc_biz_name = people.get_biz_name(cc_biz_name)
    except BaseException:
        pass
    mail_title = _(
        '[Fault Auto-recovery] %(alarm_type)s %(cc_biz_id)s (%(notify_type)s)',
        alarm_type=alarm_instance['alarm_type'],
        cc_biz_id=cc_biz_name,
        notify_type=NOTIFY_TYPE[kind])
    mail_content = _(
        "%(kind)s [%(cc_biz_id)s] business (%(alarm_type)s) alarm, IP(%(ip)s)%(message)s: %(raw)s",
        kind=NOTIFY_TYPE.get(kind),
        cc_biz_id=cc_biz_name,
        alarm_type=get_description_by_alarm_type(
            alarm_instance['alarm_type'],
            cc_biz_id=alarm_instance['cc_biz_id'],
            default=alarm_instance['alarm_type'],
        ),
        ip=alarm_instance['ip'],
        message=message,
        raw=alarm_instance['raw'],
    )
    send.mail(','.join(verifier), mail_content, title=mail_title)


def default_notice_sms(kind, alarm_instance, message, verifier):
    cc_biz_name = alarm_instance['cc_biz_id']
    try:
        cc_biz_name = people.get_biz_name(cc_biz_name)
    except BaseException:
        pass
    if message:
        message = u": %s" % message
    send.sms(
        ','.join(verifier),
        _("%(kind)s [%(cc_biz_id)s] business [%(alarm_type)s] alarm, IP[%(ip)s]%(message)s: %(raw)s",
            kind=NOTIFY_TYPE.get(kind),
            cc_biz_id=cc_biz_name,
            alarm_type=get_description_by_alarm_type(
                alarm_instance['alarm_type'],
                cc_biz_id=alarm_instance['cc_biz_id'],
                default=alarm_instance['alarm_type'],
            ),
            ip=alarm_instance['ip'],
            message=message,
            raw=alarm_instance['raw'],
          )
    )


def default_notice_im(kind, alarm_instance, message, verifier):
    cc_biz_name = alarm_instance['cc_biz_id']
    try:
        cc_biz_name = people.get_biz_name(cc_biz_name)
    except BaseException:
        pass
    if message:
        message = u": %s" % message
    send.im(
        ','.join(verifier),
        _("%(kind)s [%(cc_biz_id)s] business [%(alarm_type)s] alarm, IP[%(ip)s]%(message)s: %(raw)s",
            kind=NOTIFY_TYPE.get(kind),
            cc_biz_id=cc_biz_name,
            alarm_type=get_description_by_alarm_type(
                alarm_instance['alarm_type'],
                cc_biz_id=alarm_instance['cc_biz_id'],
                default=alarm_instance['alarm_type'],
            ),
            ip=alarm_instance['ip'],
            message=message,
            raw=alarm_instance['raw'],
          )
    )


def default_notice_phone(kind, alarm_instance, message, verifier):
    cc_biz_name = alarm_instance['cc_biz_id']
    try:
        cc_biz_name = people.get_biz_name(cc_biz_name)
    except BaseException:
        pass
    send.phone(
        ",".join(verifier),
        # json不能lazy
        gettext(
            "Fault Auto-recovery %(notify_type)s,%(cc_biz_id)s business %(alarm_type)s alarm",
            notify_type=NOTIFY_TYPE.get(kind),
            cc_biz_id=cc_biz_name,
            alarm_type=get_description_by_alarm_type(
                alarm_instance['alarm_type'],
                cc_biz_id=alarm_instance['cc_biz_id'],
                default=alarm_instance['alarm_type'],
            ),
        )
    )


hook = hooks.HookManager("send_message")
notice_collect_sms = hook.get('notice_collect_sms',
                              default_notice_collect_sms)
notice_collect_wechat = hook.get('notice_collect_wechat',
                                 default_notice_collect_wechat)
notice_collect_im = hook.get('notice_collect_im',
                             default_notice_collect_im)
notice_collect_mail = hook.get('notice_collect_mail',
                               default_notice_collect_mail)
notice_collect_phone = hook.get('notice_collect_phone',
                                default_notice_collect_phone)
notice_sms = hook.get('notice_sms', default_notice_sms)
notice_im = hook.get('notice_im', default_notice_im)
notice_phone = hook.get('notice_phone', default_notice_phone)
notice_wechat = hook.get('notice_wechat', default_notice_wechat)
notice_mail = hook.get('notice_mail', default_notice_mail)
