# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging
from datetime import datetime

from fta import settings
from fta.storage.mysql import session
from fta.storage.tables import AlarmApplication
from fta.utils import send
from fta.utils.i18n import _
from project.utils.component import bk

logger = logging.getLogger(__name__)


def get_cc_biz_id_by_app(fta_application_id):
    """通过fta_application_id获取cc_id
    """
    app = session.query(AlarmApplication).filter_by(
        app_id=fta_application_id, is_enabled=True, is_deleted=False).first()
    if app:
        return app.cc_biz_id
    else:
        return None


def get_custom_app_info():
    """获取自定义监控源的相关信息
    """
    app = session.query(AlarmApplication).filter_by(
        cc_biz_id=0,
        source_type='Custom',
        is_deleted=False,
        is_enabled=True).first()
    app_info = {}
    if app:
        app_info = {
            'app_url': app.app_url,
            'app_method': app.app_method,
            'app_id': app.id,
        }
    return app_info


def get_bkmonitor_app_info():
    """获取蓝鲸监控源的相关信息
    """
    app = session.query(AlarmApplication).filter_by(
        cc_biz_id=0,
        source_type='ALERT',
        is_deleted=False,
        is_enabled=True).first()
    app_info = {}
    if app:
        app_info = {
            'app_url': app.app_url,
            'app_method': app.app_method,
            'app_id': app.id,
        }
    return app_info


def handle_alarm_source_exception(alarm_app_id, exception_data):
    """
    处理告警源拉取告警异常的情况
    1）原有异常次数 exception_num 为 0 时，记录异常起始时间 exception_begin_time
    2）异常次数 exception_num +1
    3) 记录异常信息到 exception_data 字段
    4）空告警次数 empty_num 还原为 0
    5）超过异常阈值时，禁用该告警源
    """
    alarm_app = session.query(
        AlarmApplication).filter_by(id=alarm_app_id).first()
    if alarm_app:
        exception_num_before = alarm_app.exception_num
        if exception_num_before == 0:
            alarm_app.exception_begin_time = datetime.utcnow()

        cur_exception_num = exception_num_before + 1
        alarm_app.exception_num = cur_exception_num
        alarm_app.exception_data = exception_data
        # 更新空告警次数
        alarm_app.empty_num = 0

        # 超过异常阈值时，禁用该告警源, 0则表示不设阈值
        if (alarm_app.exception_max_num and
                cur_exception_num > alarm_app.exception_max_num):
            alarm_app.is_enabled = False
            # 邮件通知相关人员
            receiver_list = []
            for _user in [alarm_app.create_user, alarm_app.update_user]:
                if _user and _user not in receiver_list:
                    receiver_list.append(_user)
            if receiver_list:
                message = _(
                    "From [%(begin_time)s] from the time"
                    "Continuous [%(exception_num)s] from [%(source_type)s] alarm source pulls alarm anomalies. <br/>. "
                    "Pull alarm from this source has been suspended. <br/>. "
                    'Please visit <a href="%(app_url)s">[Management alarm source]</a>'
                    "page checks that your configuration item is correct! The <br/> exception message is: %(exception_msg)s",  # noqa
                    begin_time=alarm_app.exception_begin_time.strftime('%Y-%m-%d %H:%M:%S'),
                    exception_num=alarm_app.exception_num,
                    source_type=alarm_app.source_type,
                    app_url=settings.APP_URL_PROD,
                    exception_msg=alarm_app.exception_data
                )
                title = _(
                    "[Fault Auto-recovery Notification] pulled alarm error from [%(source_type)s] alarm source",
                    source_type=alarm_app.source_type)
                send.mail_app_user(
                    ','.join(receiver_list),
                    message,
                    title=title
                )
        session.flush()


def handle_alarm_source_empty(alarm_app_id):
    """
    处理拉取告警为空的情况
    1）空告警次数 empty_num 为 0 时，记录异常起始时间 empty_begin_time
    2）空告警次数 empty_num +1
    3）异常次数 exception_num 还原为 0
    """
    alarm_app = session.query(
        AlarmApplication).filter_by(id=alarm_app_id).first()
    if alarm_app:
        empty_num_before = alarm_app.empty_num
        if empty_num_before == 0:
            alarm_app.empty_begin_time = datetime.utcnow()
        alarm_app.empty_num = empty_num_before + 1
        # 更新异常次数
        alarm_app.exception_num = 0
        session.flush()


def handle_alarm_source_success(alarm_app_id):
    """
    处理拉取告警正常的情况
    1）异常次数 exception_num 还原为 0
    2）空告警次数 empty_num 还原为 0
    """
    alarm_app = session.query(
        AlarmApplication).filter_by(id=alarm_app_id).first()
    if alarm_app:
        alarm_app.exception_num = 0
        alarm_app.exception_data = ''
        alarm_app.exception_begin_time = ''
        alarm_app.empty_num = 0
        alarm_app.empty_begin_time = ''
        session.flush()


# ################# 自定义监控，只根据IP查询配置平台相关信息 ##################
def get_ips_info(ip_list):
    """
    根据 ip 信息 查询对用的 cc 信息
    """
    kwargs = {
        "ips": ','.join(ip_list),
    }
    cc_result = bk.cc.get_host_company_id(**kwargs)
    ip_dict = {}
    for ip in cc_result:
        ip_info_list = cc_result[ip].values()
        for item in ip_info_list:
            ip_dict[ip] = {
                'owenr': item['Owner'],
                'cc_company_id': item['CompanyID'],
                'cc_plat_id': item['PlatID'],
                'cc_biz_id': item['ApplicationID']
            }
    return ip_dict


def get_cc_info_by_ips(ip_list):
    # 跟IP 查询相关的 ApplicationID、PlatID、CompanyID
    # ip_list 为空时则直接返回空字典，不查询cc
    if not ip_list:
        return {}
    ip_dict = get_ips_info(ip_list)
    cc_info_dict = {}
    for ip in ip_dict:
        # 根据 CompanyID + PlatID + ip 查询cc信息
        ip_info = ip_dict.get(ip)
        plat_id = ip_info.get('cc_plat_id')
        company_id = ip_info.get('cc_company_id')
        cc_info = bk.cc.get_host_by_company_id(
            plat_id=plat_id, company_id=company_id, ip=ip)

        cc_info_dict[ip] = {
            'cc_company_id': company_id,
            'cc_plat_id': plat_id,
            'cc_biz_id': ip_info.get('cc_biz_id'),
            'owenr': ip_info.get('owner'),
            'cc_app_module_id': cc_info.get('ModuleID'),
            'cc_app_module_name': cc_info.get('ModuleName'),
            'cc_topo_set_id': cc_info.get('SetID'),
            'cc_topo_set_name': cc_info.get('SetName'),
        }
    return cc_info_dict


def query_match_machine(app_id, match_dict):
    # 按 host 查询条件
    host_condition = []
    bk_os_type = match_dict.get('bk_os_type')
    if bk_os_type:
        host_condition.append({"field": "bk_os_type", "operator": "$eq", "value": str(bk_os_type)})

    bk_state_name = match_dict.get('bk_state_name')
    if bk_state_name:
        host_condition.append({"field": "bk_state_name", "operator": "$eq", "value": str(bk_state_name)})

    bk_province_name = match_dict.get('bk_province_name')
    if bk_province_name:
        host_condition.append({"field": "bk_province_name", "operator": "$eq", "value": str(bk_province_name)})

    # 按 set 条件查询
    set_condition = []
    set_name = match_dict.get('set_name')
    if set_name:
        set_name_list = set_name.split(',')
        set_condition.append({"field": "bk_set_name", "operator": "$in", "value": set_name_list})

    # 按 module 查询
    module_condition = []
    module_name = match_dict.get('module_name')
    if module_name:
        module_name_list = module_name.split(',')
        module_condition.append({"field": "bk_module_name", "operator": "$in", "value": module_name_list})

    kwargs = {
        "bk_biz_id": app_id,
        "condition": [
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": host_condition
            },
            {
                "bk_obj_id": "set",
                "fields": [],
                "condition": set_condition
            },
            {
                "bk_obj_id": "module",
                "fields": [],
                "condition": module_condition
            },
            {
                "bk_obj_id": "biz",
                "fields": [],
                "condition": [
                    {
                        "field": "default",
                        "operator": "$ne",
                        "value": 1
                    }
                ]
            }
        ],
        "pattern": ""
    }
    cc = bk.cc
    # 使用v2的API
    cc._prefix = 'compapi/v2'
    cc_data = cc.search_host(**kwargs)
    info = cc_data.get('info') or []

    machine_list = []
    for cc_info in info:
        cc_host = cc_info.get('host') or {}
        bk_host_innerip = cc_host.get('bk_host_innerip', '')
        bk_host_id = cc_host.get('bk_host_id', '')
        bk_host_outerip = cc_host.get('bk_host_outerip', '')

        bk_cloud_info = cc_host.get('bk_cloud_id') or []
        if not bk_cloud_info:
            continue
        bk_cloud_id = bk_cloud_info[0].get('bk_inst_id', '')

        cc_biz = cc_info.get('biz') or []
        if not cc_biz:
            continue
        bk_supplier_account = cc_biz[0].get('bk_supplier_account', '')

        cc_set = cc_info.get('set') or []
        set_name_list = [_c.get('bk_set_name', '') for _c in cc_set]
        set_id = cc_set[0].get('bk_set_id', '') if cc_set else ''

        cc_module = cc_info.get('module') or []
        module_name_list = [_c.get('bk_module_name', '') for _c in cc_module]

        machine_list.append({
            'InnerIP': bk_host_innerip,
            'CompanyID': bk_supplier_account,
            'Source': bk_cloud_id,
            'HostID': bk_host_id,
            'OuterIP': bk_host_outerip,
            'SetID': set_id,
            'SetName': ','.join(set_name_list),
            'ModuleName': ','.join(module_name_list)
        })
    return machine_list
