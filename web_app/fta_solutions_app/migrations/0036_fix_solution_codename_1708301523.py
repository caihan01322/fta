# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import unicode_literals

from django.db import migrations, models

from fta_solutions_app.models import Solution


def fix_solution_codename(apps, schema_editor):
    solution = Solution.objects.filter(
        cc_biz_id=0, title__startswith=u"『快捷』发送CPU使用率TOP10的进程",
    ).first()
    if solution and not solution.codename:
        solution.codename = "cpu_proc_top10"
        solution.save()

    solution = Solution.objects.filter(
        cc_biz_id=0, title__startswith=u"『快捷』发送内存使用率TOP10的进程",
    ).first()
    if solution and not solution.codename:
        solution.codename = "mem_proc_top10"
        solution.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0035_auto_20170829_1713'),
    ]

    operations = [
        migrations.RunPython(fix_solution_codename),
    ]
