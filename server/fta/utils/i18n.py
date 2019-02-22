# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging
import os.path

import arrow

import pytz as tz
from babel import support
from fta.utils.lazy import LazyString

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class I18N(object):
    __metaclass__ = Singleton

    def __init__(self):
        # 全局唯一, 修改后可更改语言, 时区
        self.cc_biz_id = None

        from fta import settings
        self.default_locale = settings.DEFAULT_LOCALE
        self.default_timezone = settings.DEFAULT_TIMEZONE

        self.translations = {}
        self.domain = None

    def set_biz(self, cc_biz_id):
        """change biz method
        """
        self.cc_biz_id = cc_biz_id

    @property
    def translation_directories(self):
        """翻译文件夹
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        yield os.path.join(BASE_DIR, 'locale')

    def locale_best_match(self, locale):
        """兼容不同编码
        """
        if locale.lower() in ['zh', 'zh_cn', 'zh-cn']:
            return 'zh_Hans_CN'
        return 'en'

    def get_locale(self):
        """
        根据业务ID获取语言
        """
        if not self.cc_biz_id:
            return self.default_locale

        try:
            from project.utils import query_cc
            locale = query_cc.get_app_by_id(self.cc_biz_id).get('Language')
            if locale:
                return self.locale_best_match(locale)
            else:
                return self.default_locale
        except Exception:
            return self.default_locale

    def get_timezone(self):
        try:
            timezone = self._get_timezone()
        except Exception:
            timezone = tz.timezone(self.default_timezone)
        return timezone

    def _get_timezone(self):
        """
        根据业务ID获取时区
        """
        if not self.cc_biz_id:
            return self.default_timezone

        try:
            from project.utils import query_cc
            timezone = query_cc.get_app_by_id(self.cc_biz_id).get('TimeZone')
            if timezone:
                return timezone
            else:
                return self.default_timezone
        except Exception:
            return self.default_timezone

    def get_translations(self):
        """get translation on the fly
        """
        locale = self.get_locale()
        if locale not in self.translations:
            translations = support.Translations()

            for dirname in self.translation_directories:
                catalog = support.Translations.load(
                    dirname,
                    [locale],
                    self.domain,
                )
                translations.merge(catalog)
                if hasattr(catalog, 'plural'):
                    translations.plural = catalog.plural
            logger.info('load translations, %s=%s', locale, translations)
            self.translations[locale] = translations

        return self.translations[locale]


i18n = I18N()


def gettext(string, **variables):
    """replace stdlib
    """
    t = i18n.get_translations()
    if t is None:
        return string if not variables else string % variables
    s = t.ugettext(string)
    return s if not variables else s % variables


def ngettext(singular, plural, n):
    t = i18n.get_translations()
    if t is None:
        return singular
    s = t.ngettext(singular, plural, n)
    return s


def lazy_gettext(string, **variables):
    """Like :func:`gettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.
    Example::
        hello = lazy_gettext(u'Hello World')
        @app.route('/')
        def index():
            return unicode(hello)
    """
    return LazyString(gettext, string, **variables)


_ = gettext


def arrow_localtime(value, timezone=None):
    """value必须是UTC时间, arrow转换成本地时间
    """
    value = arrow.get(value).replace(tzinfo="utc")
    if not timezone:
        timezone = i18n.get_timezone()
    value = value.to(timezone)
    return value


def localtime(value, timezone=None):
    """value必须是UTC时间, datetime格式
    """
    value = arrow_localtime(value, timezone)
    value = value.datetime
    return value


def arrow_now():
    """当前时区时间, arrow格式
    """
    utcnow = arrow.utcnow()
    timezone = i18n.get_timezone()
    return utcnow.to(timezone)


def now():
    """当前时间, datetime格式
    """
    return arrow_now().datetime


def lazy_join(iterable, word):
    value = ''
    is_first = True
    for i in iterable:
        if is_first:
            value = value + i
            is_first = False
        else:
            value = value + word + i
    return value
