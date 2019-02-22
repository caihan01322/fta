# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import functools
import json

import requests
from project.blueking.component import conf
from project.blueking.component.client import ComponentClient

from fta import settings
from fta.settings import PAAS_INNER_ADDR
from fta.utils import logging

logger = logging.getLogger("utils")

FAKE_EXCEPTION = [
    # "--ALL--",
]


class ExtendMixin(object):

    def __init__(self):
        self._timeout = 32
        self._error_retries = 1
        self._error_returns = []
        self._dummy_returns = []
        self._assert_returns = []

    def on_timeout(self, timeout):
        self._timeout = timeout
        return self

    def on_error_retries(self, retry_count):
        self._error_retries = retry_count
        return self

    def on_error_returns(self, return_value):
        self._error_returns = [return_value]
        return self

    def on_dummy_returns(self, return_value):
        self._dummy_returns = [return_value]
        return self

    def on_assert_returns(self, return_value):
        self._assert_returns = [return_value]
        return self

    def inherit(self, other_obj):
        other_obj.on_timeout(self._timeout)
        other_obj.on_error_retries(self._error_retries)
        if len(self._error_returns):
            other_obj.on_error_returns(self._error_returns[0])
        if len(self._dummy_returns):
            other_obj.on_dummy_returns(self._dummy_returns[0])
        if len(self._assert_returns):
            other_obj.on_assert_returns(self._assert_returns[0])

    def _extend_conf(self):
        if "info" not in self._conf:
            try:
                self._conf["info"] = requests.get(
                    url="%s/info/get_component/?app_code=%s" % (
                        self._conf["base_url"], self.app_code),
                    timeout=8, verify=False).json()['data']
            except Exception as e:
                self._conf["info"] = []
                logger.warning("get_component error: %s", e)
        return self._conf


class Component(ExtendMixin):

    def __init__(self, app_code, app_secret, conf, module):
        super(Component, self).__init__()
        self.app_code = app_code
        self.app_secret = app_secret
        self._conf = conf
        self._prefix = "compapi"
        self._module = module

    def _getAttributeNames(self):
        return [
            component['name'] for component in self._extend_conf()['info']
            if component['component_system__name'].lower() == self._module]

    def _insert_doc(self, func):
        try:
            for comp_info in self._conf.get('info', []):
                if comp_info['name'] == self._attr:
                    func.__doc__ = comp_info['label']
        except Exception as e:
            logger.warning(e)

    def __check_fake_exception(self, attr):
        if "--ALL--" in FAKE_EXCEPTION or attr in FAKE_EXCEPTION:
            if len(self._error_returns):
                return self._error_returns[0]
            raise Exception("Fake Exception")

    def __dummy(self):
        self._default_data["dummy"] = True
        self._func = FuncBox.execute

    def __query(self):
        self._func = FuncBox.query

    def __execute(self):
        self._func = FuncBox.execute

    def __test(self):
        self._prefix = "comptest"

    def __api(self):
        self._prefix = "compapi"

    def __getattr__(self, attr):

        if attr.startswith('_') or attr == "trait_names":
            return

        self._default_data = {"app_code": self.app_code}
        self._attr = attr.split("__")[0]
        self._func = self._conf["func"]

        if len(attr.split("__")) == 2:
            getattr(self, "_Component__%s" % attr.split("__")[1])()

        self.__check_fake_exception(self._module)
        # 数据平台拉取告警api特殊处理
        if self._module == 'data' and self._attr == 'get_alarms':
            self._attr = 'monitor/alarm/alarms'
        self._url = "%s/%s/%s/%s/" % (self._conf['base_url'], self._prefix, self._module, self._attr)

        func = functools.partial(self._func, self)
        self._insert_doc(func)
        return func


class BKComponent(ExtendMixin):

    def __init__(self, ENVI, app_code, app_secret="", envi="product"):
        super(BKComponent, self).__init__()
        self.ENVI = ENVI
        self.app_code = app_code
        self.app_secret = app_secret
        self.use(envi)

    def _getAttributeNames(self):
        return list(set([component['component_system__name'].lower() for component in self._extend_conf()['info']]))

    def use(self, envi):
        self._conf = self.ENVI[envi]

    def using(self, envi):
        return BKComponent(
            self.ENVI, self.app_code, self.app_secret, envi=envi)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return

        comp = Component(self.app_code, self.app_secret, self._conf, attr)
        self.inherit(comp)
        return comp


def boxmethod(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):

        # get component
        component = kwargs.pop("component", None) or [arg for arg in args if isinstance(arg, Component)][0]

        # dummy
        if len(component._dummy_returns):
            return component._dummy_returns[0]

        logger.info("call_bk: %s", component._url)
        error_message = ""

        # error_retries
        while component._error_retries >= 1:
            try:
                return_value = func(*args, **kwargs)
                if len(component._assert_returns):
                    assert isinstance(return_value, type(component._assert_returns[0]))  # noqa
                logger.info("call_bk return_value:%s" % return_value)
                logger.info("call_bk: END")
                return return_value
            except Exception as e:
                error_message = u"%s" % e
                logger.warning("COMPONENT ERROR %s: %s %s", component._url, e, json.dumps(kwargs), )
                component._error_retries -= 1

        # error_returns
        if len(component._error_returns):
            return component._error_returns[0]

        raise Exception(error_message)

    return _wrapper


class FuncBox(object):

    @staticmethod
    def _post(component, body, **kwargs):
        try:
            r = requests.post(component._url, data=body, timeout=component._timeout, verify=False, **kwargs)
            r.raise_for_status()
        except Exception as e:
            raise Exception('REQUEST %s' % e)
        else:
            if not r.json()['result']:
                logger.warning("COMPONENT FULL ERROR: %s", r.text)
                raise Exception(r.json()['message'])
        return r.json()['data']

    @staticmethod
    @boxmethod
    def query(component, **data):
        data.update(component._default_data)
        body = json.dumps(data)
        return FuncBox._post(component, body)

    @staticmethod
    @boxmethod
    def execute(component, **data):
        from fta.utils.component_callback import CallbackManager
        callback_manager = CallbackManager(component)
        data.update(callback_manager.default_data)
        req_data = {}
        req_data['params'] = data
        req_data['request_type'] = 'xinyun'
        req_data['callback_url'] = callback_manager.callback_url
        req_data['process_uniqid'] = callback_manager.process_id
        req_data['instance_uniqid'] = callback_manager.instance_uniqid
        req_data['task_id'] = callback_manager.instance_id
        body = json.dumps(req_data)
        headers = {
            'Content-Length': len(body),
            'Content-Type': 'application/json',
        }
        FuncBox._post(component, body, headers=headers)
        logger.info("$%s exec_bk %s %s", callback_manager.instance_id, component._url, body)
        return callback_manager.instance_uniqid


class FuncBoxClient(object):

    @classmethod
    def _get_auth_token_by_skey(cls, component, uin, skey):
        client = ComponentClient(
            component.app_code,
            component.app_secret,
            common_args={"uin": uin, "skey": skey})
        url = "%s%s" % (conf.COMPONENT_SYSTEM_HOST, "/compapi/auth/get_auth_token_by_uin/")
        r = client.request("GET", url, params={"target_uin": uin, "target_skey": skey})
        r.raise_for_status()
        if not r.json()['result']:
            raise Exception(r.json()['message'])
        return r.json()["data"]["auth_token"]

    @classmethod
    def get_auth_token_by_uin(cls, component, uin=None):
        # 从 APP 的 DB 中获取
        return ""

    @classmethod
    def _get_auth_token(cls, component, data):
        if "auth_token" in data:
            return data.pop("auth_token")
        elif "_skey" in data:
            return cls._get_auth_token_by_skey(component, data.pop("_uin"), data.pop("_skey"))
        elif "_uin" in data:
            return cls.get_auth_token_by_uin(component, data.pop("_uin"))
        return cls.get_auth_token_by_uin(component)

    @classmethod
    @boxmethod
    def sdk(cls, component, **data):
        for k, v in component._conf.get("func_kwargs", {}).items():
            setattr(conf, k, v)

        if '__uin__' in data:
            client = ComponentClient(
                component.app_code,
                component.app_secret,
                common_args={"username": data['__uin__']})
            del data['__uin__']
        else:
            client = ComponentClient(
                component.app_code,
                component.app_secret,
                common_args={"username": '100'})
        method = data.pop("_method", "POST")
        if method == "POST":
            r = client.request("POST", component._url, data=data)
        else:
            r = client.request("GET", component._url, params=data)
        logger.info("call_bk(%s): %s %s ", method, component._url, data)
        r.raise_for_status()
        if not r.json()['result']:
            logger.warning("call_bk error: %s", r.text)
            raise Exception(r.json()['message'])
        return r.json()['data']


class FuncBoxQcloud(FuncBoxClient):

    @classmethod
    def get_auth_token_by_uin(cls, component, uin):
        # 从 APP 的 DB 中获取
        return ""


COMP_INFO = [{
    "component_system__name": "cmsi",
    "label": "send_sms",
    "name": "send_sms",
}, {
    "component_system__name": "cc",
    "label": "clone_host_property",
    "name": "clone_host_property",
}, {
    "component_system__name": "cc",
    "label": "update_host_module",
    "name": "update_host_module",
}]

base_url = "%s/api/c" % PAAS_INNER_ADDR
ENVI = {
    "product": {
        "base_url": base_url,
        "func": FuncBoxQcloud.sdk,
        "func_kwargs": {"RUN_MODE": "PRODUCT", },
        "version": "open",
        "info": COMP_INFO,
    },
    "test": {
        "base_url": base_url,
        "func": FuncBoxQcloud.sdk,
        "func_kwargs": {"RUN_MODE": "TEST", },
        "version": "open",
        "info": COMP_INFO,
    },
    "dev": {
        "base_url": base_url,
        "func": FuncBoxQcloud.sdk,
        "func_kwargs": {"RUN_MODE": "TEST", },
        "version": "open",
        "info": COMP_INFO,
    },
}

bk = BKComponent(ENVI, settings.APP_CODE, settings.APP_SECRET_KEY)
