# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
# noflake
import arrow

from fta import constants, settings
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppIncident
from fta.utils import get_time, hooks, people, send
from fta.utils.i18n import _
from fta.utils.monitors import get_description_by_alarm_type
from fta.utils.people import get_biz_name


def _get_incident_url(incident_id):
    return "%swechat/incident_detail/%s/" % (
        settings.WECHAT_URL, incident_id)


def default_notify(verifier, cc_biz_id, alarm_type, alarm_count):
    biz_name = get_biz_name(cc_biz_id) or ("biz[%s]" % cc_biz_id)
    message = [
        _("[Fault Auto-recovery] [Convergence Notification]"),
        _("Business: %(biz_name)s", biz_name=biz_name),
        _("%(alarm_count)s %(alarm_desc)s alarms occurred within a certain period of time",
            alarm_count=alarm_count,
            alarm_desc=get_description_by_alarm_type(
                alarm_type,
                cc_biz_id=cc_biz_id,
                default=alarm_type,
            ))
    ]
    send.wechat(verifier, constants.WECHAT_BREAKS.join(message))

    mail_title = _("[Fault Auto-recovery Notification] Convergence %(biz_name)s", biz_name=biz_name)
    send.mail(verifier, constants.MAIL_BREAKS.join(message), title=mail_title)


def default_defense(verifier, cc_biz_id, alarm_type, alarm_count):
    description = get_description_by_alarm_type(
        alarm_type,
        cc_biz_id=cc_biz_id,
        default=alarm_type,
    )
    biz_name = get_biz_name(cc_biz_id)
    template = _("""Dear FTA user, hello, this is the notice of auto-recovery exception.
                %(biz_name)s appeared a batch %(description)s alarm(s), please confirm that after the approval 
                on WeChat whether to implement auto-recovery,
                If it is not convenient for you to hang up three times, please contact the next person in charge.
                Or contact other responsible person on their own after confirmation
                """, biz_name=biz_name, description=description)
    send.phone(
        verifier,
        template
    )
    wechat_lines = [
        _("[Fault Auto-recovery] [Convergence Error Defense]"),
        _("Business: %(biz_name)s", biz_name=biz_name),
        _("Alarm type: %(description)s", description=description),
        _("Batch alarm occurred, please approve whether to execute solution")
    ]
    send.wechat(verifier, constants.WECHAT_BREAKS.join(wechat_lines))


def default_collect(verifier, cc_biz_id_list, alarm_type_list,
                    alarm_count, incident_id):

    begin_time = session.query(FtaSolutionsAppIncident).filter_by(id=incident_id).one().begin_time

    # 结束时间为事件结束时间或者当前时间
    end_time = session.query(FtaSolutionsAppIncident)\
        .filter_by(id=incident_id).one().end_time or \
        arrow.utcnow().naive

    time_desc = get_time.get_time_range_desc(
        begin_time, end_time, breaks=constants.WECHAT_BREAKS)

    message = [
        _("[Fault Auto-recovery] [Convergence Summary]"),
        _("Business: %(biz_map)s", biz_map=','.join(map(get_biz_name, cc_biz_id_list))),
        _("Alarm type: %(alarm_type)s", alarm_type=','.join(alarm_type_list)),
        "%s" % time_desc,
        _("%(alarm_count)s alarm(s) appeared", alarm_count=alarm_count),
    ]
    if hasattr(settings, "WECHAT_URL"):
        message.append(_("Details %(incident_url)s", incident_url=_get_incident_url(incident_id)))
    send.wechat(verifier, constants.WECHAT_BREAKS.join(message))


def default_universality(alarm_instances, dimensions, related_event_list,
                         incident_id, re_universality):

    # 获取所有的通知人
    verifier = []
    for alarm_instance in alarm_instances:
        verifier.extend(people.get_verifier(alarm_instance['id']))
    verifier = list(set(verifier))

    begin_time = session.query(FtaSolutionsAppIncident)\
        .filter_by(id=incident_id).one().begin_time

    # 结束时间为事件结束时间或者当前时间
    end_time = session.query(FtaSolutionsAppIncident)\
        .filter_by(id=incident_id).one().end_time or \
        arrow.utcnow().naive

    time_desc = get_time.get_time_range_desc(
        begin_time, end_time, breaks=constants.WECHAT_BREAKS)

    biz_list = [get_biz_name(a["cc_biz_id"]) for a in alarm_instances]
    biz_name = ','.join(list(set(biz_list)))

    alarm_type_list = list(set([
        get_description_by_alarm_type(
            a['alarm_type'],
            cc_biz_id=a['cc_biz_id'],
            default=a['alarm_type'],
        )
        for a in alarm_instances]))

    lines = [
        _("[Fault Auto-recovery] [Common Alarm Cause Check]")
        if re_universality else
        _("[Fault Auto-recovery] [Convergence Commonality]"),
        _("Business: %(biz_name)s", biz_name=biz_name),
        _("Alarm type: %(alarm_type)s", alarm_type=','.join(alarm_type_list)),
        '%s' % time_desc,
        _("%(alarm_count)s alarm(s) appeared", alarm_count=len(alarm_instances)),
        _("'----- Common Alarm ----- "),
    ]

    # 维度信息
    dimension_line = []
    for dimension, dimension_counter_list in dimensions.items():
        dimension_name = constants.UNIVERSALITY_DIMENSION_KEY.get(dimension,
                                                                  dimension)
        dimension_desc = ["%s(%s%%)" % dimension_counter
                          for dimension_counter in dimension_counter_list]
        dimension_line.append("%s： %s" % (
            dimension_name, ",".join(dimension_desc)))
    lines.extend(dimension_line)

    # 相关事件信息
    # 有相关事件才append
    if related_event_list:
        lines.extend([_("----- Related Events -----")])
        lines.extend([u"%s: %s" % (e.event_type, e.event_title)
                      for e in related_event_list])

    if hasattr(settings, "WECHAT_URL"):
        lines.append(_("Details %(incident_url)s", incident_url=_get_incident_url(incident_id)))
    if dimension_line:
        pass
        # 暂不发给用户
        # send.wechat(verifier, constants.WECHAT_BREAKS.join(lines))


hook = hooks.HookManager("send_converge")
notify = hook.get("notify", default_notify)
defense = hook.get("defense", default_defense)
collect = hook.get("collect", default_collect)
universality = hook.get("universality", default_universality)
