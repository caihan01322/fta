# -*- coding: utf-8 -*
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import collections
import email
import email.header
import json
import time
from contextlib import contextmanager
from functools import partial
from multiprocessing.pool import ThreadPool as Pool

import arrow
import six
from project.utils import query_cc
from project.utils.component import bk

from fta import settings
from fta.storage.mysql import session
from fta.storage.tables import AlarmApplication
from fta.utils import cipher, get_time, lock, logging, monitors
from fta.utils.text_parser import Context
from fta.utils.text_parser import SimpleParser as MailParser
from manager.utils.query_cc import (
    handle_alarm_source_empty,
    handle_alarm_source_exception,
    handle_alarm_source_success
)

try:
    from fta.poll_alarm.process import BasePollAlarm
except ImportError:
    BasePollAlarm = object

logger = logging.getLogger("poll_alarm")
EMailConfig = collections.namedtuple("EMailConfig",
                                     ["server_host", "server_port", "is_secure", "username", "password", ])
LOCALE_TZ = time.strftime("%Z", time.localtime())


class EMail(dict):
    AVALIABLE_CONTENT_TYPE = frozenset(["text/plain", "text/html", ])

    @classmethod
    def from_dict(cls, data):
        mail = cls(uid=data.get("uid"), message=None)
        mail.update(data)
        mail.uid = data.get("uid")
        mail.sender = data.get("sender")
        mail.receiver = data.get("receiver")
        mail.subject = data.get("subject")
        mail.message_id = data.get("message_id")
        mail.content = data.get("content")
        mail.time = arrow.get(data.get("time"))
        mail.criteria = data.get("criteria")
        return mail

    def __getattr__(self, attr):
        return self[attr]

    def __init__(self, uid, message, criteria=None, charset="utf-8"):
        self.uid = uid
        self.sender = None
        self.receiver = None
        self.subject = None
        self.message_id = None
        self.subject = None
        self.content = None
        self.time = None
        self.criteria = None
        self.charset = charset
        self.raw = None
        self.refresh(message, criteria)

    def to_dict(self):
        return {
            "uid": self.uid,
            "sender": self.sender,
            "receiver": self.receiver,
            "subject": self.subject,
            "message_id": self.message_id,
            "content": self.content,
            "time": self.time and self.time.isoformat(),
            "criteria": self.criteria,
        }

    @classmethod
    def decode(cls, content, charset=None):
        result = []
        for i, c in email.header.decode_header(content):
            i = i.decode(c or charset)
            result.append(i)
        return u"".join(result)

    @classmethod
    def _get_payload(cls, message, charset=None):
        if isinstance(message, six.string_types):
            return message
        payload = []
        for i in message.walk():
            if i.is_multipart():
                continue
            if i.get_content_type() in cls.AVALIABLE_CONTENT_TYPE:
                data = i.get_payload(decode=True)
                if isinstance(data, six.binary_type):
                    content_charset = i.get_content_charset(charset)
                    if content_charset:
                        data = data.decode(content_charset, "ignore")
                payload.append(data)

        return "".join(payload)

    def refresh(self, message, criteria=None):
        if not message:
            return
        raw = email.message_from_string(message)
        self.clear()
        self.raw = raw
        self.criteria = criteria
        self.charset = (raw.get_charset() or raw.get_content_charset(self.charset))

        self.update({k: self.decode(v, self.charset) for k, v in raw.items()})
        self.sender = self.get("From")
        self.receiver = self.get("To")
        self.subject = self.get("Subject")
        self.message_id = self.get("Message-ID")
        self.content = self._get_payload(raw, self.charset)

        date = self.get("Date")
        if date:
            self.time = arrow.get(date, "ddd, D MMM YYYY HH:mm:SS Z", ).to(LOCALE_TZ)


def contain_one(content, patterns):
    for p in patterns:
        if p in content:
            return True
    return False


class MailPoller(object):
    CRITERIA_HEADER = "RFC822.HEADER"
    CRITERIA = "RFC822"

    def __init__(
            self, email, password, pool,
            imap_host=None, imap_port=None,
            secure=True,
    ):
        self.email = email
        self.password = password
        self.pool = pool
        self.imap_host = imap_host
        self.imap_port = int(imap_port)
        self.secure = secure
        self._imap_client = None

    @property
    def imap_client(self):
        import imaplib

        if self._imap_client:
            return self._imap_client
        if self.secure:
            imap_client = imaplib.IMAP4_SSL(self.imap_host, self.imap_port, )
        else:
            imap_client = imaplib.IMAP4(self.imap_host, self.imap_port, )
        imap_client.login(self.email, self.password)
        self._imap_client = imap_client
        self._imap_client.select()
        return imap_client

    def noop(self):
        status, result = self.imap_client.noop()
        return status

    def select(self, mailbox="INBOX"):
        self.imap_client.select(mailbox)

    def search(self, charset=None, unseen=None, before=None, since=None, size_limit=None, ):
        queries = []
        if unseen is not None:
            queries.append("(UNSEEN)")
        if before:
            queries.append('(BEFORE "%s")' % before.replace(days=1).strftime("%d-%b-%Y"), )
        if since:
            queries.append('(SINCE "%s")' % since.strftime("%d-%b-%Y"), )
        if size_limit:
            queries.append('(SMALLER %s)' % size_limit)
        if not queries:
            queries.append('ALL')
        status, result = self.imap_client.search(charset, " ".join(queries))
        if status != "OK":
            return []
        return [EMail(uid, None, charset=charset) for uid in result[0].split()]

    def filter(self, mails, sent_from=None, sent_to=None, subject=None, before=None, since=None,
               fetch_header_already=False, ):
        result_list = []
        mails = mails if fetch_header_already else self.iter_fetch_chunks(mails=mails, criteria=self.CRITERIA_HEADER, )
        sent_from = sent_from.split(",") if sent_from else ()
        sent_to = sent_to.split(",") if sent_to else ()
        subject = [subject] if subject else []
        for mail in mails:
            if ((before and before <= mail.time) or (since and since > mail.time)):
                continue
            if sent_from and not contain_one(mail.sender, sent_from):
                continue
            if sent_to and not contain_one(mail.receiver, sent_to):
                continue
            if subject and not contain_one(mail.subject, subject):
                continue

            result_list.append(mail)
        return result_list

    def fetch_header(self, mails):
        for mail in self.iter_fetch_chunks(mails=mails, criteria=self.CRITERIA_HEADER, ):
            pass

    def fetch(self, mails, criteria=None):
        mail_mappings = {str(mail.uid): mail for mail in mails}
        status, result = self.imap_client.fetch(",".join(mail_mappings.keys()), criteria or self.CRITERIA, )
        if status != "OK":
            logger.warning("fetch mail[%s] failed", mail_mappings.keys())
            return
        for i in result:
            if len(i) < 2:
                continue
            uid, s, _ = i[0].partition(" ")
            mail = mail_mappings[uid]
            mail.refresh(i[1], criteria)
        return mails

    def iter_fetch_chunks(self, mails, chunks=100, criteria=None):
        def fetch(mail):
            try:
                return self.fetch(mail, criteria)
            except Exception as error:
                logger.error(error)
                return ()

        if mails:
            length = len(mails)
            chunks_list = [mails[i: i + chunks] for i in range(0, length, chunks)]
            for chunk in self.pool.imap(fetch, chunks_list):
                for mail in chunk:
                    yield mail

    def fetch_by(
            self, charset=None, unseen=None, before=None, since=None,
            size_limit=None, sent_from=None, sent_to=None, subject=None,
            index=None, limit=None,
    ):
        mails = self.search(charset=charset, unseen=unseen, before=before, since=since, size_limit=size_limit, )
        mails = self.filter(mails, sent_from=sent_from, sent_to=sent_to, subject=subject, before=before, since=since, )
        if index is not None:
            mails = mails[index:]
        if limit is not None:
            mails = mails[:limit]
        return list(self.iter_fetch_chunks(mails))

    @classmethod
    def fetch_dict_list(
            cls, email, password,
            imap_host=None, imap_port=None, secure=True,
            charset=None, unseen=None, before=None, since=None,
            size_limit=None, sent_from=None, sent_to=None, subject=None,
            index=None, limit=None,
    ):
        from multiprocessing.pool import ThreadPool as Pool
        pool = Pool(1)
        poller = cls(
            email, password, pool,
            imap_host=imap_host, imap_port=imap_port, secure=secure,
        )
        mails = []
        for mail in poller.fetch_by(
                charset=charset, unseen=unseen, before=before, since=since,
                size_limit=size_limit, sent_from=sent_from, sent_to=sent_to,
                subject=subject, index=index, limit=limit,
        ):
            mails.append(mail.to_dict())
        return mails


class EMailPollAlarm(BasePollAlarm):
    SOURCE_TYPE = "EMAIL"
    ALARM_FIELDS = ["ip", "cc_biz_id", "alarm_content", "alarm_type", "source_id", "source_time", "application_id", ]
    SIZE_LIMIT = 200 * 1024

    def __init__(self, force_begin_time=None, force_end_time=None, minutes=None, delta_minutes=0, debug=False, ):
        """
        :param force_begin_time: 指定拉取的告警的开始时间
        :param force_end_time: 指定拉取的告警的结束时间
        :param minutes: 指定拉取一天中的哪一分钟(一天的第一分钟为1，共24*60分钟)
        :param delta_minutes: 指定拉取与当前分钟相差多久的时间的告警
        """
        self.delta_minutes = delta_minutes
        self.str_begin_time, self.str_end_time = get_time.get_time(minutes=minutes, delta_minutes=delta_minutes)
        self.str_begin_time = force_begin_time or self.str_begin_time
        self.str_end_time = force_end_time or self.str_end_time

        self.end_time = arrow.get(self.str_end_time, ).replace(tzinfo=LOCALE_TZ)
        self.start_time = arrow.get(self.str_begin_time).replace(tzinfo=LOCALE_TZ)
        self.size_limit = self.SIZE_LIMIT
        self.applications = {}
        self.hosts_info = {}
        self.companies_info = {}
        self.qos_dict = {}
        self.pool = Pool()
        self.debug = debug
        self.load_application_config()
        super(EMailPollAlarm, self).__init__()

    @contextmanager
    def global_proxy(self):
        socks5_proxy = settings.REQUESTS_PROXIES.get("socks5")
        if not socks5_proxy:
            return

        import socks
        import socket
        import urlparse

        raw_socket = socket.socket

        if socket.socket is not socks.socksocket:
            info = urlparse.urlparse(socks5_proxy)
            if info.hostname and info.port:
                socks.set_default_proxy(
                    socks.PROXY_TYPE_SOCKS5,
                    addr=info.hostname or None,
                    port=info.port or None,
                    username=info.username or None,
                    password=info.password or None,
                )
            socket.socket = socks.socksocket

        try:
            yield
        finally:
            socket.socket = raw_socket

    def load_application_config(self):
        applications = self.applications
        for app in session.query(AlarmApplication).filter(
            AlarmApplication.is_enabled,
            AlarmApplication.is_deleted is False,
            AlarmApplication.source_type == self.SOURCE_TYPE,
        ):
            if not app.extra:
                continue
            try:
                app.extra_config = json.loads(app.extra)
                app.email_config = self.get_email_config(app.extra_config)
            except Exception:
                app.extra_config = None
                app.email_config = None
                logger.warning("load application[%s] config failed", app.id)
            if app.extra_config:
                applications[app.cc_biz_id] = app

    def get_email_config(self, extra_config):
        return EMailConfig(
            is_secure=extra_config["is_secure"],
            username=extra_config["username"],
            password=extra_config["password"],
            server_host=extra_config["server_host"],
            server_port=extra_config["server_port"],
        )

    def pull_emails_by_applications(self, email_config, applications):
        fetched_mails = {}
        cp = cipher.AESCipher.default_cipher()
        poller = MailPoller(
            email=email_config.username,
            password=cp.decrypt(email_config.password),
            pool=self.pool,
            imap_host=email_config.server_host,
            imap_port=email_config.server_port,
            secure=email_config.is_secure,
        )
        mails = poller.search(
            unseen=True, before=self.end_time, since=self.start_time,
            size_limit=self.size_limit,
        )
        if mails:
            poller.fetch_header(mails)
            for app in applications:
                sent_from = app.extra_config.get("sent_from")
                sent_to = app.extra_config.get("sent_to")
                target_mails = []
                try:
                    filter_results = poller.filter(
                        mails, before=self.end_time,
                        since=self.start_time,
                        fetch_header_already=True,
                        sent_from=(sent_from.split(",") if sent_from else None),
                        sent_to=(sent_to.split(",") if sent_to else None),
                    )
                except Exception as error:
                    logger.warning("filter error: %s", error)
                    continue
                for mail in filter_results:
                    if mail.uid not in fetched_mails:
                        target_mails.append(mail)
                if not target_mails:
                    continue
                try:
                    for mail in poller.fetch(target_mails):
                        fetched_mails[mail.uid] = mail
                except Exception as error:
                    logger.error(error)

        return fetched_mails.values()

    def get_host_info(self, cc_biz_id, ip):
        cache_key = (cc_biz_id, ip)
        host_info = self.hosts_info.get(cache_key)
        if not host_info:
            host_info = query_cc.get_host_info_by_ip(cc_biz_id, ip, )
            self.hosts_info[cache_key] = host_info
        return host_info

    def get_company_info(self, ip):
        cache_key = ip
        company_info = self.companies_info.get(cache_key)
        if not company_info:
            company_infos = query_cc.get_open_region_biz_info(ip)
            if len(company_infos) != 1:  # 要求唯一
                return None
            company_info = company_infos[0]
            self.companies_info[cache_key] = company_info
        return company_info

    def match_alarm_from_emails(self, emails, application):
        alarm_list = []
        item_config = application.extra_config.get("items")
        if item_config:
            for mail in emails:
                parser = MailParser.from_config(
                    item_config,
                    context=Context(
                        values={
                            "SUBJECT": mail.subject,
                            "SENDER": mail.sender,
                            "RECEIVER": mail.receiver,
                            "MESSAGEID": mail.message_id,
                        }, ), )
                try:
                    context = parser.parse(mail.content)
                except Exception:
                    continue
                values = context.values.copy()
                values.update({
                    "application_id": application.id,
                    "cc_biz_id": application.cc_biz_id,
                    "is_global": application.cc_biz_id == 0,
                    "source_time": mail.time.isoformat(),
                })
                values.setdefault("source_id", mail.message_id)

                alarm_list.append({k: values[k] for k in self.ALARM_FIELDS})
        return alarm_list

    def push_alarm(self):
        from datetime import datetime

        super(EMailPollAlarm, self).push_alarm()
        for i in self.alarm_list:
            session.query(AlarmApplication).filter_by(
                id=i["application_id"]
            ).update({
                "activate_time": datetime.utcnow(),
            })

    def pull_alarm(self):
        """拉取告警"""
        if not self.debug:
            lock_email_polling(self.str_begin_time, self.str_end_time, self.delta_minutes, group=self.SOURCE_TYPE, )
        self.pull_alarm_by_esb()

    def pull_alarm_by_esb(self):
        """通过ESB拉取告警"""
        alarm_list = []

        for app in self.applications.values():
            # 对应 AlarmApplication 的id
            alram_app_id = app.id
            if not app.email_config:
                handle_alarm_source_exception(alram_app_id, u"邮箱配置信息不完整")
                continue
            email_config = app.email_config
            cp = cipher.AESCipher.default_cipher()
            password = (cp.decrypt(email_config.password) if cp else email_config.password)
            try:
                params = {
                    "app_id": app.cc_biz_id,
                    "email": email_config.username,
                    "password": password,
                    "imap_host": email_config.server_host,
                    "imap_port": email_config.server_port,
                    "secure": email_config.is_secure,
                    "uin": "100",
                    "username": "admin",
                    "limit": 100,
                    "since": self.start_time.isoformat(),
                    "before": self.end_time.isoformat(),
                }
                logger.info("pulling email[%s] by esb", email_config.username)
                data = bk.fta.imap_relay__api(**params)
            except Exception as error:
                # 记录告警源异常信息
                handle_alarm_source_exception(alram_app_id, error)
                logger.exception(error)
                continue
            try:
                alarm_list.extend(self.match_alarm_from_emails(
                    [EMail.from_dict(i) for i in data],
                    app,
                ))
            except Exception as error:
                logger.warning("match email error: %s", error)

            # 从告警源中没有拉取到告警，也要记录到db总
            if not data:
                handle_alarm_source_empty(alram_app_id)
            else:
                handle_alarm_source_success(alram_app_id)

        for i in alarm_list:
            try:
                ip = i["ip"]
                company_info = self.get_company_info(ip)
                if not company_info:
                    continue
                i["_CC_COMPANY_INFO"] = company_info
                if i.get("is_global"):
                    i["cc_biz_id"] = company_info["ApplicationID"]

                cc_biz_id = i["cc_biz_id"]
                host_info = self.get_host_info(cc_biz_id, ip)
                if not host_info:
                    continue
                i["_CC_HOST_INFO"] = host_info
                self.alarm_list.append(i)
            except Exception as err:
                logger.error(err)
        return alarm_list

    def pull_alarm_directly(self):
        """拉取告警"""
        # merge email configurations
        email_config_applitions = collections.defaultdict(list)
        for i in self.applications.values():
            if not i.email_config:
                continue
            email_config_applitions[i.email_config].append(i)

        pull_emails_by_applications = self.pull_emails_by_applications
        match_alarm_from_emails = self.match_alarm_from_emails

        def pull_and_match(item):
            email_config, applications = item
            try:
                mails = pull_emails_by_applications(email_config, applications, )
            except Exception as error:
                logger.error(error)
                return ()

            if not mails:
                return

            results = []
            for app in applications:
                try:
                    results.extend(match_alarm_from_emails(mails, app, ))
                except Exception as error:
                    logger.warning("match email error: %s", error)
            return results

        alarm_list = []
        with self.global_proxy():
            for i in self.pool.imap(pull_and_match, email_config_applitions.items(), ):
                if i:
                    alarm_list.extend(i)

        for i in alarm_list:
            try:
                ip = i["ip"]
                company_info = self.get_company_info(ip)
                if not company_info:
                    continue
                i["_CC_COMPANY_INFO"] = company_info
                if i.get("is_global"):
                    i["cc_biz_id"] = company_info["ApplicationID"]

                cc_biz_id = i["cc_biz_id"]
                host_info = self.get_host_info(cc_biz_id, ip)
                if not host_info:
                    continue
                i["_CC_HOST_INFO"] = host_info
                self.alarm_list.append(i)
            except Exception as err:
                logger.error(err)

    def clean_host(self, alarm):
        return alarm["ip"]

    def clean_source_type(self, alarm):
        """
        获取告警源
        :param alarm: 原始告警字典
        :return source_type: 告警源的名称
        """
        return self.SOURCE_TYPE

    def clean_alarm_attr_id(self, alarm):
        return ''

    def clean_source_id(self, alarm):
        return alarm["source_id"]

    def clean_alarm_time(self, alarm):
        return alarm['source_time']

    def clean_alarm_type(self, alarm):
        alarm_type = alarm.get("alarm_type") or "email"
        cc_biz_id = alarm["cc_biz_id"]
        lookup_alarm_type_list = partial(
            monitors.lookup_alarm_type_list, [alarm_type],
            source_type=self.SOURCE_TYPE,
            default=alarm_type,
        )
        alarm_types = list(lookup_alarm_type_list(cc_biz_id=cc_biz_id))
        if alarm.get("is_global"):
            alarm_types += list(lookup_alarm_type_list(cc_biz_id=0))
        return alarm_types

    def clean_alarm_desc(self, alarm):
        return alarm['alarm_content']

    def clean_cc_biz_id(self, alarm):
        return alarm['_CC_COMPANY_INFO']['ApplicationID']

    def clean_cc_topo_set(self, alarm):
        return alarm['_CC_HOST_INFO']['SetName'].split(",")

    def clean_cc_app_module(self, alarm):
        return alarm['_CC_HOST_INFO']['ModuleName'].split(",")

    def clean_cc_company_id(self, alarm):
        logger.info(alarm)
        return alarm['_CC_COMPANY_INFO']['CompanyID']

    def clean_cc_plat_id(self, alarm):
        return alarm['_CC_COMPANY_INFO']['PlatID']


def lock_email_polling(str_begin_time, str_end_time, delta_minutes, group):
    begin_time = arrow.get(str_begin_time).replace(tzinfo="utc")
    minutes = (begin_time - begin_time.floor('day')).seconds / 60
    id_ = int(begin_time.format("YYMMDD") + str(minutes))
    if not lock.redis_lock("--lock_%s_%s-%s-%s" % (group, str_begin_time, str_end_time, delta_minutes)):
        raise lock.LockError("poll_%s: %s pass" % (group, id_))
