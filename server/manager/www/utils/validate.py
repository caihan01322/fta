# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""CC验证相关
"""
from fta.utils.i18n import _
from fta.www.utils.validate import ValidateError
from project.utils import query_cc


def is_cc_uniq_hostname(data, hostname, replace=True):
    """是否是CC的主机信息
    """
    ip = query_cc.get_ip_by_hostname(hostname)

    if not ip:
        raise ValidateError(_('CC failed to query [%(hostname)s] host information', hostname=hostname))

    if len(ip) > 1:
        raise ValidateError(
            _('CC get multi ip for hostname [%(hostname)s], Please ensure that the hostname is unique',
              hostname=hostname))

    ip = ip[0]
    if replace:
        data['_CC_HOST_INNER_IP'] = ip

    return data


def is_cc_uniq_company(data, ip, replace=True):
    """验证是否唯一开发商信息
    """
    company_info = query_cc.batch_get_open_region_biz_info([ip]).get(ip) or []
    if not company_info:
        raise ValidateError(_('CC failed to query [%(ip)s] developer company information', ip=ip))

    if len(company_info) > 1:
        raise ValidateError(
            _('CC get multi developer company info for ip [%(ip)s], Please ensure that the ip is unique',
              ip=ip))

    info = company_info[0]
    if replace:
        data['_CC_COMPANY_INFO'] = info

    return data


def is_cc_uniq_sn(data, sn, replace=True):
    """验证是否是唯一SN
    """
    ip = query_cc.get_ip_by_sn(sn)

    if not ip:
        raise ValidateError(_('CC failed to query [%(sn)s] host information', sn=sn))

    if len(ip) > 1:
        raise ValidateError(
            _('CC get multi ip for sn [%(sn)s], Please ensure that the sn is unique',
              sn=sn))

    ip = ip[0]
    if replace:
        data['_CC_HOST_INNER_IP'] = ip
    return data


def is_cc_host(data, cc_biz_id, ip, replace=True):
    host_info = query_cc.get_host_info_by_ip(cc_biz_id, ip)
    if not host_info:
        raise ValidateError(_('CC failed to query [%(ip)s] host information', ip=ip))
    if replace:
        data['_CC_HOST_INFO'] = host_info
    return data


def is_cc_company(data, cc_biz_id, ip, replace=True):
    """验证开发商信息
    """
    company_info = query_cc.get_company_info_by_ip(cc_biz_id, ip)
    if not company_info:
        raise ValidateError(_('CC failed to query [%(ip)s] developer company information', ip=ip))
    if replace:
        data['_CC_COMPANY_INFO'] = company_info
    return data


def is_cc_sn(data, cc_biz_id, sn, replace=True):
    """验证SN号码
    """
    host_info = query_cc.get_host_info_by_sn(cc_biz_id, sn)
    if not host_info:
        raise ValidateError(_('CC failed to query [%(sn)s] host information', sn=sn))
    if replace:
        data['_CC_HOST_INFO'] = host_info
    return data
