# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json

from project.utils.component import bk

try:
    from fta.utils import logging
except BaseException:
    import logging

logger = logging.getLogger('utils')


class CC(object):
    """
    使用方法：
    >>> CC(["127.0.0.1", "127.0.0.2"]).get("SetName|set")

    >>> CC("127.0.0.1").get("HostName")
    """

    # 批量拉取时切片的大小
    BUCKET = 200

    def __init__(self, ip=[], set_id=[], include_outer_ip=False, default_kwargs={}):
        if not isinstance(ip, list) and ip:
            self.ip_list = [ip]
        else:
            self.ip_list = [i for i in ip]
        if not isinstance(set_id, list) and set_id:
            self.set_id_list = [set_id]
        else:
            self.set_id_list = [i for i in set_id]
        self.include_outer_ip = include_outer_ip
        self.default_kwargs = default_kwargs
        self.attrs = []

    def get(self, var):
        """
        获取单个属性的方法
        :param var: 属性名
                    属性名可以加参数
                    比如 set 属性: SetName|set
        :return unicode: 属性值

        支持参数: all、set、custom、tcm

        all: 当有多个参数的时候
             将返回通过逗号间隔的字符串

             如有多个主机名称的时候
             "HostName|all"
             返回 "hostname1,hostname2,hostnameN"
             不添加默认返回第一个

        set: 查询 Set 属性
             如查询 Set 名称
             "SetName|set"

        custom: 查询自定义属性
                如查询一个名为 IDC 的 Set 属性
                "IDC|set|custom"

        tcm: 查询的结果如果是多个，则返回列表格式，否则返回单个
             查询结果只有一个时得到: "返回的结果1"
             查询结果有多个时得到: "[返回的结果1,返回的结果2,返回的结果三]"

        参数能任意组合，如以下两个写法是等价的：

        ${IDC|set|custom|all}
        ${IDC|all|set|custom}
        """

        # 获取属性的值
        query_attr_name = CC._clean_attr_show(var)
        attr_name = CC._clean_attr_type(query_attr_name)
        result_values = self.values(query_attr_name).values()
        result = result_values[0][attr_name] if result_values else ""

        argvs = var.split('|')[1:]

        # 处理 all 参数
        is_all = 'all' in argvs
        if is_all and len(result) > 1:
            result_str = u','.join(result)
        elif len(result) > 0:
            result_str = result[0]
        else:
            result_str = ""

        # 处理 tcm 参数
        is_tcm = 'tcm' in argvs
        if is_tcm:
            result_str = u'[%s]' % result_str

        logger.info("cc query ip:%s set:%s %s = %s", self.ip_list, self.set_id_list, var, result_str)

        return result_str

    @staticmethod
    def _clean_attr_show(attr):
        if attr.startswith('cc|'):
            attr = attr.replace('cc|', '')
        return attr.replace('|all', '').replace('|tcm', '')

    @staticmethod
    def _clean_attr_type(attr):
        if attr.startswith('cc|'):
            attr = attr.replace('cc|', '')
        return attr.replace('|set', '').replace('|custom', '')

    @staticmethod
    def _clean_attr(attr):
        """得到不含参数的属性名"""
        return CC._clean_attr_type(CC._clean_attr_show(attr))

    @staticmethod
    def _is_set_attr(attr):
        """判断是否是 SET 属性"""
        return '|set' in attr

    @staticmethod
    def _is_custom_attr(attr):
        """判断是否是 自定义 属性"""
        return '|custom' in attr

    @property
    def host_std_attr(self):
        """筛选主机标准属性"""
        return [CC._clean_attr(attr) for attr in self.attrs if
                not CC._is_set_attr(attr) and not CC._is_custom_attr(attr)]

    @property
    def host_cst_attr(self):
        """筛选主机自定义属性"""
        return [CC._clean_attr(attr) for attr in self.attrs if not CC._is_set_attr(attr) and CC._is_custom_attr(attr)]

    @property
    def set_std_attr(self):
        """筛选SET标准属性"""
        return [CC._clean_attr(attr) for attr in self.attrs if CC._is_set_attr(attr) and not CC._is_custom_attr(attr)]

    @property
    def set_cst_attr(self):
        """筛选SET自定义属性"""
        return [CC._clean_attr(attr) for attr in self.attrs if CC._is_set_attr(attr) and CC._is_custom_attr(attr)]

    @property
    def all_attr(self):
        """所有的属性"""
        return list(set(self.host_std_attr + self.host_cst_attr + self.set_std_attr + self.set_cst_attr))

    def _get_cc_hosts(self):
        """获取所有相关主机的 CC 主机信息"""
        host_std_attr = list(set(self.host_std_attr + ['InnerIP', 'OuterIP', 'TopoSetID', 'DisplayName']))
        self.cc_hosts = []

        # 将所有 IP 当做内网 IP 查询一次
        seek = 0
        while seek < len(self.ip_list):
            query_ip = ','.join(self.ip_list[seek: seek + self.BUCKET])
            cc_hosts = bk.cc.on_error_retries(2).get_query_info(
                host_std_req_column=host_std_attr,
                host_cst_req_column=self.host_cst_attr,
                host_std_key_values={'InnerIP': query_ip}) or []
            self.cc_hosts.extend(cc_hosts)
            seek += self.BUCKET

        # 如果查询 IP 不包含外网 IP，可以返回了
        if self.include_outer_ip is not True:
            return self.cc_hosts

        # 将所有 IP 当做外网 IP 查询一次
        seek = 0
        while seek < len(self.ip_list):
            query_ip = ','.join(self.ip_list[seek: seek + self.BUCKET])
            outer_cc_hosts = bk.cc.on_error_retries(2).get_query_info(
                host_std_req_column=host_std_attr,
                host_cst_req_column=self.host_cst_attr,
                host_std_key_values={'OuterIP': query_ip}) or []
            self.cc_hosts.extend(outer_cc_hosts)
            seek += self.BUCKET

        # logger.debug("cc_hosts %s %s", self.ip_list, self.cc_hosts)
        return self.cc_hosts

    def _get_cc_sets(self):
        """获取所有相关主机的 CC SET 信息"""

        # 无查询 CC 属性，无需查询
        if not filter(CC._is_set_attr, self.attrs):
            return []

        set_ids = self.set_id_list + list(set([cc_host["TopoSetID"] for cc_host in self.cc_hosts]))

        # 如果查询 set 自定义属性，必须为同业务
        if any([self._is_custom_attr(attr) and self._is_set_attr(attr) for attr in self.attrs]):
            biz_name_2_id = CCBiz.items("DisplayName", "ApplicationID")
            set_bizs = {cc_host["TopoSetID"]: biz_name_2_id[cc_host["DisplayName"]] for cc_host in self.cc_hosts}
            app_id = set_bizs[set_ids[0]]
            for set_id in set_ids:
                assert app_id == set_bizs[set_id]
        else:
            app_id = ""

        seek = 0
        self.cc_sets = []
        while seek < len(set_ids):
            query_set = ','.join(set_ids[seek: seek + self.BUCKET])
            kwargs = dict(
                method="getTopoSetList",
                app_id=app_id,
                set_std_req_column=self.set_std_attr + ["SetID"],
                set_cst_req_column=self.set_cst_attr,
                set_std_key_values={"SetID": query_set})
            kwargs.update(self.default_kwargs)
            # logger.debug("query_set: %s", kwargs)
            cc_sets = bk.cc.on_error_retries(2).get_query_info(**kwargs) or []
            if isinstance(cc_sets, dict):
                cc_sets = cc_sets.values()
            self.cc_sets.extend(cc_sets)
            seek += self.BUCKET

        # logger.debug("cc_sets %s %s", self.ip_list, cc_sets)
        return self.cc_sets

    def _init_result(self, result):
        """初始化结果字典"""
        for attr in self.attrs:
            for ip in self.ip_list:
                result.setdefault(ip, {})[CC._clean_attr(attr)] = []
            for set_id in self.set_id_list:
                result.setdefault(set_id, {})[CC._clean_attr(attr)] = []
        return result

    def _fill_ip_result(self, result, cc_hosts, cc_sets):
        """填充 IP 属性到 result 字典中"""
        for ip in self.ip_list:
            cc_host = [
                info for info in cc_hosts if ip in info['InnerIP'].split(',') or ip in info['OuterIP'].split(',')
            ]
            if not cc_host:
                logger.warning("ip %s not host info", ip)
                continue
            set_id = cc_host[0]["TopoSetID"]
            # logger.debug("CCSets %s", cc_sets)
            cc_set = [info for info in cc_sets if info['SetID'] == set_id]
            for attr in self.all_attr:
                value = [
                    info[attr] for info in cc_host if info.get(attr)
                ] or [
                    info[attr] for info in cc_set if info.get(attr)
                ]
                result[ip][attr] = list(set(value))

    def _fill_set_result(self, result, cc_sets):
        """填充 set 属性到 result 字典中"""
        for set_id in self.set_id_list:
            cc_set = [info for info in cc_sets if info['SetID'] == set_id]
            for attr in self.all_attr:
                value = [info[attr] for info in cc_set if info.get(attr)]
                result[set_id][attr] = list(set(value))

    def values(self, *attrs):
        """
        批量查询属性的方法
        :param *attrs: 查询的属性名
        :return dict: {
                "ip1": {
                    "attr1": ["value1", "value2"]
                }
            }
        """

        self.attrs = attrs

        # 没有查询数据直接返回
        if not self.ip_list and not self.set_id_list:
            return {}

        logger.info("cc batch query ip:%s set:%s %s", self.ip_list, self.set_id_list, attrs)

        # 初始化结果字典
        result = self._init_result({})

        # 获取所有 ip 的主机属性
        cc_hosts = self._get_cc_hosts()
        if not cc_hosts and not self.set_id_list:
            logger.warning("cc info None: %s", self.ip_list)
            return result

        # 获取所有 set 的 set 属性
        cc_sets = self._get_cc_sets()

        # 填充 ip 属性到 result 字典中
        self._fill_ip_result(result, cc_hosts, cc_sets)

        # 填充 set 属性到 result 字典中
        self._fill_set_result(result, cc_sets)

        # logger.debug("result %s %s", self.ip_list, result)
        return result

    def values_with_cache(self, timeout, *attrs):
        """
        values 方法的缓存版本
        :param timeout: 缓存失效时间
        其他同 values 方法
        """
        from fta.storage.cache import Cache
        cache = Cache('redis')
        cache_key = "CC_%s" % json.dumps([self.ip_list, self.set_id_list, attrs])
        result = json.loads(cache.get(cache_key) or "{}")
        if not result:
            result = self.values(*attrs)
            cache.set(cache_key, json.dumps(result), timeout)
        return result


class CCBiz(object):
    """
    使用方法：
    >>> CCBiz(cc_biz_id=120).get("GroupName")

    >>> CCBiz.items(key="ApplicationID", value="DisplayName")
    """

    def __init__(self, cc_biz_id=None, cc_biz_name=None):
        """
        :param cc_biz_id: CC 业务 ID
        :param cc_biz_name: CC 业务名
        cc_biz_id 和 cc_biz_name 至少一项必填
        """
        assert cc_biz_id or cc_biz_name
        if cc_biz_id:
            self.key = "ApplicationID"
            self.key_value = unicode(cc_biz_id)
        elif cc_biz_name:
            self.key = "DisplayName"
            self.key_value = unicode(cc_biz_name)

    def get(self, attr_name, default=None):
        """
        获取属性值
        :param attr_name: 属性名
        :param default: 查询不到时的默认值，默认为 None
        :return unicode: 属性值，查询不到返回 param default
        """
        return self.items(self.key, attr_name).get(self.key_value, default)

    from fta.utils.decorator import func_cache

    @staticmethod
    @func_cache(60 * 60)
    def items(key, value):
        """
        指定业务属性的两个属性名，返回其对应的字典
        :param key: 作为字典 KEY 的属性名
        :param value: 作为字典 VALUE 的属性名
        :return dict: {"key_attr_value": "value_attr_value"}
        """
        data = {'method': 'getAppList', 'app_std_req_column': [key, value]}
        cc_result = bk.cc.on_error_retries(2).get_query_info(**data)
        return {unicode(biz[key]): unicode(biz[value]) for biz in cc_result}
