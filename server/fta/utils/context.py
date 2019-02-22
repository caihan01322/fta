# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow
from sqlalchemy.exc import IntegrityError

from fta.storage.cache import Cache
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppContext
from fta.utils import extended_json as json
from fta.utils import logging

logger = logging.getLogger("job")

callback_cache = Cache("callback")


class ContextAcquireException(Exception):
    pass


class ContextMysqlBackend(object):

    """MySQL Backend of Context"""

    def load_key(self, key, field):
        try:
            return session.query(FtaSolutionsAppContext)\
                .filter_by(key=key).filter_by(field=field).one().value
        except BaseException:
            return None

    def load(self, key):
        contexts = session.query(FtaSolutionsAppContext).filter_by(key=key)
        return {context.field: context.value for context in contexts}

    def dump_key(self, key, field, value):
        try:
            session.execute(
                FtaSolutionsAppContext.__table__.insert(),
                [{"key": key, "field": field, "value": value,
                  "updated_on": arrow.utcnow().naive,
                  "created_on": arrow.utcnow().naive}])
        except IntegrityError:
            session.query(FtaSolutionsAppContext)\
                .filter_by(key=key).filter_by(field=field)\
                .update({"value": value,
                         "updated_on": arrow.utcnow().naive})

    def dump(self, key, context):
        for field, value in context.items():
            self.dump_key(key, field, value)

    def expire(self, key, timeout):
        pass

    def acquire(self, key, field, from_value, to_value):
        if not session.query(
            FtaSolutionsAppContext,
        ).filter_by(
            key=key, field=field, value=json.dumps(from_value),
        ).update({
            "value": json.dumps(to_value),
        }):
            raise ContextAcquireException(
                "Context %s.%s from(%s) to (%s) failed" % (
                    key, field, from_value, to_value,
                ),
            )


class ContextRedisBackend(object):

    def __init__(self, redis):
        self.redis = redis
        self.load = redis.hgetall
        self.load_key = redis.hget
        self.dump = redis.hmset
        self.dump_key = redis.hset
        self.expire = redis.expire

    def acquire(self, key, field, from_value, to_value):
        raise ContextAcquireException("Context redis-backend can't acquire")
        # self.dump_key(field, to_value)


CONTEXT_MYSQL_BACKEND = ContextMysqlBackend()
CONTEXT_REDIS_BACKEND = ContextRedisBackend(callback_cache)


class Context(object):

    """
    Managing  context of an obj(usually is an alarm solution)

    Usage:

        # process1 begin

        class ContextChild(Context):
            def run(self):
                self.a = 1

        c = ContextChild("uniq_id")
        assert not hasattr(c, "a")
        c.run()
        assert c.a == 1

        # process1 end

        ---------------------

        # new process2 begin

        c = context("uniq_id")
        assert c.a == 1

        # new process2 end
    """

    def __init__(self, instance_id=None, prefix="", postfix="",
                 backend=CONTEXT_MYSQL_BACKEND):
        self._backend = backend
        self._prefix = prefix
        self._postfix = postfix
        if instance_id is None:
            self._context = {}
        else:
            self._instance_id = instance_id
            self._context = self._load()

    @property
    def _key(self):
        """
            get key based on prefix, instance_id and postfix
        """
        return "_".join(filter(lambda x: x, map(str, [
            self._prefix, self._instance_id, self._postfix])))

    def _acquire(self, field, from_value, to_value):
        """modify a field's value"""
        if field in self._context:
            self._backend.acquire(self._key, field, from_value, to_value)
        self._context[field] = to_value

    def _load(self):
        """get all context of current obj from backend"""
        context = self._backend.load(self._key)
        return {k: json.loads(v) for k, v in context.items()}

    def _load_key(self, key):
        """get value by field"""
        return json.loads(self._backend.load_key(self._key, key) or "null")

    def _dump(self):
        """save all context of current obj to backend"""
        context = {k: json.dumps(v) for k, v in self._context.items()}
        self._backend.dump(self._key, context)
        self._backend.expire(self._key, 60 * 60 * 24)

    def _dump_key(self, key):
        """save value by field"""
        self._backend.dump_key(self._key, key, json.dumps(self._context[key]))
        self._backend.expire(self._key, 60 * 60 * 24)

    def _clear(self):
        """caution! delete all context of current obj"""
        self._context = {}
        self._dump()

    def __getattr__(self, item):
        if not item.startswith("_"):
            return self[item]

    def __setattr__(self, item, value):
        if item.startswith("_"):
            super(Context, self).__setattr__(item, value)
        else:
            self[item] = value

    def __getitem__(self, item):
        return self._context.get(item)

    def __setitem__(self, item, value):
        self._context[item] = value
        self._dump_key(item)
