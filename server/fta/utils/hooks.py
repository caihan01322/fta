# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

# Get overloaded module in project.hooks or not
# It is controlled by sys.argv
# If "overload" is in sys.argv then overload it, else not

import fnmatch
import importlib
import inspect
import re
import sys

from fta.utils import logging

logger = logging.getLogger("utils")


class HookWrapper(object):

    def __init__(self, wrapped, module_name):
        self.wrapped = wrapped
        self.hooks = HookManager(module_name)

    def __getattr__(self, name):
        method = self.hooks.get(name, True)
        return method if method is not True else getattr(self.wrapped, name)


class HookManager(object):

    def __init__(self, module_name):
        try:
            self.module = importlib.import_module(
                "project.hooks.%s" % module_name)
        except ImportError:
            pass
        except Exception as e:
            logger.warning(u"hooks import error: %s", e)
            self.module = None

    def get(self, attr_name, default_obj=None):
        try:
            return getattr(self.module, attr_name)
        except BaseException:
            if not default_obj:
                raise
            return default_obj

    def get_by_argv(self, attr_name, default_obj=None):
        if "overload" in sys.argv:
            return self.get(attr_name)
        else:
            return default_obj

    def __getattr__(self, attr_name):
        return self.get(attr_name, lambda *args, **kwargs: None)

    def patch(self, attr_name):
        def wrapper(default_obj):
            return self.get(attr_name, default_obj)

        return wrapper


class HookImport(object):
    MATCH_FUNC_KEY = 'match_'

    def __init__(self, module_name, fail_silently=True):
        self.module_name = module_name
        self.fail_silently = fail_silently

        try:
            self.module = importlib.import_module(module_name)
        except ImportError:
            if fail_silently:
                self.module = None
            else:
                raise
        self.re_patterns = {}

    def get_match_func(self, match_mode):
        """获取匹配函数
        """
        all_match_func = filter(lambda x: x[0].startswith(self.MATCH_FUNC_KEY), inspect.getmembers(self))
        func_name = '%s%s' % (self.MATCH_FUNC_KEY, match_mode)
        match_func = filter(lambda x: x[0] == func_name, all_match_func)
        if not match_func:
            support_match = [i[0][len(self.MATCH_FUNC_KEY):] for i in all_match_func]
            raise NotImplementedError('import_all only support [%s] match mode' % ('|'.join(support_match)))
        return match_func[0][1]

    def match_prefix(self, name, pattern):
        """前缀匹配
        """
        return name.startswith(pattern)

    def match_wildcard(self, name, pattern):
        """通配符匹配
        """
        return fnmatch.fnmatch(name, pattern)

    def match_regex(self, name, pattern):
        """正则表达式匹配
        """
        # cache re compile
        re_pattern = self.re_patterns.get(pattern)
        if not re_pattern:
            re_pattern = re.compile(pattern)
            self.re_patterns[pattern] = re_pattern
        return bool(re_pattern.match(name))

    def import_all(self, pattern, match_mode='prefix', env={}):
        match_func = self.get_match_func(match_mode)
        matched = dict(filter(lambda x: match_func(x[0], pattern), inspect.getmembers(self.module)))

        if env and matched:
            env.update(matched)
            name = env.get('__name__', '')
            logger.info("'%s' has import %s from '%s'" % (name, matched.keys(), self.module_name))
        return matched

    def __import__(self, name, default_obj=AttributeError):
        """单个引用
        """
        obj = getattr(self.module, name, default_obj)
        if obj == AttributeError:
            module_name = "<'%s'>" % self.module_name
            raise AttributeError("%s has no attribute '%s'" % (self.module or module_name, name))
        return obj


def hook_import(name, modules, default=None, catch=False):
    for m in modules:
        try:
            return importlib.import_module("%s.%s" % (m.rstrip("."), name))
        except BaseException:
            if not catch:
                raise
    return default
