# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import os.path

import jinja2
from fta.utils import hooks, i18n, logging

logger = logging.getLogger('utils')


def render_mail(kwargs, template_dir):
    file_path, file_name = os.path.split(template_dir)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([file_path]),
        extensions=['jinja2.ext.i18n'])

    env.install_gettext_translations(i18n)
    template = env.get_template(file_name)
    content = template.render(**kwargs)
    return content


def default_func(verifier, message, *args, **kwargs):
    print "!!! Don't have send method !!!"
    logger.error("Don't have send mthod")


hook = hooks.HookManager("send")
wechat = hook.get("wechat", default_func)
sms = hook.get("sms", default_func)
im = hook.get("im", default_func)
mail = hook.get("mail", default_func)
phone = hook.get("phone", default_func)
mail_app_user = hook.get("mail_app_user", default_func)
