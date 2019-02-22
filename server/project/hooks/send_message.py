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
from project.utils import get_plat_info, query_cc

from fta import constants, settings
from fta.utils import logging, send
from fta.utils.i18n import _, localtime
from fta.utils.instance_log import list_alarm_instance_log
from fta.utils.monitors import get_description_by_alarm_type
from fta.utils.send_message import NOTIFY_TYPE

logger = logging.getLogger('utils')

HLINE = u'-' * 19  # 用于信息展示区域划分


def notice_collect_wechat(verifier, **kwargs):
    message = get_collect_message(kwargs["status"])
    kwargs["cc_biz_name"] = query_cc.get_cc_biz_attr(str(kwargs["cc_biz_name"]), 'ApplicationName')
    if send.wechat(verifier, message=message % kwargs) is False:
        send.sms(verifier, message=message % kwargs)


def notice_collect_sms(verifier, **kwargs):
    message = get_collect_message(kwargs["status"])
    kwargs["cc_biz_name"] = query_cc.get_cc_biz_attr(str(kwargs["cc_biz_name"]), 'ApplicationName')
    if send.sms(verifier, message=message % kwargs) is False:
        send.wechat(verifier, message=message % kwargs)


def notice_collect_phone(verifier, **kwargs):
    if kwargs["status"] == "BEGIN":
        kwargs["collect_count"] = 1
        kwargs["time_desc"] = kwargs["begin_time"]
    kwargs["cc_biz_name"] = query_cc.get_cc_biz_attr(str(kwargs["cc_biz_name"]), 'ApplicationName')
    message = _("BlueKing monitoring collection notice,"
                "Business %(cc_biz_name)s"
                "At %(time_desc)s"
                "Article %(collect_count)s appears"
                "%(alarm_type)s Alarms")
    send.phone(verifier, message=message % kwargs)


def notice_mail_from_plat(alarm_info, verifier):
    mail_title = _("[Auto-recovery Notification] {alarm_type} {cc_biz_name} {result_title}").format(**alarm_info)
    mail_content = send.render_mail(alarm_info, "manager/www/webservice/templates/mail/info.html")
    send.mail(",".join(verifier), mail_content, title=mail_title)


def notice_mail(kind, alarm_instance, message, verifier):
    logger.info("$%s notice_mail %s", alarm_instance["id"], verifier)
    alarm_info = get_alarm_info(alarm_instance, message, kind)
    notice_mail_from_plat(alarm_info, verifier)


def get_collect_message(status):
    if status == 'BEGIN':
        return u"\n".join([
            _("[Auto-recovery Collection Start] [(%(collect_type)s)]"),
            _("Business: %(cc_biz_name)s"),
            _("Alarm Type: %(alarm_type)s"),
            _("Description: %(description)s"),
            _("Dimension: %(dimension)s"),
            _("At %(begin_time)s"),
            _("Article 1 appears"),
        ])
    elif status == 'END':
        return u"\n".join([
            _("[Auto-recovery Collection Complete] [(%(collect_type)s)]"),
            _("Business: %(cc_biz_name)s"),
            _("Alarm Type: %(alarm_type)s"),
            _("Description: %(description)s"),
            _("Dimension: %(dimension)s"),
            u"%(time_desc)s",
            _("Article %(collect_count)s appears"),
            _("Details %(url)s")
        ])
    logger.warning('pass unknow collect status: %s', status)


def get_alarm_subject(alarm_instance):
    if alarm_instance.get("ip"):
        plat_info = get_plat_info(alarm_instance)
        return u"IP[%s](%s)" % (
            alarm_instance["ip"],
            query_cc.get_host_brief_info(plat_info['plat_id'], plat_info['company_id'], alarm_instance["ip"]))
    elif alarm_instance.get("cc_topo_set"):
        return u"SET[%s]" % alarm_instance["cc_topo_set"]
    else:
        subject = ""
        try:
            dimensions = get_dimensions(alarm_instance)
            if dimensions:
                subject = ",".join(["%s=%s" % (k, v) for k, v in dimensions.items() if k != 'anomaly_type'])
        except Exception as e:
            logger.exception("get_alarm_subject error %s, alarm_instance: %s", e, alarm_instance)
        return subject


def get_alarm_info(alarm_instance, message, kind):
    """生成通知内容"""
    solution = json.loads(alarm_instance['snap_solution'] or '{}')
    plat_info = get_plat_info(alarm_instance)
    if settings.ENV == "PRODUCT":
        instance_url = "%s%s/alarm_instance/page/%s/" % (
            settings.APP_URL_PROD, alarm_instance['cc_biz_id'], alarm_instance["id"])
    else:
        instance_url = "%s%s/alarm_instance/page/%s/" % (
            settings.APP_URL_TEST, alarm_instance['cc_biz_id'], alarm_instance["id"])
    cur_year = arrow.now().format("YYYY")
    return {
        'result_title': NOTIFY_TYPE[kind],
        'cc_biz_name': query_cc.get_cc_biz_attr(alarm_instance['cc_biz_id'], 'ApplicationName'),
        'host': alarm_instance['ip'],
        'host_info': query_cc.get_host_brief_info(plat_info['plat_id'], plat_info['company_id'], alarm_instance['ip']),
        'brief_time': localtime(alarm_instance['source_time']).strftime(constants.SIMPLE_DT_FORMAT),
        'alarm_type': _(get_description_by_alarm_type(
            alarm_instance['alarm_type'],
            cc_biz_id=alarm_instance['cc_biz_id'],
            default=alarm_instance['alarm_type'],
        )),
        'alarm_detail': alarm_instance['raw'],
        'instance_id': alarm_instance["id"],
        'instance_url': instance_url,
        'result_status': kind,
        'result_detail': message or _("None"),
        'solution': _(solution.get('title')) or _("No processing"),
        'alarm_logs': _remove_log_datetime_format(list_alarm_instance_log(alarm_instance['id'])),
        'cur_year': cur_year,
    }


def get_dimensions(alarm_instance):
    origin_alarm = json.loads(alarm_instance["origin_alarm"])
    try:
        origin_dimension = origin_alarm.get("dimensions_alias") or origin_alarm["alarm_info"]["dimensions"]
    except BaseException:
        try:
            origin_dimension = origin_alarm["dimensions"]
        except BaseException:
            origin_dimension = {}
    return origin_dimension


def _remove_log_datetime_format(alarm_logs):
    """移除告警日志中的datetime(发邮件接口不支持datetime)"""
    for log in alarm_logs:
        log['time'] = arrow.get(log['time']).format('YYYY-MM-DD HH:mm:ss')
    return alarm_logs
