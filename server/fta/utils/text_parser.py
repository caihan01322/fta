# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
#!/usr/bin/env python
# encoding: utf-8

import re
from collections import OrderedDict, deque
from contextlib import contextmanager

import six

undefined = object()


class ParseError(Exception):
    def __init__(self, context, *args, **kwargs):
        super(ParseError, self).__init__(*args, **kwargs)
        self.context = context


class CircularRefParseError(ParseError):
    pass


class ReferenceParseError(ParseError):
    pass


class ParseValueError(ParseError):
    pass


def force_text(obj, encoding="utf-8", errors="strict"):
    if isinstance(obj, six.text_type):
        return obj
    if not isinstance(obj, six.binary_type):
        obj = str(obj)
    return obj.decode(encoding, errors)


class RegisterDict(dict):
    def register(self, key, force=False):
        key = str(key)
        if not force and key in self:
            raise KeyError("%s was existed" % key)

        def update(obj):
            self[key] = obj
            return obj

        return update


class Context(object):

    def __init__(
        self, input=None, items=None, values=None, parser=None,
        debug=False,
    ):
        self.input = input
        self.values = values or {}
        self.comments = OrderedDict()
        self.parser = parser
        self.debug = debug
        self.set_items(items)

    def set_items(self, items):
        self.items = OrderedDict(items or {})

    def add_comment(self, name, comment):
        comments = self.comments.get(name)
        if comments is None:
            comments = self.comments.setdefault(name, [])
        comments.append(comment)

    @classmethod
    def from_item_list(cls, items, **kwargs):
        return cls(items=[
            (i.name, i) for i in items
        ], **kwargs)


class Item(object):
    TYPE = ""
    DEFAULT_ATTRS = (
        ("default", undefined),
        ("type", TYPE),
    )

    def __init__(
        self, value, dependencies=None, name=None, input=None,
        **kwargs
    ):
        self.name = name or force_text(id(self))
        self.value = value
        self.input = input
        self.dependencies = None

        self.set_dependencies(dependencies)

        params = dict(self.DEFAULT_ATTRS)
        params.update(kwargs)

        for attr, val in params.items():
            setattr(self, attr, val)

        self.init()

    def add_comment(self, context, comment):
        context.add_comment(self.name, comment)

    def set_dependencies(self, dependencies):
        dependencies = list(dependencies or [])
        if self.input:
            dependencies.append(self.input)
        self.dependencies = dependencies

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Item[{self.name}]: type={self.type}>".format(self=self)

    def init(self):
        pass

    def can_evaluate(self, context):
        context_values = context.values
        for i in self.dependencies:
            if i not in context_values:
                return False
        return True

    def get_value(self, context):
        return self.default

    def evaluate(self, context):
        value = self.get_value(context)
        if value is undefined:
            raise ParseValueError(context, self.name)
        return value

    def evaluate_string(self, context):
        return force_text(self.evaluate(context))


class ContantItem(Item):
    TYPE = "contant"
    DEFAULT_ATTRS = Item.DEFAULT_ATTRS + (
        ("type", TYPE),
    )

    def get_value(self, context):
        return self.value


class TemplateItem(Item):
    TYPE = "template"
    DEFAULT_ATTRS = Item.DEFAULT_ATTRS + (
        ("type", TYPE),
        ("default", u""),
    )
    VAR_REGEX = re.compile(r"\${\s*(?P<key>\w+)\s*}")

    def init(self):
        self.template = self.VAR_REGEX.split(self.value)
        self.dependencies.extend(
            var for is_var, var in self.iter_value()
            if is_var
        )

    def iter_value(self):
        is_var = False
        for part in self.template:
            yield is_var, part
            is_var = not is_var

    def get_value(self, context):
        parts = []
        values = context.values
        for is_var, part in self.iter_value():
            if is_var:
                part = values.get(part)
            parts.append(force_text(part))
        return "".join(parts)


class ExprItem(Item):
    DEFAULT_ATTRS = Item.DEFAULT_ATTRS + (
        ("pattern", None),
    )

    def get_input(self, context):
        input_ = self.input
        if not input_:
            return context.input
        return context.values.get(input_, u"")


class RegexExprItem(ExprItem):
    TYPE = "regex"
    DEFAULT_ATTRS = ExprItem.DEFAULT_ATTRS + (
        ("type", TYPE),
        ("flag", "SIM"),
    )
    REGEX_FLAGS = {
        "S": re.S,
        "I": re.I,
        "M": re.M,
        "U": re.U,
    }

    def init(self):
        flag = 0
        for f in self.flag:
            v = self.REGEX_FLAGS.get(f.upper())
            if not v:
                continue
            flag |= v
        self.pattern = re.compile(self.value, flag)

    def get_value(self, context):
        input_ = self.get_input(context)
        match = self.pattern.search(input_)
        if not match:
            self.add_comment(context, "pattern not found")
            return self.default
        groups = match.groups()
        return groups[0] if groups else match.group()


class CSSSelectorExprItem(ExprItem):
    TYPE = "css-selector"
    DEFAULT_ATTRS = ExprItem.DEFAULT_ATTRS + (
        ("type", TYPE),
    )

    def get_value(self, context):
        from pyquery import PyQuery

        input_ = self.get_input(context)
        pyquery = PyQuery(input_)
        return pyquery(self.value).text().strip()


class HTMLXPathExprItem(ExprItem):
    TYPE = "xpath"
    DEFAULT_ATTRS = ExprItem.DEFAULT_ATTRS + (
        ("type", TYPE),
    )

    def get_value(self, context):
        from lxml import etree

        input_ = self.get_input(context)
        root = etree.HTML(force_text(input_))
        result = root.xpath(self.value)
        if not result:
            self.add_comment(context, "pattern not found")
            return self.default
        if isinstance(result, six.string_types):
            return force_text(result).strip()
        result = result[0]
        if isinstance(result, etree._Element):
            return etree.tostring(result).strip()
        return result.strip()


class ItemFactory(object):
    ITEM_TYPE_MAPPINGS = {
        Item.TYPE: Item,
        ContantItem.TYPE: ContantItem,
        TemplateItem.TYPE: TemplateItem,
        RegexExprItem.TYPE: RegexExprItem,
        CSSSelectorExprItem.TYPE: CSSSelectorExprItem,
        HTMLXPathExprItem.TYPE: HTMLXPathExprItem,
    }

    @classmethod
    def get_item(cls, type, **kwargs):
        type_class = cls.ITEM_TYPE_MAPPINGS.get(type)
        if not type_class:
            raise TypeError(type)
        return type_class(type=type, **kwargs)


class ParseOrdering(object):

    def __init__(self, context):
        self.solved_items = OrderedDict()
        self.context = context
        self.dependencies = {}

        for name, item in context.items.items():
            if not item.dependencies:
                self.solved_items[name] = item
            else:
                self.dependencies[name] = deque(item.dependencies)

    def solve_dependencies(self, dependencies):
        old_dependencies = tuple(dependencies)
        solved_once = False
        dependencies.clear()
        for i in old_dependencies:
            if i in self.solved_items:
                solved_once = True
                continue
            if i not in self.dependencies:
                raise ReferenceParseError(self.context, i)
            dependencies.append(i)
        return solved_once

    def check_dependencies(self):
        context = self.context
        solved_once = False
        for name, dependencies in tuple(self.dependencies.items()):
            if not dependencies:
                solved_once = True
                self.solved_items[name] = context.items[name]
                self.dependencies.pop(name)
            else:
                if self.solve_dependencies(dependencies):
                    solved_once = True
        return solved_once

    def check(self):
        while self.dependencies:
            if not self.check_dependencies():
                raise CircularRefParseError(self.context)

    def __iter__(self):
        if self.dependencies:
            self.check()
        return iter(self.solved_items.values())


class BaseParser(object):

    def __init__(self, items=None, context=None):
        self.items = items or []
        self.context = context
        if context:
            context.items = {
                i.name: i
                for i in items
            }
            context.input = None
            context.parser = self

    @property
    def name(self):
        return "$%s-%s" % (self.__class__, id(self))

    @contextmanager
    def parse_context(self, context):
        old_context = self.context
        self.context = context
        try:
            yield
        finally:
            self.context = old_context

    def add_comment(self, context, comment):
        context.add_comment(self.name, comment)

    def try_evaluate(self, context, item):
        if item.can_evaluate(context):
            result = item.evaluate_string(context)
            context.values[item.name] = result
            if context.debug:
                self.add_comment(context, "!!result: %s" % result)
            return True
        elif context.debug:
            self.add_comment(context, "!!skiped: %s" % item.name)
        return False

    def get_context(self, content):
        if self.context:
            self.context.input = content
            return self.context
        return Context.from_item_list(
            input=content, items=self.items, parser=self,
        )

    def parse(self, content):
        raise NotImplementedError()

    def isplit_and_parse(self, content, regex):
        if isinstance(regex, six.string_types):
            regex = re.compile(regex)

        for part in regex.split(content):
            error = None
            try:
                context = self.parse(part)
            except Exception as error:
                pass
            yield error, context

    @classmethod
    def from_config(cls, config, *args, **kwargs):
        items = [
            ItemFactory.get_item(**i)
            for i in config
        ]
        return cls(items=items, *args, **kwargs)

    @classmethod
    def from_yaml(cls, yaml_content, *args, **kwargs):
        import yaml
        config = yaml.load(yaml_content)
        return cls.from_config(config["items"])


class ContextOptimizeMixin(object):

    def optimize_context(self, context):
        ordering_items = [
            (i.name, i)
            for i in ParseOrdering(context)
        ]
        context.set_items(ordering_items)
        return context

    def get_context(self, content):
        context = super(ContextOptimizeMixin, self).get_context(content)
        return self.optimize_context(context)


class LoopParseMixin(object):

    def parse(self, content):
        context = self.get_context(content)
        items = deque(context.items.values())
        if not items:
            return

        sentry = None
        while items:
            item = items.popleft()
            if self.try_evaluate(context, item):
                if item is sentry:
                    sentry = None
            else:
                if item is sentry:
                    raise ParseValueError(context, item.name)
                elif not sentry:
                    sentry = item
                items.appendleft(item)

        return context


class SimpleParseMixin(object):

    def parse(self, content):
        context = self.get_context(content)
        for name, item in context.items.items():
            if not self.try_evaluate(context, item):
                raise ParseValueError(context, name)
        return context


class ContextOptimizeBaseParser(ContextOptimizeMixin, BaseParser):
    pass


class SimpleParser(SimpleParseMixin, BaseParser):
    pass


class FastParser(SimpleParseMixin, ContextOptimizeBaseParser):
    pass


class SimpleLoopParser(LoopParseMixin, BaseParser):
    pass


class LoopParser(LoopParseMixin, ContextOptimizeBaseParser):
    pass
