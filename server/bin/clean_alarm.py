#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import datetime
import logging
import os.path
import sys

from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppAlarminstance

"""清理数据
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


# 日志配置
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    level='DEBUG'
)
logger = logging.getLogger("fta")


def query_yes_no(question, default=None):
    """删除确认
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def get_query(days=90, max_alarm_id=None):
    """获取监控数据
    """
    if max_alarm_id:
        logger.info('try get data where ID < %s' % max_alarm_id)
        query = session.query(FtaSolutionsAppAlarminstance).filter(FtaSolutionsAppAlarminstance.id < max_alarm_id)
    else:
        now = datetime.datetime.utcnow()
        begin_time = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d 00:00:00')
        logger.info('try get data where source_time < %s, %s days from now.' % (begin_time, days))
        query = session.query(FtaSolutionsAppAlarminstance).filter(
            FtaSolutionsAppAlarminstance.source_time < begin_time)
    return query


def delete_data(query):
    """删除数据
    """
    table_name = FtaSolutionsAppAlarminstance.__tablename__
    count = query.count()
    if count == 0:
        logger.info("no data to clean, quit.")
        return

    if query_yes_no("Please Confire to delete", "no"):
        logger.info('[%s] try clean %s data...' % (table_name, count))
        query.delete()
        logger.info('[%s] clean data success' % (table_name))
    else:
        logger.info('[%s] clean data canceled' % (table_name))


def main(args):
    if not args.delete:
        logger.info("Please choice action: --delete")
        return

    table_name = FtaSolutionsAppAlarminstance.__tablename__

    query = get_query(days=args.days, max_alarm_id=args.max_alarm_id)
    logger.info('get %s data from %s' % (query.count(), table_name))
    if args.delete:
        delete_data(query)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup fta_solutions_app_alarminstance')
    parser.add_argument(
        "-a", "--days", type=int, default=90,
        help="Data cleaned by date, sooner than specified time will be cleaned, default 90 days"
    )
    parser.add_argument(
        "-i", "--max_alarm_id", type=int, default=None,
        help="Cleans data by database ID, less than specified ID will be cleaned"
    )
    parser.add_argument('-d', '--delete', action='store_true', help='delete data from alarminstance')
    args = parser.parse_args()

    try:
        main(args)
    except Exception:
        logger.exception('clean data error')
        sys.exit(1)
