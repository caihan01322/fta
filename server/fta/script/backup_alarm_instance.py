# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import argparse
import datetime
import os.path
import sys
from itertools import groupby

from sqlalchemy import TEXT, Column, MetaData, Table, create_engine
from sqlalchemy.orm import sessionmaker

from fta import settings
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import logging
from fta.utils.decorator import redis_lock

"""备份数据脚本
1, 可以分表备份
2, 自动创建表，分表
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


logger = logging.getLogger("root")

backup_engine = create_engine(
    'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (
        settings.BACKUP_MYSQL_USER, settings.BACKUP_MYSQL_PASSWORD,
        settings.BACKUP_MYSQL_HOST, settings.BACKUP_MYSQL_PORT, settings.BACKUP_MYSQL_NAME),
    pool_recycle=30)
BackupSession = sessionmaker(bind=backup_engine)
backup_session = BackupSession(autoflush=True, expire_on_commit=True, autocommit=True)
meta = MetaData()


def get_table(partitioning_key=None):
    # 维护表字段
    fix_columns = {
        'raw': Column('raw', TEXT, nullable=False),
        'tnm_alarm': Column('tnm_alarm', TEXT),
        'comment': Column('comment', TEXT),
        'snap_alarm_def': Column('snap_alarm_def', TEXT),
        'snap_solution': Column('snap_solution', TEXT),
        'origin_alarm': Column('origin_alarm', TEXT),

    }

    # 获取原来表字段
    base_columns = dict((column.name, column.copy()) for column in FtaSolutionsAppAlarminstance.__table__.columns)
    base_columns.update(fix_columns)
    if partitioning_key:
        table_name = '%s-%s' % (FtaSolutionsAppAlarminstance.__tablename__, partitioning_key)
    else:
        table_name = FtaSolutionsAppAlarminstance.__tablename__

    # 动态创建表
    table = Table(
        table_name,
        meta,
        *base_columns.values()
    )
    if not table.exists(bind=backup_engine):
        table.create(bind=backup_engine)

    return table


def get_query(days=90, max_alarm_id=None):
    """获取监控数据
    """
    if max_alarm_id:
        query = session.query(FtaSolutionsAppAlarminstance).filter(FtaSolutionsAppAlarminstance.id < max_alarm_id)
    else:
        now = datetime.datetime.now()
        begin_time = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d 00:00:00')
        query = session.query(FtaSolutionsAppAlarminstance).filter(
            FtaSolutionsAppAlarminstance.begin_time < begin_time)
    return query


def bulk_insert(table, data):
    """
    批量插入
    注意不能全量插入，否则myql报max_allowed_packet错误
    """
    bucket = 150  # 每次插入150条数据
    num = len(data)
    count = 1
    while num > 0:
        bucket_data = data[bucket * (count - 1): bucket * count]

        logger.info('[%s] try bulk insert %s data...' % (table.name, len(bucket_data)))
        result = backup_session.execute(table.insert().prefix_with("IGNORE"), bucket_data)
        logger.info('[%s] bulk insert %s success' % (table.name, result.rowcount))

        num -= bucket
        count += 1


@redis_lock('fta::backup_data::delete', 60 * 60)
def delete_data(query):
    """删除数据
    """
    table_name = FtaSolutionsAppAlarminstance.__tablename__

    logger.info('[%s] try delete %s data...' % (table_name, len(query.count())))
    result = query.delete()
    logger.info('[%s] delete %s success' % (table_name, result.rowcount))


@redis_lock('fta::backup_data::partitioning', 60 * 60)
def backup_data_partitioning(query):
    """分表备份数据
    """
    result = orm_2_dict(query)
    for partitioning_key, data in groupby(sorted(result, key=lambda x: x['begin_time'].strftime('%Y%m%d')),
                                          key=lambda x: x['begin_time'].strftime('%Y%m%d')):

        table = get_table(partitioning_key)
        data = list(data)
        bulk_insert(table, data)


@redis_lock('fta::backup_data::raw', 60 * 60)
def backup_data(query):
    """直接备份数据
    """
    data = orm_2_dict(query)
    table = get_table()

    bulk_insert(table, data)


def main(args):
    table_name = FtaSolutionsAppAlarminstance.__tablename__

    query = get_query(days=args.days, max_alarm_id=args.max_alarm_id)
    logger.info('get %s data from %s' % (query.count(), table_name))
    if args.backup:
        backup_data(query)
    if args.backup_partitioning:
        backup_data_partitioning(query)
    if args.delete:
        delete_data(query)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup fta_solutions_app_alarminstance')
    parser.add_argument("-a", "--days", type=int, default=90)
    parser.add_argument("-i", "--max_alarm_id", type=int, default=None)

    parser.add_argument('-b', '--backup', action='store_true', help='backup data from alarminstance')
    parser.add_argument('-p', '--backup_partitioning', action='store_true',
                        help='backup data from alarminstance by day')
    parser.add_argument('-d', '--delete', action='store_true', help='delete data from alarminstance')
    args = parser.parse_args()

    try:
        main(args)
    except Exception:
        logger.exception('backup error')
        sys.exit(1)
