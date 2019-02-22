# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import absolute_import

import hashlib
import hmac
import random
import string
import time
import urlparse
from functools import wraps
from urllib import urlencode
from urllib2 import urlopen


def signer(_func):
    """signature urlopen
    """

    @wraps(_func)
    def _wrapped_view(url, data=None, app_secret='', **kwargs):

        # 生成签名参数
        _request = urlparse.urlparse(url)
        query = dict(urlparse.parse_qsl(_request.query))
        query['Nonce'] = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])
        query['Timestamp'] = int(time.time())
        if not data:
            method = 'GET'
            _query = '&'.join('%s=%s' % (key, value) for key, value in sorted(query.items()))
        else:
            method = 'POST'
            query['Data'] = data
            _query = '&'.join('%s=%s' % (key, value) for key, value in sorted(query.items()))
            query.pop('Data', None)

        # 签名
        raw_msg = '%s%s%s?%s' % (method, _request.netloc, _request.path, _query)
        signature = hmac.new(app_secret, raw_msg, hashlib.sha256).hexdigest()
        query['Signature'] = signature
        query = urlencode(query)
        # 带上签名参数
        url = '%s://%s%s?%s' % (_request.scheme, _request.netloc, _request.path, query)
        return _func(url, data, **kwargs)
    return _wrapped_view


signed_urlopen = signer(urlopen)
