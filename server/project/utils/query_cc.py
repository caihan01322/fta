# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from project.utils.component import bk

from fta.storage.mysql import session
from fta.storage.tables import AlarmApplication
from fta.utils import logging
from fta.utils.decorator import func_cache, try_exception
from fta.utils.i18n import _

logger = logging.getLogger("query_cc")


@try_exception(exception_return=[])
@func_cache(60 * 10)
def get_app_host_list(app_id):
    """
    获取指定业务所有主机信息
    :param app_id
    :return dict: {"InnerIP": host_info}
    """
    cc_result = bk.cc.get_app_host_list(app_id=app_id)
    return cc_result


@try_exception(exception_return={})
@func_cache(60 * 60)
def get_plat_name():
    """获取所有平台ID与平台名的映射"""
    plat_info = {}
    res = bk.cc.get_plat_id()
    for plat in res:
        plat_id = int(plat['plat_id'])
        plat_info[plat_id] = plat['plat_name']
    return plat_info


@try_exception(exception_return={})
@func_cache(60 * 10)
def get_app_by_id(app_id):
    """
    查询业务信息
    :param app_id
    :return dict: {host_info}
    """
    if app_id:
        cc_result = bk.cc.get_app_by_id(app_id=app_id)
        if cc_result:
            return cc_result[0]
    return {}


@try_exception(exception_return=[])
@func_cache(60 * 10)
def get_open_region_biz_info(inner_ip):
    """获取公有区域机器所属平台,开发商和业务, 一台机器可能属于多个业务
    :param inner_ip 内网IP
    :return [{'PlatID':xx, 'CompanyID':xx, 'ApplicationID'}, ...]
    """
    res = bk.cc.get_host_company_id(ips=inner_ip)
    if inner_ip not in res:
        return []
    return res[inner_ip].values()


@try_exception(exception_return={})
@func_cache(60 * 10)
def batch_get_open_region_biz_info(inner_ip_list):
    """获取公有区域机器所属平台,开发商和业务, 一台机器可能属于多个业务
    :param inner_ip_list 内网IP列表
    :return [{'PlatID':xx, 'CompanyID':xx, 'ApplicationID'}, ...]
    :return {inner_ip: [{'PlatID':xx, 'CompanyID':xx, 'ApplicationID'}, ...]}
    """
    res = bk.cc.get_host_company_id(ips=",".join(inner_ip_list))
    _data = {}
    for inner_ip in inner_ip_list:
        _data[inner_ip] = res[inner_ip].values()
    return _data


@try_exception(exception_return={})
@func_cache(60 * 10)
def get_host_by_company_id(plat_id, company_id, inner_ip):
    res = bk.cc.get_host_by_company_id(plat_id=plat_id, company_id=company_id, ip=inner_ip)
    return res or {}


@try_exception(exception_return={})
@func_cache(60 * 10)
def get_host_list_by_ip(app_id, ip):
    """
    根据业务ID和IP查询该IP对应的所有主机信息
    :param app_id 业务ID
    :param ip  内网IP
    :return {plat_id: host_info_with_company_id}
    """
    resp = bk.cc.get_host_list_by_ip(app_id=app_id, ip=ip)
    result = {}
    for info in resp:
        inner_ip = info['InnerIP']
        host_info = result.get(inner_ip)
        if host_info:
            for k, v in host_info.items():
                value = info[k]
                if v == value:
                    continue
                if isinstance(v, basestring):
                    info[k] = "%s,%s" % (v, value)
        result[inner_ip] = info

    return result


@try_exception(exception_return={})
def get_host_info(plat_id, company_id, ip):
    """
    查询根据平台,开发商,IP查询主机详细信息
    返回的主机维护人和备份维护人可能为空
    :param plat_id 平台ID
    :param company_id 开发商ID
    :param inner_ip 内网IP
    :return {'ApplicationID': xx, 'ApplicationName': xx, 'ModuleName': xx
            'ModuleID': xx, 'SetName': xx, 'SetID': xx,
            'Operator': xx, 'BakOperator': xx, 'AssetID': xx, 'Region': xx, ...}
    """
    if not ip:
        return {}
    res = get_host_by_company_id(plat_id, company_id, ip)
    if not res:
        return {}
    app_id = res['ApplicationID']
    host_list = get_app_host_list(app_id)
    host_info = {}
    for host in host_list:
        # 一台主机可能属于多个set和module
        if host['Source'] == str(plat_id) and host['InnerIP'] == ip:
            if not host_info:
                host_info = host
                host_info['ApplicationID'] = res['ApplicationID']
                host_info['ApplicationName'] = res['ApplicationName']
            else:
                host_info['SetID'] = ','.join(set(host_info['SetID'].split(',') + [host['SetID']]))
                host_info['SetName'] = ','.join(set(host_info['SetName'].split(',') + [host['SetName']]))
                host_info['ModuleID'] = ','.join(set(host_info['ModuleID'].split(',') + [host['ModuleID']]))
                host_info['ModuleName'] = ','.join(set(host_info['ModuleName'].split(',') + [host['ModuleName']]))
    return host_info


def get_plat_host_info(plat_id, company_id, inner_ip):
    """
    查询根据平台,开发商,IP查询主机信息
    :param plat_id 平台ID
    :param company_id 开发商ID
    :param inner_ip 内网IP
    :return {'ApplicationID': xx, 'ApplicationName': xx, 'ModuleName': xx
            'ModuleID': xx, 'SetName': xx, 'SetID': xx,
            'Operator': xx, 'BakOperator': xx}
    """
    return get_host_by_company_id(plat_id, company_id, inner_ip)


@try_exception(exception_return="--")
def get_host_brief_info(plat_id, company_id, inner_ip):
    if not inner_ip:
        return u'(--)'
    host_info = get_plat_host_info(plat_id, company_id, inner_ip)
    if host_info:
        set_name = host_info.get('SetName')
        module_name = host_info.get('ModuleName')
        return u'(%s-%s)' % (_(set_name), _(module_name))
    return u'(--)'


@try_exception(exception_return="")
def get_cc_biz_responsible(app_id):
    """
    查询 cc 业务运维
    :param app_id
    :return unicode: "qq1;qq2"
    """
    app_info = get_app_by_id(app_id)
    return app_info.get('Maintainers', "")


def get_cc_biz_attr(app_id, attr):
    """
    查询 cc 业务的指定属性
    :param app_id
    :param attr: 任意存在的主机属性
    :return unicode: 属性值
    """
    app_info = get_app_by_id(app_id)
    return app_info.get(attr)


def get_cc_ip_responsible(plat_id, company_id, inner_ip):
    """
    查询 主机 运维, 返回列表格式
    :param plat_id
    :param company_id
    :param inner_ip
    :return list: [qq1, qq2]
    """
    if not inner_ip:
        return []
    responsible = []
    host_info = get_plat_host_info(plat_id, company_id, inner_ip)
    operator = host_info.get('Operator')
    bak_operator = host_info.get('BakOperator')
    # Operator 及 BakOperator 字段都可能为空
    if operator:
        responsible.append(operator)
    if bak_operator:
        responsible.append(bak_operator)
    return responsible


@try_exception(exception_return=[])
@func_cache(60 * 10)
def get_modules_by_appid(app_id):
    """
    查询业务下的所有模块信息
    注意：企业版使用get_modules_by_property代替
    """
    cc_data = bk.cc.get_modules_by_property(app_id=app_id)
    return cc_data


def get_module_id_by_name(app_id, module_name):
    """
    根据模块名称获取模块id
    """
    cc_data = get_modules_by_appid(app_id)
    for data in cc_data:
        if data.get('ModuleName') == module_name:
            return data.get('ModuleID')
    return ''


@try_exception(exception_return=[])
@func_cache(60 * 10)
def get_sets_by_appid(app_id):
    """
    查询业务下的所有模块信息
    """
    cc_data = bk.cc.get_sets_by_property(app_id=app_id)
    return cc_data


def get_set_id_by_name(app_id, set_name):
    """
    根据模块名称获取模块id
    """
    cc_data = get_sets_by_appid(app_id)
    for data in cc_data:
        if data.get('SetName') == set_name:
            return data.get('SetID')
    return ''


def get_app_name(app_id):
    app_info = get_app_by_id(app_id)
    return app_info['ApplicationName']


@try_exception(exception_return=[])
def get_agent_abnor_list(app_id):
    """
    查询业务下的所有模块信息
    """
    cc_data = bk.cc.get_app_agent_status(app_id=app_id)
    agent_abnor_list = cc_data.get('agentNorList') or []
    ip_list = ['%s_%s_%s' % (agent['Ip'], agent['CompanyId'], agent['PlatId']) for agent in agent_abnor_list]
    return ip_list


# ################# 二次封装的cc接口，不再加缓存 ##################

def get_host_info_by_ip(cc_biz_id, ip):
    """根据业务ID和IP，查询主机set, module信息，返回全部信息，做告警快照使用
    """
    host_info = get_host_list_by_ip(cc_biz_id, ip)
    if ip in host_info:
        return host_info[ip]
    return {}


def get_company_info_by_ip(cc_biz_id, ip):
    """根据业务ID和IP，查询company_id和plat_id信息
    """
    company_info = get_open_region_biz_info(ip)
    for info in company_info:
        if str(info['ApplicationID']) == str(cc_biz_id):
            return info
    return {}


def get_all_info_by_ip(cc_biz_id, ip):
    """一次性获取主机，Company信息
    """
    data = {}
    host_info = get_host_info_by_ip(cc_biz_id, ip)
    company_info = get_company_info_by_ip(cc_biz_id, ip)
    data.update(host_info)
    data.update(company_info)
    return data


@func_cache(60 * 10)
def get_cc_info_by_ip(cc_biz_id, ip):
    """
    根据 ip 查询 机器 的 set 和 module 信息
    """
    kwargs = {
        "app_id": cc_biz_id,
        "ip": ip
    }
    cc_data = bk.cc.get_host_list_by_ip(**kwargs)

    cc_info_dict = {}
    if isinstance(cc_data, list):
        info = cc_data[0]
        cc_info_dict = {
            'cc_app_module': info['ModuleID'],
            'cc_app_module_name': info['ModuleName'],
            'cc_topo_set': info['SetID'],
            'cc_topo_set_name': info['SetName'],
            'cc_biz_name': info['ApplicationName'],
            'cc_status': info['Status'],
        }
    return cc_info_dict


# ################# 从db中获取数据 ##################
def get_cc_biz_id_by_app(fta_application_id):
    """
    通过fta_application_id获取cc_id
    """
    app = session.query(AlarmApplication).filter_by(
        app_id=fta_application_id,
        is_deleted=False,
        is_enabled=True).first()
    if app:
        return app.cc_biz_id
    else:
        return None


@func_cache(60 * 10)
def get_ip_by_hostname(hostname):
    """
    通过hostname或者主机IP
    """
    kwargs = {
        "condition": [{
            "bk_obj_id": "host",
            "fields": [],
            "condition": [{
                'field': 'bk_host_name',
                'value': hostname,
                'operator': '$eq'
            }]
        }],
        "page": {
            "start": 0,
            "limit": 100,
            "sort": "bk_host_name"
        },
        "pattern": ""
    }
    cc = bk.cc
    # 使用v2的API
    cc._prefix = 'compapi/v2'
    cc_data = cc.search_host(**kwargs)
    info = cc_data.get('info') or []
    host = [i['host']['bk_host_innerip'] for i in info]

    return host


@func_cache(60 * 10)
def get_ip_by_sn(sn):
    """通过SN获取主机IP
    """
    kwargs = {
        "condition": [{
            "bk_obj_id": "host",
            "fields": [],
            "condition": [{
                'field': 'bk_sn',
                'value': sn,
                'operator': '$eq'
            }]
        }],
        "page": {
            "start": 0,
            "limit": 100,
            "sort": "bk_host_name"
        },
        "pattern": ""
    }
    cc = bk.cc
    # 使用v2的API
    cc._prefix = 'compapi/v2'
    cc_data = cc.search_host(**kwargs)
    info = cc_data.get('info') or []
    host = [i['host']['bk_host_innerip'] for i in info]
    return host
