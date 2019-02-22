# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from datetime import datetime

from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Index, Integer, SmallInteger, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        Index('group_id', 'group_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey(u'auth_group.id'), nullable=False, index=True)
    permission_id = Column(
        ForeignKey(u'auth_permission.id'), nullable=False, index=True)

    group = relationship(u'AuthGroup')
    permission = relationship(u'AuthPermission')


class AuthMessage(Base):
    __tablename__ = 'auth_message'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    message = Column(String, nullable=False)

    user = relationship(u'AuthUser')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        Index('content_type_id', 'content_type_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    content_type_id = Column(
        ForeignKey(u'django_content_type.id'), nullable=False, index=True)
    codename = Column(String(100), nullable=False)

    content_type = relationship(u'DjangoContentType')


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(75), nullable=False)
    password = Column(String(128), nullable=False)
    is_staff = Column(Integer, nullable=False)
    is_active = Column(Integer, nullable=False)
    is_superuser = Column(Integer, nullable=False)
    last_login = Column(DateTime, nullable=False)
    date_joined = Column(DateTime, nullable=False)


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        Index('user_id', 'user_id', 'group_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    group_id = Column(ForeignKey(u'auth_group.id'), nullable=False, index=True)

    group = relationship(u'AuthGroup')
    user = relationship(u'AuthUser')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        Index('user_id', 'user_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    permission_id = Column(
        ForeignKey(u'auth_permission.id'), nullable=False, index=True)

    permission = relationship(u'AuthPermission')
    user = relationship(u'AuthUser')


class CeleryTaskmeta(Base):
    __tablename__ = 'celery_taskmeta'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    result = Column(String)
    date_done = Column(DateTime, nullable=False)
    traceback = Column(String)
    hidden = Column(Integer, nullable=False, index=True)
    meta = Column(String)


class CeleryTasksetmeta(Base):
    __tablename__ = 'celery_tasksetmeta'

    id = Column(Integer, primary_key=True)
    taskset_id = Column(String(255), nullable=False, unique=True)
    result = Column(String, nullable=False)
    date_done = Column(DateTime, nullable=False)
    hidden = Column(Integer, nullable=False, index=True)


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'

    id = Column(Integer, primary_key=True)
    action_time = Column(DateTime, nullable=False)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    content_type_id = Column(ForeignKey(u'django_content_type.id'), index=True)
    object_id = Column(String)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    change_message = Column(String, nullable=False)

    content_type = relationship(u'DjangoContentType')
    user = relationship(u'AuthUser')


class DjangoCache(Base):
    __tablename__ = 'django_cache'

    cache_key = Column(String(255), primary_key=True)
    value = Column(String, nullable=False)
    expires = Column(DateTime, nullable=False, index=True)


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('app_label', 'app_label', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40), primary_key=True)
    session_data = Column(String, nullable=False)
    expire_date = Column(DateTime, nullable=False, index=True)


class DjangoSite(Base):
    __tablename__ = 'django_site'

    id = Column(Integer, primary_key=True)
    domain = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)


class DjceleryCrontabschedule(Base):
    __tablename__ = 'djcelery_crontabschedule'

    id = Column(Integer, primary_key=True)
    minute = Column(String(64), nullable=False)
    hour = Column(String(64), nullable=False)
    day_of_week = Column(String(64), nullable=False)
    day_of_month = Column(String(64), nullable=False)
    month_of_year = Column(String(64), nullable=False)


class DjceleryIntervalschedule(Base):
    __tablename__ = 'djcelery_intervalschedule'

    id = Column(Integer, primary_key=True)
    every = Column(Integer, nullable=False)
    period = Column(String(24), nullable=False)


class DjceleryPeriodictask(Base):
    __tablename__ = 'djcelery_periodictask'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    task = Column(String(200), nullable=False)
    interval_id = Column(
        ForeignKey(u'djcelery_intervalschedule.id'), index=True)
    crontab_id = Column(ForeignKey(u'djcelery_crontabschedule.id'), index=True)
    args = Column(String, nullable=False)
    kwargs = Column(String, nullable=False)
    queue = Column(String(200))
    exchange = Column(String(200))
    routing_key = Column(String(200))
    expires = Column(DateTime)
    enabled = Column(Integer, nullable=False)
    last_run_at = Column(DateTime)
    total_run_count = Column(Integer, nullable=False)
    date_changed = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)

    crontab = relationship(u'DjceleryCrontabschedule')
    interval = relationship(u'DjceleryIntervalschedule')


class DjceleryPeriodictasks(Base):
    __tablename__ = 'djcelery_periodictasks'

    ident = Column(SmallInteger, primary_key=True)
    last_update = Column(DateTime, nullable=False)


class DjceleryTaskstate(Base):
    __tablename__ = 'djcelery_taskstate'

    id = Column(Integer, primary_key=True)
    state = Column(String(64), nullable=False, index=True)
    task_id = Column(String(36), nullable=False, unique=True)
    name = Column(String(200), index=True)
    tstamp = Column(DateTime, nullable=False, index=True)
    args = Column(String)
    kwargs = Column(String)
    eta = Column(DateTime)
    expires = Column(DateTime)
    result = Column(String)
    traceback = Column(String)
    runtime = Column(Float(asdecimal=True))
    retries = Column(Integer, nullable=False)
    worker_id = Column(ForeignKey(u'djcelery_workerstate.id'), index=True)
    hidden = Column(Integer, nullable=False, index=True)

    worker = relationship(u'DjceleryWorkerstate')


class DjceleryWorkerstate(Base):
    __tablename__ = 'djcelery_workerstate'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(255), nullable=False, unique=True)
    last_heartbeat = Column(DateTime, index=True)


class FtaSolutionsAppAdvice(Base):
    __tablename__ = 'fta_solutions_app_advice'

    id = Column(Integer, primary_key=True)
    advice_def_id = Column(Integer, nullable=False, index=True)
    cc_biz_id = Column(Integer, nullable=False)
    subject = Column(String(128), nullable=False)
    alarm_num = Column(Integer, nullable=False)
    alarm_start_time = Column(Date, nullable=False)
    alarm_end_time = Column(Date, nullable=False)
    status = Column(String(32), nullable=False)
    comment = Column(String)
    create_time = Column(DateTime, nullable=False, index=True)
    operator = Column(String(128))
    modify_time = Column(DateTime)
    advice_fta_def_id = Column(Integer, nullable=True, default=0)
    alarminstance_id = Column(Integer, nullable=True, default=0)
    offline_handle = Column(String(32), default='no')


class FtaSolutionsAppAdvicedef(Base):
    __tablename__ = 'fta_solutions_app_advicedef'

    id = Column(Integer, primary_key=True)
    codename = Column(String(128), nullable=False)
    description = Column(String, nullable=False)
    is_enabled = Column(Integer, nullable=False)
    cc_biz_id = Column(Integer, nullable=False)
    subject_type = Column(String(64), nullable=False)
    check_type = Column(String(64), nullable=False)
    check_sub_type = Column(String(128), nullable=False)
    interval = Column(Integer, nullable=False)
    threshold = Column(Integer, nullable=False)
    advice_type = Column(String(64), nullable=False)
    advice = Column(String, nullable=False)
    create_time = Column(DateTime, nullable=False)


class FtaSolutionsAppAlarmdef(Base):
    __tablename__ = 'fta_solutions_app_alarmdef'

    id = Column(Integer, primary_key=True)
    is_enabled = Column(Integer, nullable=False)
    is_deleted = Column(Integer, nullable=False)
    category = Column(String(32), nullable=False)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    alarm_type = Column(String(128), nullable=False)
    tnm_attr_id = Column(String)
    reg = Column(String(255))
    process = Column(String(255))
    module = Column(String, nullable=False)
    topo_set = Column(String, nullable=False)
    set_attr = Column(String, nullable=False)
    idc = Column(String, nullable=False)
    device_class = Column(String, nullable=False)
    responsible = Column(String(255))
    title = Column(String(128))
    description = Column(String)
    ok_notify = Column(Integer, nullable=False)
    notify = Column(String, nullable=False)
    solution_id = Column(Integer, index=True)
    timeout = Column(Integer, nullable=False)
    source_type = Column(String(32))
    alarm_attr_id = Column(String(128))
    module_names = Column(String)
    set_names = Column(String)


class FtaSolutionsAppAlarmType(Base):
    __tablename__ = 'fta_solutions_app_alarmtype'

    id = Column(Integer, primary_key=True)
    is_enabled = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=True)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    source_type = Column(String(128), nullable=False, index=True)
    alarm_type = Column(String(128), nullable=False)
    pattern = Column(String(128), nullable=False)
    description = Column(String)
    exclude = Column(String, default='')
    match_mode = Column(Integer, default=0)


class FtaSolutionsAppAlarminstance(Base):
    __tablename__ = 'fta_solutions_app_alarminstance'

    id = Column(Integer, primary_key=True)
    alarm_def_id = Column(Integer, nullable=False, index=True)
    source_type = Column(String(32))
    source_id = Column(String(255), index=True)
    event_id = Column(String(255), unique=True)
    ip = Column(String(30))
    raw = Column(String, nullable=False)
    status = Column(String(30), index=True)
    failure_type = Column(String(30))
    tnm_alarm = Column(String)
    tnm_alarm_id = Column(String(30), unique=True)
    inc_alarm_id = Column(String(30))
    uwork_id = Column(String(30))
    bpm_task_id = Column(String(30))
    comment = Column(String)
    source_time = Column(DateTime, index=True)
    begin_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    priority = Column(Integer, nullable=False, index=True, default=1)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    alarm_type = Column(String(128), nullable=False, index=True)
    solution_type = Column(String(128), index=True)
    snap_alarm_def = Column(String)
    snap_solution = Column(String)
    cc_topo_set = Column(String(128), nullable=False, index=True)
    cc_app_module = Column(String(128), nullable=False, index=True)
    origin_alarm = Column(String)
    approved_user = Column(String(128))
    approved_time = Column(DateTime)
    approved_comment = Column(String(128))
    level = Column(Integer, nullable=False, index=True, default=1)
    finish_time = Column(DateTime)


class FtaSolutionsAppAlarminstanceBackup(Base):
    __tablename__ = 'fta_solutions_app_alarminstancebackup'

    id = Column(Integer, primary_key=True)
    alarm_def_id = Column(Integer, nullable=False, index=True)
    source_type = Column(String(32))
    source_id = Column(String(255), index=True)
    event_id = Column(String(255), unique=True)
    ip = Column(String(30))
    raw = Column(String, nullable=False)
    status = Column(String(30), index=True)
    failure_type = Column(String(30))
    tnm_alarm = Column(String)
    tnm_alarm_id = Column(String(30), unique=True)
    inc_alarm_id = Column(String(30))
    uwork_id = Column(String(30))
    bpm_task_id = Column(String(30))
    comment = Column(String)
    source_time = Column(DateTime, index=True)
    begin_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    priority = Column(Integer, nullable=False, index=True)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    alarm_type = Column(String(128), nullable=False, index=True)
    solution_type = Column(String(128), index=True)
    snap_alarm_def = Column(String)
    snap_solution = Column(String)
    cc_topo_set = Column(String(128), nullable=False, index=True)
    cc_app_module = Column(String(128), nullable=False, index=True)
    origin_alarm = Column(String)
    approved_user = Column(String(128))
    approved_time = Column(DateTime)
    approved_comment = Column(String(128))
    level = Column(Integer, nullable=False, index=True)
    finish_time = Column(DateTime)


class FtaSolutionsAppAlarminstancearchive(Base):
    __tablename__ = 'fta_solutions_app_alarminstancearchive'
    __table_args__ = (
        Index('fta_solutions_app_alarminstancearchi_date_78c35a10ad17e6e8_uniq', 'date', 'cc_biz_id', 'biz_team',
              'is_success', 'alarm_type', 'failure_type', 'solution_type', 'source_type', 'is_off_time', unique=True),
    )

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    cc_biz_id = Column(SmallInteger, nullable=False, index=True)
    biz_team = Column(String(128), nullable=False, index=True)
    is_success = Column(Integer, nullable=False, index=True)
    alarm_type = Column(String(128), nullable=False, index=True)
    failure_type = Column(String(32), index=True)
    solution_type = Column(String(32), index=True)
    source_type = Column(String(32), index=True)
    is_off_time = Column(Integer, nullable=False, index=True)
    sub_count = Column(Integer, nullable=False)
    sub_consumed = Column(Integer, nullable=False)
    sub_profit = Column(Integer, nullable=False)
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=False)


class FtaSolutionsAppAlarminstancelog(Base):
    __tablename__ = 'fta_solutions_app_alarminstancelog'

    id = Column(Integer, primary_key=True)
    alarm_instance_id = Column(Integer, nullable=False, index=True)
    content = Column(String, nullable=False)
    time = Column(DateTime, nullable=False)
    step_name = Column(String(32))
    level = Column(SmallInteger)


class FtaSolutionsAppBizconf(Base):
    __tablename__ = 'fta_solutions_app_bizconf'

    id = Column(Integer, primary_key=True)
    cc_biz_id = Column(Integer, nullable=False, unique=True)
    tnm_servicegroup_id = Column(Integer, unique=True)
    responsible = Column(String(512))
    online_data_source_host = Column(String(15))


class FtaSolutionsAppConf(Base):
    __tablename__ = 'fta_solutions_app_conf'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    value = Column(String, nullable=False)


class FtaSolutionsAppContext(Base):
    __tablename__ = 'fta_solutions_app_context'
    __table_args__ = (
        Index('fta_solutions_app_context_key_479774ab6f8ce62c_uniq',
              'key', 'field', unique=True),
    )

    id = Column(Integer, primary_key=True)
    key = Column(String(128), nullable=False, index=True)
    field = Column(String(128), nullable=False)
    value = Column(String, nullable=False)
    created_on = Column(DateTime)
    updated_on = Column(DateTime, index=True)


class FtaSolutionsAppDatachanglog(Base):
    __tablename__ = 'fta_solutions_app_datachanglog'

    id = Column(Integer, primary_key=True)
    change_model = Column(String(100), nullable=False)
    change_id = Column(Integer, nullable=False)
    change_time = Column(DateTime, nullable=False)
    change_type = Column(String(20), nullable=False)
    new = Column(String)
    username = Column(String(30), nullable=False)


class FtaSolutionsAppEagleeye(Base):
    __tablename__ = 'fta_solutions_app_eagleeye'

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, nullable=False, index=True)
    eagle_eye_orderno = Column(String(128), nullable=False, index=True)
    data_type = Column(String(32))


class FtaSolutionsAppIgnorealarm(Base):
    __tablename__ = 'fta_solutions_app_ignorealarm'

    id = Column(Integer, primary_key=True)
    cc_biz_id = Column(Integer, nullable=False)
    alarm_type = Column(String(255))
    attr_id = Column(String(512))
    cc_module = Column(String(512))
    note = Column(String, nullable=False)


class FtaSolutionsAppIncRelatedAlarm(Base):
    __tablename__ = 'fta_solutions_app_increlatedalarm'

    id = Column(Integer, primary_key=True)
    orderno = Column(String(255), unique=True)
    trigger_orderno = Column(String(255))
    product_id = Column(String(255))
    server_ip = Column(String(255))
    category_id = Column(Integer)
    archive = Column(String(255), index=True)
    level = Column(Integer)
    trigger_start_time = Column(DateTime, index=True)
    trigger_end_time = Column(DateTime)
    content = Column(String(512))
    affect = Column(String(512))
    strategy = Column(String(512))
    remark = Column(String(512))
    url = Column(String(512))
    responsible_people = Column(String(512))
    trigger_fault = Column(Integer)
    trigger_description = Column(String(512))
    ticket_type = Column(Integer)
    ticket_name = Column(String(512))
    ticket_no = Column(String(512))
    ticket_url = Column(String(512))
    ticket_description = Column(String(512))
    ticket_reason = Column(String(512))
    ticket_summary = Column(String(512))


class FtaSolutionsAppIncident(Base):
    __tablename__ = 'fta_solutions_app_incident'

    id = Column(Integer, primary_key=True)
    is_visible = Column(Integer, nullable=False)
    incident_def_id = Column(Integer, nullable=False, index=True)
    incident_type = Column(String(128), index=True)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    dimension = Column(String(128), nullable=False, unique=True)
    description = Column(String, nullable=False)
    content = Column(String, nullable=False)
    detail = Column(String)
    last_check_time = Column(DateTime, nullable=False)
    begin_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    notify_status = Column(String(4))


class FtaSolutionsAppIncidentalarm(Base):
    __tablename__ = 'fta_solutions_app_incidentalarm'
    __table_args__ = (
        Index('fta_solutions_app_incidentala_incident_id_7885b719f404a6c5_uniq',
              'incident_id', 'alarm_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, nullable=False, index=True)
    alarm_id = Column(Integer, nullable=False, index=True)
    is_primary = Column(Integer, nullable=False)


class FtaSolutionsAppIncidentdef(Base):
    __tablename__ = 'fta_solutions_app_incidentdef'
    __table_args__ = (
        Index('fta_solutions_app_incidentdef_cc_biz_id_5b78b22401899362_uniq',
              'cc_biz_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    is_enabled = Column(Integer, nullable=False)
    cc_biz_id = Column(Integer, nullable=False)
    codename = Column(String(128), nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    rule = Column(String, nullable=False)
    exclude = Column(String)


class FtaSolutionsAppKpicache(Base):
    __tablename__ = 'fta_solutions_app_kpicache'
    __table_args__ = (
        Index('fta_solutions_app_kpicache_date_24e23487f48f6a0e_uniq',
              'date', 'cc_biz_id', 'kpi_type', unique=True),
    )

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    kpi_type = Column(Integer, nullable=False)
    tnm_total = Column(Integer, nullable=False)
    tnm_covered = Column(Integer, nullable=False)
    tnm_success = Column(Integer, nullable=False)


class FtaSolutionsAppOutofscopearchive(Base):
    __tablename__ = 'fta_solutions_app_outofscopearchive'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)

    status = Column(String, default=True, index=True)

    cc_biz_id = Column(Integer, nullable=False, index=True)
    alarm_type = Column(String(255), nullable=False, index=True)
    cc_module = Column(String(128), index=True)
    cc_set_name = Column(String(128), index=True)
    sub_count = Column(Integer, nullable=False)
    extra = Column(String, nullable=True)


class FtaSolutionsAppSolution(Base):
    __tablename__ = 'fta_solutions_app_solution'

    id = Column(Integer, primary_key=True)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    solution_type = Column(String(128), nullable=False)
    codename = Column(String(128))
    title = Column(String(512), nullable=False)
    creator = Column(String(255), nullable=False)
    config = Column(String)


class FtaSolutionsAppUserbiz(Base):
    __tablename__ = 'fta_solutions_app_userbiz'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    cc_biz_id = Column(Integer, nullable=False)


class FtaSolutionsAppWorld(Base):
    __tablename__ = 'fta_solutions_app_world'

    id = Column(Integer, primary_key=True)
    is_enabled = Column(Integer, nullable=False)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    cc_set_name = Column(String(30), nullable=False)
    cc_set_chn_name = Column(String(30), nullable=False)
    world_id = Column(String(30), nullable=False)
    tnm_attr_id = Column(String(30))
    tnm_attr_name = Column(String(255))
    comment = Column(String)
    online_data_source_host = Column(String(15))


class FtaSolutionsAppApproveCallback(Base):
    __tablename__ = 'fta_solutions_app_approvecallback'

    id = Column(Integer, primary_key=True)
    alarm_id = Column(Integer, nullable=False)
    node_idx = Column(Integer, nullable=False)
    obj_id = Column(Integer, nullable=False)
    approval = Column(Integer, nullable=False)
    reason = Column(String(255))
    approver = Column(String(255))


class SouthMigrationhistory(Base):
    __tablename__ = 'south_migrationhistory'

    id = Column(Integer, primary_key=True)
    app_name = Column(String(255), nullable=False)
    migration = Column(String(255), nullable=False)
    applied = Column(DateTime, nullable=False)


class TastypieApiacces(Base):
    __tablename__ = 'tastypie_apiaccess'

    id = Column(Integer, primary_key=True)
    identifier = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    request_method = Column(String(10), nullable=False)
    accessed = Column(Integer, nullable=False)


class TastypieApikey(Base):
    __tablename__ = 'tastypie_apikey'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, unique=True)
    key = Column(String(256), nullable=False)
    created = Column(DateTime, nullable=False)

    user = relationship(u'AuthUser')


class WechatApponlineattrrelationship(Base):
    __tablename__ = 'wechat_apponlineattrrelationship'

    id = Column(Integer, primary_key=True)
    cc_biz_id = Column(Integer, nullable=False)
    tnm_attr_id = Column(Integer, nullable=False, unique=True)
    tnm_attr_name = Column(String(256), nullable=False)
    show_num = Column(Integer, nullable=False)
    is_star = Column(Integer, nullable=False)


class WechatAppotherattrrelationship(Base):
    __tablename__ = 'wechat_appotherattrrelationship'

    id = Column(Integer, primary_key=True)
    cc_biz_id = Column(Integer, nullable=False)
    tnm_attr_id = Column(Integer, nullable=False, unique=True)
    tnm_attr_name = Column(String(256), nullable=False)
    tnm_attr_ip = Column(String(256))
    is_star = Column(Integer, nullable=False)


# class WechatApprove(Base):
#     __tablename__ = 'wechat_approve'
#
#     id = Column(Integer, primary_key=True)
#     task_id = Column(Integer, nullable=False)
#     message = Column(String, nullable=False)
#     approved_user = Column(String(128))
#     approved_time = Column(DateTime)
#     approved_comment = Column(String(128))
#     approved_result = Column(String(128))

class WechatApprove(Base):
    __tablename__ = 'wechat_approve'

    id = Column(Integer, primary_key=True)

    obj_id = Column(String(255), nullable=True)
    message = Column(String, nullable=False)
    callback_url = Column(String, nullable=True)
    status = Column(String(32), default='WAITING')

    approve_users = Column(String, nullable=True)

    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class WechatUserapprelationship(Base):
    __tablename__ = 'wechat_userapprelationship'
    __table_args__ = (
        Index('wechat_userapprelationship_username_260dae9e314169d8_uniq',
              'username', 'cc_biz_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    cc_biz_id = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)


class QcloudOwnerInfo(Base):
    __tablename__ = 'fta_solutions_app_qcloudownerinfo'
    id = Column(Integer, primary_key=True)
    owner_uin = Column(String(50), nullable=False, unique=True)
    qcloud_app_id = Column(String(50), nullable=False)


class AlarmApplication(Base):
    __tablename__ = 'fta_solutions_app_alarmapplication'

    id = Column(Integer, primary_key=True)
    source_type = Column(String(64), nullable=False)
    cc_biz_id = Column(Integer, nullable=False, index=True)
    app_name = Column(String(255), nullable=False)

    # ID默认生成UUID
    app_id = Column(String(255), nullable=False, unique=True)
    # 生成Secret
    app_secret = Column(String(255), nullable=False, unique=True)

    # 创建时间，人
    create_time = Column(DateTime, nullable=False)
    create_user = Column(String(128), nullable=False)

    # 修改时间，人
    update_time = Column(DateTime, nullable=False)
    update_user = Column(String(128), nullable=False)

    # 上报时间
    activate_time = Column(DateTime, nullable=True, default=None)

    # 开关项
    is_enabled = Column(Integer, nullable=False)
    is_deleted = Column(Integer, nullable=False)

    extra = Column(String, nullable=True)
    exclude = Column(String, default="", nullable=True)

    # 自定义监控配置项
    app_url = Column(String, nullable=True)
    app_method = Column(String(10), nullable=True)
    # 记录监控源异常信息
    exception_max_num = Column(Integer, default=0, nullable=True)
    exception_num = Column(Integer, default=0, nullable=True)
    exception_data = Column(String, default='', nullable=True)
    exception_begin_time = Column(DateTime, nullable=True)
    empty_num = Column(Integer, default=0, nullable=True)
    empty_begin_time = Column(DateTime, nullable=True)


class AdviceFtaDef(Base):
    __tablename__ = 'fta_solutions_app_adviceftadef'

    id = Column(Integer, primary_key=True)
    advice_def_id = Column(Integer, nullable=False, index=True)

    is_enabled = Column(Integer, nullable=False)
    is_deleted = Column(Integer, nullable=False)
    cc_biz_id = Column(Integer, nullable=False, index=True)

    module = Column(String, nullable=False)
    topo_set = Column(String, nullable=False)
    module_names = Column(String)
    set_names = Column(String)

    responsible = Column(String(255))
    title = Column(String(128))
    description = Column(String)
    notify = Column(String, nullable=False)
    solution_id = Column(Integer, index=True)
    timeout = Column(Integer, nullable=False)

    exclude = Column(String, nullable=True)
    handle_type = Column(String(10))
