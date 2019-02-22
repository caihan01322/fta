# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import functools
import sys
import time
import traceback

from flask import request
from fta.utils import extended_json, get_local_ip, logging

logger = logging.getLogger("webserver")


def api(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return_value = func(*args, **kwargs)
        except Exception as e:
            _, _, tb = sys.exc_info()
            filepath, lineno, _, _ = traceback.extract_tb(tb)[-1]
            filename = filepath.split("/")[-1].split(".")[0]
            result = {"result": False,
                      "data": None,
                      "message": u"%s@%s: %s" % (filename, get_local_ip(), e),
                      "code": str(lineno)}
            logger.warning(result)
        else:
            result = {"result": True,
                      "data": return_value,
                      "message": "",
                      "code": "0"}
        return extended_json.dumps(result)
    return wrapper


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        beg_ts = time.time()
        status = "SUCCESS"
        try:
            return_value = func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            status = u"ERROR: %s" % e
        cost_ts = time.time() - beg_ts
        log_info = "WEBSERVER %s %s %s %s %s" % (
            request.method, request.url, cost_ts, status,
            request.get_data() or request.form)
        if status != "SUCCESS":
            logger.warning(log_info)
            raise Exception(status)
        else:
            logger.info(log_info)
            return return_value
    return wrapper
