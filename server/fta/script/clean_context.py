# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
删除根据更新时间删除Context表中老的context
天数作为参数传入, 比如传入15, 则删除15天以前的数据

python -m script.clean_context 15
"""

import sys

import arrow

from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppContext
from fta.utils import logging

logger = logging.getLogger('root')

MIN_CLEAN_DAY = 15


def clean_context(end_time):
    num = session.query(FtaSolutionsAppContext).filter(
        FtaSolutionsAppContext.updated_on <= end_time).delete()
    logger.info("Delete %s context records which updated_on less than %s" % (
        num, end_time))


def main():
    try:
        clean_day = sys.argv[1]
        if clean_day < MIN_CLEAN_DAY:
            clean_day = MIN_CLEAN_DAY
    except BaseException:
        clean_day = MIN_CLEAN_DAY

    end_day = arrow.utcnow().replace(days=-1 * clean_day).naive
    clean_context(end_day)


if __name__ == '__main__':
    main()
