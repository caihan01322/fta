# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import hashlib
from itertools import product

import arrow

from fta.storage import tables
from fta.storage.cache import Cache
from fta.storage.mysql import session
from fta.utils import logging

ARCHIVE_KEY_PREFIX = "unmatch_alarm"
PRODUCT_DIMENSIONS = ["alarm_type", "module_name", "set_name"]

redis = Cache("dimension")
logger = logging.getLogger(__name__)


def clean_alarm(alarm):
    match_info = alarm.get("_match_info")
    if not match_info:
        return None

    cleaned_alarm = {
        "cc_biz_id": match_info.get("cc_biz_id"),
        "company_id": match_info.get("cc_company_id"),
        "plat_id": match_info.get("cc_plat_id"),
        "module_name": match_info.get("cc_app_module", []),
        "set_name": match_info.get("cc_topo_set", []),
        "alarm_type": match_info.get("alarm_type", []),
        "source_type": match_info.get("source_type"),
        "alarm_time": match_info.get("alarm_time"),
        "raw_alarm_type": alarm.get("alarm_type"),
    }
    return cleaned_alarm


def get_archive_key(cc_biz_id, alarm_type, module_name, set_name):
    raw_key = "%s/%s/%s/%s" % (cc_biz_id, alarm_type, module_name, set_name)
    hash_key = hashlib.sha1(raw_key).hexdigest()
    return "%s:%s" % (ARCHIVE_KEY_PREFIX, hash_key)


def gen_dimensions_by_alarm(alarm):
    product_set = [set(alarm[k]) for k in PRODUCT_DIMENSIONS]
    for i in product_set:
        if not i:
            # append empty string for product
            i.add("")
    for parts in product(*product_set):
        yield dict(zip(PRODUCT_DIMENSIONS, parts))


def update_archive_by_alarm(dimensions, alarm):
    key = get_archive_key(alarm.get("cc_biz_id"), *dimensions.values())
    result = redis.hincrby(key, "sub_count")
    if result > 1:
        return
    # for the archive which is empty
    # expires more than a day
    redis.expire(key, 60 * 60 * 25)
    for k, v in dimensions.items():
        redis.hset(key, k, v)

    for k in alarm.viewkeys() - dimensions.viewkeys():
        redis.hset(key, k, alarm[k])


def persist_archive_by_key(key):
    cached_archive = redis.hgetall(key)
    sub_count = int(cached_archive.get("sub_count", 0))
    ident_params = {
        "cc_biz_id": cached_archive.get("cc_biz_id"),
        "alarm_type": cached_archive.get("alarm_type"),
        "cc_module": cached_archive.get("module_name"),
        "cc_set_name": cached_archive.get("set_name"),
    }
    archive = session.query(tables.FtaSolutionsAppOutofscopearchive).filter_by(**ident_params).first()
    now = arrow.now()
    if not archive:
        archive = tables.FtaSolutionsAppOutofscopearchive(
            status="new", sub_count=0, extra="{}",
            created_on=now.naive, updated_on=now.naive,
            **ident_params
        )
        session.add(archive)
    if archive.status in ["new", "suggest"]:
        session.query(tables.FtaSolutionsAppOutofscopearchive).filter(
            tables.FtaSolutionsAppOutofscopearchive.id == archive.id,
        ).update({
            "sub_count": tables.FtaSolutionsAppOutofscopearchive.sub_count + sub_count,
            "updated_on": now.naive,
        })
    redis.expire(key, 0)  # delete cached data when persist sucess


def persist_cached_archives():
    keys = redis.keys("%s*" % ARCHIVE_KEY_PREFIX)
    with session.no_autoflush:
        for key in keys:
            try:
                persist_archive_by_key(key)
            except Exception as err:
                logger.exception(err)
    session.flush()


def unmatch_alarm_hook(alarm):
    cleaned_alarm = clean_alarm(alarm)
    if not cleaned_alarm:
        return None
    cc_biz_id = int(cleaned_alarm.get("cc_biz_id") or 0)
    if not cc_biz_id:
        return None
    for dimensions in gen_dimensions_by_alarm(cleaned_alarm):
        try:
            update_archive_by_alarm(dimensions, cleaned_alarm)
        except Exception as err:
            logger.exception("unmatched alarm handle failed: biz[%s], %s", cc_biz_id, err, )
    logger.info("got an unmatched alarm fo biz[%s]", cc_biz_id, )
