# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import importlib
import os
import traceback

from django.db.transaction import atomic


def default_runner(apps, schema_editor, module, silent):
    if not hasattr(module, "MODEL"):
        if silent:
            return
        raise AttributeError("MODEL not in %s" % module.__name__)

    if not hasattr(module, "DATA"):
        if silent:
            return
        raise AttributeError("DATA not in %s" % module.__name__)

    checker = getattr(module, "CHECKER", lambda apps: (
        not module.MODEL.objects.all().exists()
    ))
    item_checker = getattr(
        module, "ITEM_CHECKER", lambda apps, item: True
    )

    pk = module.MODEL._meta.pk.attname

    if checker(apps):
        for item in module.DATA:
            if not item_checker(apps, item):
                continue
            if pk in item and module.MODEL.objects.filter(pk=item[pk]).exists():
                continue
            try:
                module.MODEL.objects.create(**item)
            except Exception:
                if not silent:
                    raise
                print(traceback.format_exc())


def init_fixture(name_list, silent=None):
    if isinstance(name_list, basestring):
        name_list = [name_list]

    silent = (
        os.environ.get("MIGRATE_SILENT") == "1"
        if silent is None else silent
    )

    def wrapper(apps, schema_editor):
        with atomic():
            for name in name_list:
                module_name = "project.fixture.%s" % name
                try:
                    module = importlib.import_module(module_name)
                except Exception:
                    if not silent:
                        raise
                    print(traceback.format_exc())
                    return

                runner = getattr(module, "RUNNER", default_runner)
                try:
                    runner(apps, schema_editor, module, silent)
                except Exception:
                    if not silent:
                        raise
                    print(traceback.format_exc())
                    return

    return wrapper
