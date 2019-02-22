# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

import arrow
from sqlalchemy import func

from fta import constants
from fta.advice.advice_fta import AdviceFtaManager
from fta.storage.mysql import session
from fta.storage.tables import (FtaSolutionsAppAdvice,
                                FtaSolutionsAppAlarminstance)
from fta.utils import logging
from fta.utils.i18n import _
from project.utils import query_cc

logger = logging.getLogger("advice")


def common_ip_handler(advicedef, check_time, alarm_type_condition):
    advice_list = common_handler(
        advicedef, check_time, alarm_type_condition, "ip")

    # ip_list = [advice['subject'] for advice in advice_list]

    def get_ip_info(app_id, ip):
        info = query_cc.get_cc_info_by_ip(cc_biz_id=app_id, ip=ip)
        return {
            'set_chn_name': info['cc_topo_set_name'] or info['cc_topo_set'],
            'app_module': info['cc_app_module_name'] or info['cc_app_module'],
            'state': info['cc_status'],
            'display_name': info['cc_biz_name']}

    def filter_state(advice):
        # 过滤掉运维已经介入处理的, 比如已经移动了模块，
        # 或者是进行了回收（业务变为Reborn）等等
        host_info = get_ip_info(advice['cc_biz_id'], advice['subject'])
        if host_info.get('state') in (u"--->开发使用中[无告警]", u"--->故障中"):
            logger.info('host_info %s state in [%s], just ignore.' % (host_info, u"--->开发使用中[无告警],--->故障中"))
            return False
        if host_info.get('display_name') == 'reborn':
            logger.info('host_info %s display_name == %s, just ignore.' % (host_info, 'reborn'))
            return False
        if host_info.get('app_module') == u"故障机":
            logger.info('host_info %s app_module == %s, just ignore.' % (host_info, u"故障机"))
            return False
        advice['host_info'] = host_info
        return True

    return [advice for advice in advice_list if save_advice(advice) and filter_state(advice)]


def common_world_handler(advicedef, check_time, alarm_type_condition):
    advice_list = common_handler(advicedef, check_time, alarm_type_condition, "cc_topo_set")
    return [advice for advice in advice_list if save_advice(advice)]


def common_handler(advicedef, check_time, alarm_type_condition, subject_key):
    start_time = arrow.get(check_time).replace(days=-1 * advicedef['interval']).format(constants.STD_ARROW_FORMAT)

    hit_ret = session.query(
        func.count(FtaSolutionsAppAlarminstance.id),
        FtaSolutionsAppAlarminstance.cc_biz_id,
        getattr(FtaSolutionsAppAlarminstance, subject_key),
        FtaSolutionsAppAlarminstance.id,
        FtaSolutionsAppAlarminstance.cc_topo_set,
        FtaSolutionsAppAlarminstance.cc_app_module).filter(
        FtaSolutionsAppAlarminstance.source_time >= start_time
    ).filter(
        FtaSolutionsAppAlarminstance.source_time <= check_time
    ).filter(
        FtaSolutionsAppAlarminstance.alarm_type.in_(alarm_type_condition)
    )
    if advicedef["cc_biz_id"]:
        hit_ret = hit_ret.filter(FtaSolutionsAppAlarminstance.cc_biz_id == advicedef["cc_biz_id"], )

    hit_ret = hit_ret.group_by(getattr(FtaSolutionsAppAlarminstance, subject_key), )
    return [{
        'advice_def_id': advicedef['id'],
        'alarm_num': i[0],
        'cc_biz_id': i[1],
        'subject': i[2],
        'alarminstance_id': i[3],
        'alarm_start_time': start_time,
        'alarm_end_time': check_time,
        'create_time': arrow.utcnow().naive,
        'status': 'fresh',
        'comment': json.dumps({'set_name': i[4], 'module_name': i[5]}),
    } for i in hit_ret if i[0] >= advicedef['threshold']]


def save_advice(advice):
    """7天内产生过相同的建议，就不重复产生。 返回true/false来表示是否保存"""
    comp_time = arrow.get(advice['create_time']).replace(days=-7).naive

    ret = session.query(FtaSolutionsAppAdvice).filter(
        FtaSolutionsAppAdvice.advice_def_id == advice['advice_def_id']
    ).filter(
        FtaSolutionsAppAdvice.cc_biz_id == advice['cc_biz_id']
    ).filter(
        FtaSolutionsAppAdvice.subject == advice['subject']
    ).filter(FtaSolutionsAppAdvice.create_time >= comp_time).count()

    if ret:
        logger.info("advice exists: %s" % str(advice))
        return False

    alarminstance_id = advice.pop('alarminstance_id')
    try:
        ad_result = session.execute(FtaSolutionsAppAdvice.__table__.insert(), advice)
        advice_id = ad_result.inserted_primary_key[0]
    except Exception as e:
        logger.exception("save advice exception: %s" % e)
        return False

    # 执行自愈预警操作
    try:
        advice['alarminstance_id'] = alarminstance_id
        advice['advice_id'] = advice_id
        advice_fta = AdviceFtaManager(advice)
        advice_fta.make_alarm_by_advice()
    except BaseException:
        logger.exception(_("Auto-recovery early warning error, advice: %s") % advice)

    return True
