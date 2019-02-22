# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

import arrow

from fta import constants, settings
from fta.collect import CONTEXT
from fta.converge.incident import IncidentManager
from fta.storage.mysql import session
from fta.storage.queue import MessageQueue
from fta.storage.tables import FtaSolutionsAppAlarminstance, FtaSolutionsAppIncident, FtaSolutionsAppIncidentalarm
from fta.utils import get_first, get_list, lock, logging, people, scheduler, send_message
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.i18n import gettext as _
from fta.utils.i18n import i18n
from fta.utils.monitors import get_description_by_alarm_type
from manager.define.incidentdef import get_or_create_incidentdef

logger = logging.getLogger("collect")

COLLECT_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_COLLECT)


class Collect(object):

    def __init__(self):
        self.job = []
        self.alarm_instance = {}
        self.match_info = {}
        self.alarm_def = {}
        self.solution = {}

    def _set_conf(self):
        """
        解析套餐配置

        对于配置 solution["config"]:
        :param range_time: 按时间范围汇总 default: 0
        :param range_count: 按数量范围汇总 default: 0
        :param range_count_floor: 汇总通知下限数量 default: 0
        :param notice_front: 通知前几条的单条告警通知 default: 0
        :param notice_begin: 汇总是否发送开始通知 default: False
        :param notice_end: 汇总是否发送结束通知 default: False
        :param notice_wechat: 汇总是否发送微信通知 default: False
        :param notice_sms: 汇总是否发送短信通知 default: False
        :param notice_mail: 汇总是否发送邮件通知 default: False
        :param notice_im: 汇总是否发送IM通知 default: False
        :param notice_phone: 汇总是否发送电话通知 default: False

        如果没有指定 range_time 和 range_count 相当于不通知。
        如果没有指定 notice_begin 和 notice_end 相当于不通知。
        """
        self.alarm_def = json.loads(self.alarm_instance["snap_alarm_def"])
        self.match_info = json.loads(self.alarm_instance["origin_alarm"])["_match_info"]
        self.solution = json.loads(self.alarm_instance["snap_solution"] or "{}")

        # 获取通知人
        self.verifier = people.get_verifier(self.alarm_instance["id"])

        try:
            if self.alarm_instance["solution_type"] == "collect":
                config = json.loads(self.solution.get("config"))
            else:
                config = {}
        except BaseException:
            config = {}

        # 对于请关注的告警，添加默认的汇总通知
        if self.alarm_instance["status"] == "for_notice":
            config = {
                "range_time": "30",
                "notice_begin": "on",
                "notice_end": "on"
            }
        self.config = config

        # 按时间范围汇总
        self.range_time = int(config.get("range_time", 0) or 0)
        # 按数量范围汇总
        self.range_count = int(config.get("range_count", 0) or 0)
        # 汇总通知下限数量
        self.range_count_floor = int(config.get("range_count_floor", 0) or 0)
        # 通知前几条的单条告警通知
        self.notice_front = int(config.get("notice_front", 0) or 0)
        # 判断是否从告警配置获取通知策略
        if config.get("notice_conf_by_alarm_def"):
            _notify_conf = json.loads(self.alarm_def.get("notify") or "{}")
            # 汇总是否开始通知
            self.notice_begin = any([k.startswith("begin_notify") for k in _notify_conf.keys()])
            # 汇总是否结束通知
            self.notice_end = any([k.startswith("end_notify") for k in _notify_conf.keys()])
            # 汇总是否微信通知
            self.notice_wechat = any([k.endswith("notice_wechat") for k in _notify_conf.keys()])
            # 汇总是否短信通知
            self.notice_sms = any([k.endswith("notice_sms") for k in _notify_conf.keys()])
            # 汇总是否邮件通知
            self.notice_mail = any([k.endswith("notice_mail") for k in _notify_conf.keys()])
            # 汇总是否IM通知
            self.notice_im = any([k.endswith("notice_im") for k in _notify_conf.keys()])
            # 汇总是否电话通知
            self.notice_phone = any([k.endswith("notice_phone") for k in _notify_conf.keys()])
        else:
            # 汇总是否开始通知
            self.notice_begin = config.get("notice_begin")
            # 汇总是否结束通知
            self.notice_end = config.get("notice_end")
            # 汇总是否微信通知
            self.notice_wechat = config.get("notice_wechat")
            # 汇总是否短信通知
            self.notice_sms = config.get("notice_sms")
            # 汇总是否邮件通知
            self.notice_mail = config.get("notice_mail")
            # 汇总是否IM通知
            self.notice_im = config.get("notice_im")
            # 汇总是否电话通知
            self.notice_phone = config.get("notice_phone")
        # 汇总的维度
        self.dimension = config.get("dimension", [])

        # 拼接 collect 的 key
        self.alarm_key = u"collect:[%s](%s)%s" % (
            self.match_info["cc_biz_id"],
            self.alarm_def["id"],
            "_".join([get_first(self.match_info[dimension]) for dimension in self.dimension if config.get(dimension)])
        )
        self.alarm_time_key = "%s_time" % self.alarm_key

    def _get_notice_info(self):
        """获取通知信息变量"""

        # 生成 collect_type 描述
        collect_type = []
        if self.alarm_instance["status"] == "for_notice":
            collect_type.append(_("(Alarm is skipped by flow control)"))
        if self.range_time:
            collect_type.append(_("%(range_time)s minute(s)", range_time=self.range_time))
        if self.range_count:
            collect_type.append(_("%(range_count)s article(s)", range_count=self.range_count))
        collect_type = "".join(collect_type)

        # 生成 dimension 描述
        dimension_desc = [
            u"%s(%s)" % (dimension, ",".join(get_list(self.match_info[dimension])))
            for dimension in self.dimension if self.config.get(dimension)
        ]

        return {
            "collect_type": collect_type,
            "cc_biz_id": self.match_info["cc_biz_id"],
            "cc_biz_name": self.match_info["cc_biz_id"],
            "alarm_type": get_description_by_alarm_type(
                self.alarm_def["alarm_type"],
                default=self.alarm_def["alarm_type"]
            ),
            "description": self.alarm_def.get("description", "") or self.solution.get("title", ""),
            "dimension": u" ".join(dimension_desc) if dimension_desc else _("all")
        }

    def pull_alarm(self, event_id=None, alarm_instance={}):
        """
        拉取告警
        :param event_id: 指定拉取的告警的 event_id，通常用于测试
        :param alarm_instance: 指定拉取的告警的字典，通常用于测试
        """

        # 没有指定 event_id 或 alarm_instance 则从队列中取
        if not event_id and not alarm_instance:
            self.job = COLLECT_QUEUE.take(timeout=settings.QUEUE_WAIT_TIMEOUT)
            if not self.job:
                raise lock.PassEmpty
            self.event_id = self.job.body
            logger.info("collect process event_id: %s", self.event_id)

        # 如果传入一个 event_id，则通过 id 获取告警，通常是为了测试
        elif event_id:
            self.event_id = event_id

        # 如果传入一个告警字典则直接使用，通常是为了测试
        if alarm_instance:
            self.alarm_instance = alarm_instance

        # 没有指定 alarm_instance 则根据 event_id 从数据库中取
        else:
            lock.lock_collect_alarm(self.event_id)
            self.alarm_instance = get_alarm_instance(event_id=self.event_id)

        i18n.set_biz(self.alarm_instance['cc_biz_id'])

        CONTEXT.set("id", self.alarm_instance["id"])

        # 获取配置信息
        self._set_conf()

    def _check_conf(self):
        # 没有有效配置就跳过
        if not (self.range_time or self.range_count or
                self.notice_begin or self.notice_end):
            logger.info(
                u"$%s not conf: %s",
                self.alarm_instance["id"],
                self.alarm_instance["snap_solution"])
            raise lock.PassEmpty

    def _send_message(self):
        """发送单条告警通知"""
        end_status, self.alarm_instance["status"] = self.alarm_instance["status"], "received"
        send_message.notify_info(self.alarm_instance)
        self.alarm_instance["status"] = end_status
        send_message.notify_info(self.alarm_instance)

    def collect_alarm(self):

        # 发送告警通知
        if self.alarm_instance["solution_type"] != "collect":
            self._send_message()

        # 检查汇总配置是否合法
        self._check_conf()

        # 获取通知信息参数
        self.notice_info = self._get_notice_info()

        # collect_alarm 为汇总专用
        incident_def_id = get_or_create_incidentdef(codename='collect_alarm').id

        # 创建或获取集合事件
        if self.alarm_instance['status'] in ['for_notice']:
            description = self.notice_info['collect_type']
        else:
            description = u"%s %s" % (self.notice_info["alarm_type"], self.notice_info["dimension"])

        incident_dict = {
            "incident_def_id": incident_def_id,
            "cc_biz_id": self.match_info["cc_biz_id"],
            "dimension": "%s" % self.alarm_key,
            "incident_type": "collect_alarm",
            "description": description,
        }

        incident_manager = IncidentManager(
            incident_dict, [self.alarm_instance["id"]])
        if self.range_time:
            # 防止事件因为意外未被关闭，超过时限5分钟强制关闭
            start_time = arrow.utcnow().replace(minutes=-(self.range_time + 5)).naive
        else:
            start_time = None
        incident = incident_manager.create_incident(start_time=start_time)

        # 补充事件信息到通知信息
        if hasattr(settings, "WECHAT_URL"):
            self.notice_info["url"] = "%swechat/incident_detail/%s/" % (settings.WECHAT_URL, incident["id"])
        else:
            self.notice_info["url"] = ""
        self.notice_info["incident_id"] = incident["id"]
        self.notice_info["collect_count"] = incident_manager.count_alarm()
        self.notice_info["begin_time"] = incident["begin_time"]
        self.notice_info["end_time"] = incident["end_time"] or arrow.utcnow().format(constants.STD_ARROW_FORMAT)
        logger.info(
            "$%s collect(count=%s) incident(id=%s, is_created=%s)",
            self.alarm_instance["id"],
            self.notice_info["collect_count"],
            incident["id"],
            incident_manager.is_created)

        # 如果没有集合
        if incident_manager.is_created:
            # 发送开始通知
            if self.notice_begin:
                send_message.notify_collect(
                    "begin", self.verifier,
                    self.notice_wechat,
                    self.notice_sms,
                    self.notice_mail,
                    self.notice_im,
                    self.notice_phone,
                    **self.notice_info)
                self._update_comment(_("Collection successful (notification start)"))
            # 设置定时任务发送通知
            if self.notice_end and self.range_time:
                self._call_in_future(incident["id"])

        # 集合数量达到阈值触发通知
        elif self.range_count \
                and self.notice_info["collect_count"] >= self.range_count \
                and IncidentManager.end_incident_by_id(incident["id"]) \
                and self.notice_end:
            send_message.notify_collect(
                "end", self.verifier,
                self.notice_wechat,
                self.notice_sms,
                self.notice_mail,
                self.notice_im,
                self.notice_phone,
                **self.notice_info)
            self._update_comment(
                _("Collection successful (trigger threshold [%(range_count)s] notification)",
                  range_count=self.range_count)
            )
        else:
            # 直接保存无处理
            self._update_comment(_('Collection successful (save directly without processing)'))

    def _update_comment(self, comment):
        # QOS不更新描述
        if self.alarm_instance['status'] in ['for_reference']:
            session.query(FtaSolutionsAppAlarminstance).filter_by(
                id=self.alarm_instance["id"],
            ).update({"comment": comment})

    def _call_in_future(self, incident_id):
        """调用定时任务来发送结束通知"""
        scheduler.run(
            module="fta.collect.process",
            function="end_collect_by_time",
            args=(
                incident_id,
                self.range_count_floor,
                self.notice_info,
                self.verifier,
                self.notice_wechat,
                self.notice_sms,
                self.notice_mail,
                self.notice_im,
                self.notice_phone),
            delta_seconds=60 * int(self.range_time))

    def push_alarm(self):
        pass

    def start(self):
        try:
            self.pull_alarm()
            self.collect_alarm()
            self.push_alarm()
        except lock.PassEmpty:
            pass
        except lock.LockError as e:
            logger.info("$%s %s", self.event_id, e)
        except Exception as e:
            logger.exception("%s $%s frame_error %s", constants.ERROR_01_CONERGE, self.alarm_instance.get("id"), e)
            raise
        finally:
            if self.job:
                self.job.delete()


def end_collect_by_time(
        incident_id, count_floor,
        notice_info, verifier,
        notice_wechat=True, notice_sms=False, notice_mail=True, notice_im=False, notice_phone=False):
    """发送按时间段汇总的结束通知"""
    logger.info("collect end incident: %s", incident_id)

    # 如果事件已经被其他进程结束，则跳过
    if IncidentManager.end_incident_by_id(incident_id):
        incident = session.query(
            FtaSolutionsAppIncident).filter_by(id=incident_id).one()

        # 更新开始时间、结束事件、汇总数量
        notice_info["begin_time"] = incident.begin_time.strftime(constants.STD_DT_FORMAT)
        notice_info["end_time"] = incident.end_time.strftime(constants.STD_DT_FORMAT)
        notice_info["collect_count"] = session.query(FtaSolutionsAppIncidentalarm).filter_by(
            incident_id=incident_id).count()

        # 判断汇总数量是否达到通知的下限数量
        if notice_info["collect_count"] > count_floor:
            send_message.notify_collect(
                "end", verifier,
                notice_wechat, notice_sms, notice_mail, notice_im, notice_phone,
                **notice_info)

    else:
        logger.info("collect end incident pass: %s", incident_id)
