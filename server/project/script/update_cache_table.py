# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import copy
import datetime
import json
import sys

import arrow
from sqlalchemy import func

from fta import constants
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import (FtaSolutionsAppAlarmdef,
                                FtaSolutionsAppAlarminstance,
                                FtaSolutionsAppAlarminstancearchive,
                                FtaSolutionsAppConf,
                                FtaSolutionsAppDatachanglog,
                                FtaSolutionsAppKpicache)
from fta.utils import get_time, logging
from fta.utils.decorator import redis_lock
from fta.utils.func_timer import time_limiter

logger = logging.getLogger("root")


class AlarmInstanceArchive(object):
    DEFAULT_PROFIT = 15 * 60  # 每个告警的平均人工处理时间：15分钟
    # 根据自研组的经验得出 (实际上需要加上至少半个小时的人工时间)
    MANUAL_CONSUME = {
        'agent': 1.45 * 60 * 60,
        'clock-unsync': DEFAULT_PROFIT,
        'core-dumped': DEFAULT_PROFIT,
        'cpu-high': DEFAULT_PROFIT,
        'customized': DEFAULT_PROFIT,
        'disk-full': DEFAULT_PROFIT,
        'disk-readonly': 1.7 * 60 * 60,
        'disk-readonly-full': DEFAULT_PROFIT,
        'leaf-biz-watchman': DEFAULT_PROFIT,
        'JungleAlert': DEFAULT_PROFIT,
        'memory-full': DEFAULT_PROFIT,
        'online': DEFAULT_PROFIT,
        'os-restart': 0.86 * 60 * 60,
        'ping': 1.06 * 60 * 60,
        'port-missing': DEFAULT_PROFIT,
        'process-missing': DEFAULT_PROFIT,
        'raid': DEFAULT_PROFIT
    }

    # 统计维度
    DEFAULT_SUB = {
        "sub_count": 0,  # 总告警数
        "sub_consumed": 0,  # 总执行时间
        "sub_profit": 0  # 总收益时间
    }

    def __init__(self):
        self.result = {}  # 统计信息 {archive_id: DEFAULT_SUB}

    def calc(self, from_date, end_date):
        dba_def = session.query(FtaSolutionsAppAlarmdef.id) \
            .filter_by(category="DBA").all()
        dba_def_id = [d[0] for d in dba_def]
        logger.info("DBADEF_ID %s", dba_def_id)
        # 只算已经结束了的, 对于没有end_time的应该定期清理分析
        # 同时去掉DBA告警，因为普通运维并不关注
        from_time = arrow.get(from_date).floor("day").naive
        end_time = arrow.get(end_date).ceil("day").naive
        history = session.query(FtaSolutionsAppAlarminstance).filter(
            FtaSolutionsAppAlarminstance.source_time >= from_time,
            FtaSolutionsAppAlarminstance.source_time <= end_time,
            FtaSolutionsAppAlarminstance.end_time,
            ~FtaSolutionsAppAlarminstance.alarm_def_id.in_(dba_def_id))

        logger.info(
            "Count History %s: %s TO %s", history.count(), from_time, end_time)

        # 累计单条告警的信息到 result
        for ai in history:
            rec_id = self.get_rec_id(ai)
            self.update_result(rec_id, ai)

        # 将 result 中的统计数据更新到数据库
        for id_, value in self.result.items():
            session.query(FtaSolutionsAppAlarminstancearchive).filter_by(id=id_).update(value)
            logger.info("AlarmInstanceArchive update: %s: %s", id_, value)
        session.query(FtaSolutionsAppAlarminstancearchive).filter(
            FtaSolutionsAppAlarminstancearchive.date >= from_date
        ).filter(
            FtaSolutionsAppAlarminstancearchive.date <= end_date
        ).filter(
            ~FtaSolutionsAppAlarminstancearchive.id.in_(self.result.keys())
        ).update(self.DEFAULT_SUB, synchronize_session="fetch")

    def update_result(self, rec_id, ai):
        """将单条告警的数据统计到 result 里"""
        # 获取执行耗时
        consumed = max((ai.end_time - ai.begin_time).total_seconds(), 1)

        # 获取节省时间
        orig_consume = self.MANUAL_CONSUME.get(
            ai.alarm_type, self.DEFAULT_PROFIT)
        profit = 0
        if ai.solution_type not in (None, 'collect', 'sleep') and ai.status in (
                'success', 'almost_success') and consumed < orig_consume:
            profit = orig_consume - consumed

        self.result[rec_id] = self.result.get(rec_id) or copy.deepcopy(self.DEFAULT_SUB)
        self.result[rec_id]["sub_count"] += 1
        self.result[rec_id]["sub_consumed"] += consumed
        self.result[rec_id]["sub_profit"] += profit
        # logger.info("AlarmInstanceArchive RESULT: %s", self.result)

    def get_query_dict(self, ai):
        """获取单条告警的统计维度字典"""
        # 防止一些旧老脏数据导致异常
        eff_time = ai.source_time or ai.begin_time or ai.end_time
        is_success = ai.status in [s for s in constants.INSTANCE_END_STATUS if s != 'failure']
        query_dict = dict(
            date=eff_time.date(),
            cc_biz_id=ai.cc_biz_id,
            biz_team=ai.cc_biz_id,
            is_success=is_success,
            alarm_type=ai.alarm_type,
            failure_type=ai.failure_type,
            solution_type=ai.solution_type,
            source_type=ai.source_type,
            is_off_time=eff_time.hour < 9 or eff_time.hour >= 18,
        )
        return {k: "" if v is None else v for k, v in query_dict.items()}

    def get_rec_id(self, ai):
        query_dict = self.get_query_dict(ai)
        # logger.info("AlarmInstanceArchive query_dict: %s", query_dict)
        try:
            return session.query(FtaSolutionsAppAlarminstancearchive).filter_by(**query_dict).one().id
        except Exception as err:
            # logger.exception(err)
            pass

        try:
            # bug fix, sub_count and so on doesn't have a default value
            for field, default_value in self.DEFAULT_SUB.items():
                query_dict.setdefault(field, default_value)
            now = datetime.datetime.utcnow()
            query_dict.setdefault('created_on', now)
            query_dict.setdefault('updated_on', now)

            result = session.execute(
                FtaSolutionsAppAlarminstancearchive.__table__.insert(),
                query_dict,
            )
            return result.inserted_primary_key[0]
        except Exception as err:
            logger.exception(err)


class BIZ_IN_TIME(object):
    """更新业务接入自愈的时间"""

    def calc(self):
        alarm_def_changes = orm_2_dict(
            session.query(FtaSolutionsAppDatachanglog)
            .filter_by(change_model="AlarmDef").all())
        record_dict = {}
        for alarm_def_change in alarm_def_changes:
            alarm_defs = json.loads(alarm_def_change['new'])
            for alarm_def in alarm_defs:
                if alarm_def['fields'].get('is_enabled'):
                    cc_biz_id = str(alarm_def['fields']['cc_biz_id'])
                    record_dict[cc_biz_id] = record_dict.get(cc_biz_id) or \
                        alarm_def_change['change_time'].strftime("%Y-%m-%d")
        session.query(FtaSolutionsAppConf).filter_by(name="BIZ_IN_TIME").update({"value": json.dumps(record_dict)})
        return record_dict


class KPICache(object):
    """给所有业务计算最近30天的KPI, 一天一次, 每天都是浮动30天的KPI"""

    # 时间范围类型
    KPI_TYPE_DICT = {
        30: u'一个月浮动',
        15: u'半个月浮动',
        7: u'一周浮动',
        1: u'一天浮动'
    }

    # 统计维度
    DEFAULT_SUB = {
        "tnm_total": 0,  # 总 cvm 告警数
        "tnm_covered": 0,  # 总自愈处理的 cvm 告警数
        "tnm_success": 0  # 总自愈执行成功的 cvm 告警数
    }

    def __init__(self):
        # 算到昨天为止，因为今天还没结束，数据还不完整
        self.calc_day = arrow.utcnow().floor('day').replace(days=-1)
        self.result = {}

    def calc(self):
        for cc_biz_id in sorted(BIZ_IN_TIME().calc().keys()):
            for kpi_days in self.KPI_TYPE_DICT.keys():
                rec_id = self.get_rec_id(cc_biz_id, kpi_days)
                self.update_result(rec_id, cc_biz_id, kpi_days)

        # 将 result 中的统计数据更新到数据库
        for id_, value in self.result.items():
            session.query(FtaSolutionsAppKpicache).filter_by(id=id_).update(value)
        return True

    def update_result(self, rec_id, cc_biz_id, kpi_days):

        begin = arrow.utcnow().floor('day').replace(days=-1 * kpi_days).naive
        end = self.calc_day.ceil('day').naive

        logger.info("KPICache %s %s %s %s %s",
                    rec_id, cc_biz_id, kpi_days, begin, end)

        cvm_covered = session.query(
            func.sum(FtaSolutionsAppAlarminstancearchive.sub_count)
        ).filter(
            FtaSolutionsAppAlarminstancearchive.date >= begin
        ).filter(
            FtaSolutionsAppAlarminstancearchive.date <= end
        ).filter_by(cc_biz_id=cc_biz_id).filter_by(source_type="ALERT").scalar() or 0

        cvm_success = session.query(
            func.sum(FtaSolutionsAppAlarminstancearchive.sub_count)
        ).filter(
            FtaSolutionsAppAlarminstancearchive.date >= begin
        ).filter(
            FtaSolutionsAppAlarminstancearchive.date <= end
        ).filter_by(cc_biz_id=cc_biz_id).filter_by(source_type="ALERT").filter_by(is_success=True).scalar() or 0

        # 告警总体为：自愈处理的+网平未处理的告警
        cvm_total = cvm_covered

        self.result[rec_id] = self.result.get(rec_id) or copy.deepcopy(self.DEFAULT_SUB)
        self.result[rec_id]["tnm_total"] = cvm_total
        self.result[rec_id]["tnm_covered"] = cvm_covered
        self.result[rec_id]["tnm_success"] = cvm_success

    def get_rec_id(self, cc_biz_id, kpi_days):
        query_dict = {
            "date": self.calc_day.naive,
            "cc_biz_id": cc_biz_id,
            "kpi_type": kpi_days,
        }
        query_dict = {k: "" if v is None else v for k, v in query_dict.items()}
        try:
            return session.query(FtaSolutionsAppKpicache.id).filter_by(**query_dict).one().id
        except BaseException:
            pass

        try:
            result = session.execute(
                FtaSolutionsAppKpicache.__table__.insert(),
                query_dict,
            )
            return result.inserted_primary_key[0]
        except Exception as err:
            logger.exception(err)


@time_limiter(2 * 60 * 60, u"缓存表统计任务")
def calc(begin_time, end_time):
    logger.info(u"开始统计任务 %s TO %s", begin_time, end_time)

    try:
        AlarmInstanceArchive().calc(begin_time, end_time)
        logger.info(u"统计完成: AlarmInstanceArchive")

    except Exception as e:
        logger.exception(u"执行统计任务失败：%s", e)

    try:
        BIZ_IN_TIME().calc()
        logger.info(u"统计完成: BIZ_IN_TIME")
    except Exception as e:
        logger.exception(u"执行统计任务失败：%s", e)


@redis_lock("update_cache", 15 * 60)
def default_calc():
    begin_time = arrow.utcnow().floor("day").format(constants.STD_ARROW_FORMAT)
    end_time = arrow.utcnow().ceil("day").format(constants.STD_ARROW_FORMAT)
    calc(begin_time, end_time)

    begin_time = arrow.utcnow().replace(days=-1).floor("day").format(constants.STD_ARROW_FORMAT)
    end_time = arrow.utcnow().replace(days=-1).ceil("day").format(constants.STD_ARROW_FORMAT)
    calc(begin_time, end_time)


def main(name=None):
    try:
        begin_time = sys.argv[1]
        end_time = sys.argv[2]
    except BaseException:
        default_calc()
    else:
        date_list = get_time.get_day_by_day(begin_time, end_time)
        logger.info("calc date: %s", date_list)
        for i in range(1, len(date_list)):
            calc(date_list[i - 1], date_list[i])


if __name__ == '__main__':
    main()
