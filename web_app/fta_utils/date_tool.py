# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from datetime import datetime

import arrow
from django.utils import timezone


def get_date_range(from_date=None, to_date=None):
    """获取一段时间中的每一个date"""
    # 先把时间转为带时区的时间
    current_tz = timezone.get_current_timezone()
    if not isinstance(from_date, arrow.Arrow):
        from_date = arrow.Arrow.fromdate(from_date, current_tz)
    if not isinstance(to_date, arrow.Arrow):
        to_date = arrow.Arrow.fromdate(to_date, current_tz)
    # the first day we stored the alarms
    from_date = from_date or arrow.get(2014, 3, 1)
    to_date = to_date or arrow.now().floor('day')
    for day in arrow.Arrow.range('day', from_date, to_date):
        yield day.date()


def get_datetime_range(day):
    """获取一天的头和尾"""
    start, end = arrow.Arrow.fromdate(day).span('day')
    return (start.naive, end.naive)


def try_parse_datetime(dt, is_strat=False):
    '''Return datetime from string or None
    '''
    try:
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except Exception:
            if is_strat:
                dt = "%s 00:00:00" % dt
            else:
                dt = "%s 23:59:59" % dt
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

        # from native time to local time
        current_tz = timezone.get_current_timezone()
        dt = current_tz.localize(dt)
        return dt
    except (TypeError, ValueError):
        pass

    return
