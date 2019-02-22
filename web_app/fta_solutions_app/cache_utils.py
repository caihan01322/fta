# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from collections import defaultdict

from fta_solutions_app.models import AlarmInstanceArchive
from fta_solutions_app.models import BizConf
from fta_solutions_app.models import IncidentDef
from fta_utils.cache import web_cache
from fta_utils.cc import CCBiz
from fta_utils.component import bk
from permission.exceptions import APIError
from project.permission.utils import _get_all_user_info


def get_alert_alarm_type_api():
    res = bk.data.get_alarm_type()
    if not res.get('result', False):
        raise APIError(res.get('message', 'call component sdk error'))
    data = res['data']
    return data


def get_cc_obj_attr():
    query = {"bk_obj_id": "host", "bk_supplier_account": "0"}
    res = bk.cc.search_object_attribute(**query)
    if not res.get('result', False):
        raise APIError(res.get('message', 'call component sdk error'))
    data = res['data']
    attr_dcit = {}
    for _d in data:
        bk_property_id = _d.get('bk_property_id')
        if bk_property_id in ['bk_os_type', 'bk_state_name', 'bk_province_name']:
            attr_dcit[bk_property_id] = _d.get('option') or []
    return attr_dcit


@web_cache(60 * 5)
def _get_app_module_with_cache(cc_biz_id, username):
    """获取业务下的模块列表，按名字排序"""
    cc_result = bk.cc.get_modules_by_property(app_id=cc_biz_id)
    if not cc_result.get('result', False):
        raise APIError(cc_result.get('message', 'call component sdk error'))
    cc_data = cc_result['data']
    data = sorted(cc_data, key=lambda x: x.get('ModuleID', '').upper())  # 按字母排序
    return data


@web_cache(60 * 5)
def _get_app_topo_set_with_cache(cc_biz_id, username):
    """获取业务下的SET列表，按名字排序"""
    bk.set_username(username)
    cc_result = bk.cc.get_sets_by_property(app_id=cc_biz_id)
    if not cc_result.get('result', False):
        raise APIError(cc_result.get('message', 'call component sdk error'))
    cc_data = cc_result['data'] or []
    data = sorted(cc_data, key=lambda x: x['SetName'].upper())  # 按字母排序
    return data


@web_cache(60 * 5)
def get_app_topo_set_to_module_dict(cc_biz_id, username):
    """
    获取某业务所有业务SET->业务模块的对应关系，用来表现接入报警处的
    业务SET -> 业务模块 之间的二级菜单关系。

    :param str cc_biz_id: 业务ID
    :returns: topo set到module的对应关系dict
    """
    # 首先获取所有的SetName，方便之后做字符串匹配
    cc_result = bk.cc.get_modules_by_property(app_id=cc_biz_id)
    if not cc_result.get('result', False):
        raise APIError(cc_result.get('message', 'call component sdk error'))
    data = cc_result['data'] or []

    result = defaultdict(set)
    for row in data:
        set_id = row['SetID']
        module_id = row['ModuleID']
        result[set_id].add(module_id)

    # set转换成list方便JSON序列化
    result = dict((k, list(v)) for k, v in result.iteritems())
    return result


@web_cache(60 * 5)
def get_all_user_info(cc_biz_id, username):
    """
    当前用户所属开发商下的所有用户信息
    """
    return _get_all_user_info(username)


@web_cache(60 * 30)
def get_app_set_attr_to_topo_set_dict(cc_biz_id, username):
    """
    获取某业务所有业务SET属性->业务SET的对应关系，用来表现接入报警处的
    业务SET属性 -> 业务SET 之间的二级菜单关系。

    :param str cc_biz_id: 业务ID
    :returns: topo_set属性到topo_set的对应关系dict
    """
    bk.set_username(username)
    cc_result = bk.cc.get_sets_by_property(app_id=cc_biz_id)
    if not cc_result.get('result', False):
        raise APIError(cc_result.get('message', 'call component sdk error'))
    data = cc_result['data'] or []

    result = defaultdict(set)
    for row in data:
        result['category-%s' % row.get('Category', '')].add(row['SetID'])
        result['envi_type-%s' % row.get('EnviType', '0')].add(row['SetID'])
        result['service_state-%s' % row.get('ServiceStatus', '0')].add(row['SetID'])
    result = dict((k, list(v)) for k, v in result.iteritems())
    return result


# 告警特性缓存 begin -----------------------------------

@web_cache(48 * 60 * 60)
def _get_attr_by_id(attr_id, username):
    kwargs = {
        "attr_id": attr_id,
        "pagesize": 0
    }
    try:
        bk.set_username(username)
        result = bk.tnm2.get_attr(**kwargs)
    except Exception:
        return None
    if result:
        attr = result[0]
    else:
        return None
    return attr


@web_cache(60 * 30)
def _get_biz_attr_list(cc_biz_id, username):
    """
    查询业务自定义告警特性
    """
    return []
    bk.set_username(username)
    cc_biz_name = CCBiz(username, cc_biz_id).get("ApplicationName")
    kwargs = {
        "service_group": u"CC_%s" % cc_biz_name,
        "service": u"CC_%s" % cc_biz_name,
        "pagesize": 0
    }
    try:
        biz_attr_list = bk.tnm2.get_attr(**kwargs)
    except Exception:
        biz_attr_list = []
    # 业务自定义是不可能达到1万个的
    if len(biz_attr_list) > 10000:
        biz_attr_list = []
    return _simplify_attr_list(biz_attr_list)


def _simplify_attr_list(attr_list):
    """
    对attr_list进行简化，去掉没有用的字段。
    """
    for attr in attr_list:
        for key in attr.keys():
            if key not in ("attr_id", "attr_name", "attr_type"):
                attr.pop(key)
    return attr_list


def _get_cc_biz_by_group(username):
    """
    用于业务选择框，以小组分组
    :return dict: {team1:{biz_id_1: biz_name, ...}, ... }
    """
    groups = {}
    cc_name_dict = CCBiz(username).items("ApplicationID", "ApplicationName")
    cc_group_dict = CCBiz(username).items("ApplicationID", "GroupName")
    cc_abbre_dict = CCBiz(username).items("ApplicationID", "Abbreviation")
    for biz_id, biz_group in cc_group_dict.items():
        show_name = cc_name_dict.get(biz_id)
        if cc_abbre_dict.get(biz_id):
            show_name = '%s (%s)' % (show_name, cc_abbre_dict[biz_id])
        groups.setdefault(biz_group, {})[biz_id] = show_name
    return groups


def get_biz_responsible(cc_biz_id, username):
    """获取业务的运维"""
    # 先从用户配置表拿
    try:
        conf = BizConf.objects.get(cc_biz_id=cc_biz_id)
        responsible = conf.responsible
    except BizConf.DoesNotExist:
        responsible = None
    # 如果用户没有配，再从cc拿
    if not responsible:
        responsible = CCBiz(username, cc_biz_id).get("Maintainers")

    return responsible or []


def get_user_biz(username):
    apps = CCBiz(username=username).items("ApplicationID", "ApplicationName")
    bizs = [(app_id, apps.get(app_id, app_id)) for app_id in apps]
    return bizs


@web_cache(60 * 5)
def get_all_ijobs_id(username):
    """
    获取所有ijobs作业id
    note: job 的业务id 和 cc 的业务id 一致，可直接通过 cc 的 get_app_by_user 方法获取
    """
    apps = CCBiz(username=username).items("ApplicationID", "ApplicationName")
    return {app_id: app_id for app_id in apps}


@web_cache(60 * 30)
def _get_all_teams_covered():
    return AlarmInstanceArchive.objects.all().distinct().values_list('biz_team', flat=True)


def list_incident_desc():
    return {inc.id: inc.description for inc in IncidentDef.objects.all()}


def get_module_id_by_name(module_name, cc_biz_id, username):
    """
    根据模块名称获取模块id
    """
    cc_data = _get_app_module_with_cache(cc_biz_id, username)
    for data in cc_data:
        if data.get('ModuleName') == module_name:
            return data.get('ModuleID')
    return ''


def get_set_id_by_name(set_name, cc_biz_id, username):
    """
    根据模块名称获取模块id
    """
    cc_data = _get_app_topo_set_with_cache(cc_biz_id, username)
    for data in cc_data:
        if data.get('SetName') == set_name:
            return data.get('SetID')
    return ''
