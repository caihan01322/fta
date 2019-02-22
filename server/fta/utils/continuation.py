# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta import settings
from fta.storage.cache import Cache, RedisIndexException
from fta.storage.queue import MessageQueue
from fta.utils import extended_json as json
from fta.utils import get_random_id, logging, scheduler

logger = logging.getLogger("job")

callback_cache = Cache("callback")

JOB_QUEUE = MessageQueue("beanstalkd", settings.QUEUE_JOB)

ESB_TIMEOUT = 14 * 24 * 60 * 60


class WaitCallback(Exception):
    pass


def get_callback_key(esb_id):
    return "callback_%s" % esb_id


def get_callback_info(esb_id, **kwargs):
    for redis_index in range(len(callback_cache.redis_conf)):
        try:
            json_job_info = callback_cache.set_index(redis_index)\
                .get(get_callback_key(esb_id))
        except RedisIndexException:
            continue
        if json_job_info:
            logger.info("esb_id callback_info %s: %s | kwargs: %s",
                        esb_id, json_job_info, kwargs)
            job_info = json.loads(json_job_info)
            job_info.update(kwargs)
            return job_info
    raise Exception("esb_id callback_info %s: None" % esb_id)


def wait_esb_callback(instance_id, node_idx, run_times,
                      callback_module, callback_func,
                      esb_id):
    job_info = json.dumps({
        "instance_id": instance_id,
        "node_idx": node_idx,
        "run_times": run_times,
        "callback_module": callback_module,
        "callback_func": callback_func,
    })
    callback_cache.set(get_callback_key(esb_id), job_info, ESB_TIMEOUT)


def wait_polling_callback(instance_id, node_idx, run_times,
                          callback_module, callback_func,
                          url, kwargs={}, delta_seconds=0):
    kwargs["url"] = url
    scheduler.poll(
        module="fta.utils.continuation",
        function="put_result_to_job_queue",
        args=(
            instance_id,
            node_idx,
            run_times,
            callback_module,
            callback_func,
        ),
        kwargs=kwargs,
        delta_seconds=delta_seconds)


def wait_callback(instance_id, node_idx, run_times,
                  callback_module, callback_func,
                  kwargs={}, delta_seconds=0):
    put_result_to_job_queue(instance_id, node_idx, run_times,
                            callback_module, callback_func,
                            delta_seconds=delta_seconds, **kwargs)


def put_result_to_job_queue(instance_id, node_idx, run_times,
                            callback_module, callback_func,
                            id_=None, delta_seconds=0, **kwargs):
    job_info = json.dumps({
        "id": id_ or get_random_id(),
        "instance_id": instance_id,
        "node_idx": node_idx,
        "run_times": run_times,
        "module": callback_module,
        "function": callback_func,
        "kwargs": kwargs,
    })
    logger.info(
        "$%s &%s put into job queue delay(%s): %s",
        instance_id, node_idx, delta_seconds, job_info)
    JOB_QUEUE.put(job_info, delay=int(delta_seconds))


if __name__ == '__main__':
    instance_id = 'lie'
    node_idx = 0
    run_times = 0
    callback_module = 'project.test'
    callback_func = 'test_joe'
    kwargs = 0
    delta_seconds = 10
    wait_callback(instance_id, node_idx, run_times, callback_module, callback_func, kwargs, delta_seconds)
