# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import re
import arrow
import socket
import random
import hashlib
import itertools
import json


def is_ip(ci_name):
    try:
        socket.inet_aton(ci_name)
        return True
    except BaseException:
        return False


def get_local_ip():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.

    stackoverflow上有人说用socket.gethostbyname(socket.getfqdn())
    但实测后发现有些机器会返回127.0.0.1
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def get_first(objs, default=""):
    """get the first element in a list or get blank"""
    if len(objs) > 0:
        return objs[0]
    return default


def get_list(obj):
    return obj if isinstance(obj, list) else [obj]


def split_list(raw_string):
    if isinstance(raw_string, (list, set)):
        return raw_string
    re_obj = re.compile(r'\s*[;,]\s*')
    return filter(lambda x: x, re_obj.split(raw_string))


def expand_list(obj_list):
    return list(itertools.chain.from_iterable(obj_list))


def remove_blank(objs):
    if isinstance(objs, (list, set)):
        return [unicode(obj) for obj in objs if obj]
    return objs


def remove_tag(text):
    """去除 html 标签"""
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)


def get_random_id():
    return "%s%s" % (arrow.utcnow().timestamp, random.randint(1000, 9999))


def _count_md5(content):
    if content is None:
        return None
    m2 = hashlib.md5()
    if isinstance(content, unicode):
        m2.update(content.encode("utf8"))
    else:
        m2.update(content)
    return m2.hexdigest()


def get_md5(content):
    if isinstance(content, list):
        return [_count_md5(c) for c in content]
    else:
        return _count_md5(content)


def is_ja_new_performance_alarm(alarm):
    """判断一个告警是不是JA基础性能告警"""
    try:
        origin_alarm = json.loads(alarm["origin_alarm"])
        if origin_alarm.get("scenario") == "performance":
            return True
    except Exception:
        if isinstance(alarm, dict):
            return alarm.get('scenario') == 'performance'
    return False
