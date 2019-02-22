# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta import constants
from fta.utils import logging
from fta.utils.i18n import i18n

logger = logging.getLogger("utils")


def get_time(minutes=None, delta_minutes=0, interval=-2):
    """minutes为指定当天的分钟数， delta为指定往回偏移的分钟数"""

    if minutes:
        end_time = arrow.utcnow().floor('day').replace(
            minutes=minutes - delta_minutes)
    else:
        end_time = arrow.utcnow().floor('minute').replace(
            minutes=delta_minutes * -1)

    begin_time = end_time.replace(minutes=interval)

    logger.info(
        "GET_TIME_VALUE %s minutes(%s)",
        begin_time,
        minutes or (begin_time - begin_time.floor('day')).seconds / 60)

    return (begin_time.format(constants.STD_ARROW_FORMAT),
            end_time.format(constants.STD_ARROW_FORMAT))


def get_time_range_desc(begin_time, end_time, breaks=u" ", to_local=True):
    """根据开始时间和结束时间来生成时间段的文字描述"""

    begin_time_obj = arrow.get(begin_time)
    end_time_obj = arrow.get(end_time)

    if to_local is True:
        timezone = i18n.get_timezone()

        begin_time_obj = begin_time_obj.to(timezone)
        end_time_obj = end_time_obj.to(timezone)

    begin_time_desc = begin_time_obj.format(constants.SIMPLE_ARROW_FORMAT)
    end_time_desc = end_time_obj.format(constants.SIMPLE_ARROW_FORMAT)

    if begin_time == end_time:
        time_desc = u"于 {}".format(begin_time_desc)
    else:
        time_desc = breaks.join([
            u"从 {}".format(begin_time_desc),
            u"到 {}".format(end_time_desc),
        ])
    return time_desc


def get_day_by_day(begin_date, end_date):
    begin = arrow.get(begin_date)
    end = arrow.get(end_date)
    date_list = []
    while begin <= end:
        date_list.append(begin.format("YYYY-MM-DD"))
        begin = begin.replace(days=1)
    return date_list
