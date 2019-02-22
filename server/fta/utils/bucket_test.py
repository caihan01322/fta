# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import functools

from fta import settings


class check_env(object):
    """
    A decorator use for bucket test

    >>> @check_env(env="PRODUCT")
    >>> def func(args):
    >>>     return None

    only PRODUCT env will exec this func
    other env will return args
    """

    def __init__(self, env):
        self.env = env

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(arg):
            if self.env == settings.ENV:
                return task_definition(arg)
            else:
                return arg
        return wrapper


@check_env("PRODUCT")
def filter_tnm_alarm(tnm_alarm_list):
    """灰度测试告警"""
    # 16.02.04 现在暂时没用了，需要灰度的时候才会用到 by admin
    # 灰度测试阶段的白名单，只有在灰度测试中的业务才push出去
    GREY_RELEASE_BIZ = [u'CC_蓝鲸']
    return [
        a for a in tnm_alarm_list
        if a['service'].upper() in GREY_RELEASE_BIZ]
