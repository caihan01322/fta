# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from __future__ import absolute_import

import json
import logging
import traceback

import arrow

from fta import settings, utils

LOCAL_IP = utils.get_local_ip()
ENABLE_REDIS_HANDLER = getattr(settings, "ENABLE_REDIS_HANDLER", False)


class RedisHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self._redis_client = None

    @property
    def redis_client(self):
        if not self._redis_client:
            from fta.storage.cache import Cache
            self._redis_client = Cache("log")
        return self._redis_client

    def emit(self, record):
        try:
            self._emit(record)
        except BaseException:
            print "WRITE LOG FAILURE"

    def _emit(self, record):
        if not ENABLE_REDIS_HANDLER:
            return
        if self.redis_client is None:
            print "WRITE LOG TO REDIS ERROR: REDIS GONE"
            return
        if self.redis_client.llen("logs") >= settings.REDIS_MAXLOG:
            print "WRITE LOG TO REDIS ERROR: REDIS FULL"
            return
        if record.exc_info:
            exc_lines = ''.join(traceback.format_exception(*record.exc_info))
        else:
            exc_lines = ""
        record_dict = {
            'ip': LOCAL_IP,
            'created': arrow.utcnow().isoformat(),
            'exc_info': exc_lines,
            'filename': record.filename,
            'funcname': record.funcName,
            'level': record.levelno,
            'lineno': record.lineno,
            'module': record.module,
            'msecs': record.msecs,
            'message': record.getMessage(),
            'logger': record.name,
            'pathname': record.pathname,
            'process': record.process,
            'processname': record.processName,
            'relativecreated': record.relativeCreated,
            'thread': record.thread,
            'threadname': record.threadName,
        }
        try:
            self.redis_client.lpush("logs", json.dumps(record_dict))
        except Exception as e:
            print "WRITE LOG TO REDIS ERROR: %s" % str(e)
