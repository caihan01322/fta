# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import os

from fta.storage.cache import Cache
from fta.storage.mysql import session
from fta.storage.tables import (FtaSolutionsAppAlarminstance,
                                FtaSolutionsAppAlarminstancelog)
from fta.utils import (alarm_instance, get_list, get_local_ip, instance_log,
                       logging, remove_blank)
from fta.utils.context import Context

redis_cache = Cache('redis')

IP = get_local_ip()


class LockError(Exception):
    pass


class PassEmpty(Exception):
    pass


def redis_lock(key, timeout=60 * 60 * 12, extend=False):
    """should use mysql lock in important process

    :return bool: True means get lock success
                  False means get lock failure
    """
    result = redis_cache.set(key, "__lock__", timeout, nx=True)
    if extend:
        redis_cache.expire(key, timeout)
    return result


def redis_unlock(key):
    """should use mysql lock in important process

    :return bool: True means get lock success
                  False means get lock failure
    """
    redis_cache.delete(key)


def lock_collect_alarm(event_id):
    if not redis_lock("--collect:%s--" % event_id):
        raise LockError("collect: %s pass" % event_id)


def lock_alarm_instance(event_id, from_status_list, to_status):
    task_id = "%s:%s" % (IP, os.getpid())
    for from_status in get_list(from_status_list):
        if session.query(FtaSolutionsAppAlarminstance) \
                .filter_by(event_id=event_id, status=from_status) \
                .update({"status": to_status, "bpm_task_id": task_id}):
            return from_status
    raise LockError("event_id: %s pass" % event_id)


def lock_alarm_instance_node(event_id, node_id=None, job_id=None):
    instance_id = alarm_instance.get_alarm_instance(event_id=event_id)["id"]

    # if "event_id" ~"node_id" ~"job_id"
    if not node_id:
        return instance_log.update_alarm_instance_comment(
            instance_id, "", "node_path", logging.DEBUG, cover=False)

    node_desc_list = [node_id] + remove_blank([
        Context(instance_id).RUN_TIMES, job_id])
    node_desc = "=" + ":".join(map(str, node_desc_list)) + "=>"

    while True:

        node = session.query(
            FtaSolutionsAppAlarminstancelog,
        ).filter_by(
            alarm_instance_id=instance_id,
            step_name="node_path",
            level=logging.DEBUG,
        ).first()

        if node:
            node_path = node.content
        else:
            node_path = ""
            instance_log.update_alarm_instance_comment(
                instance_id, node_path, "node_path",
                logging.DEBUG, cover=False,
            )

        if node_desc in node_path:
            raise LockError("$%s node: %s pass %s" % (
                instance_id, node_desc, node_path))

        if session.query(FtaSolutionsAppAlarminstancelog).filter_by(
            alarm_instance_id=instance_id,
            step_name="node_path",
            level=logging.DEBUG,
            content=node_path,
        ).update({"content": node_path + node_desc}):
            break
