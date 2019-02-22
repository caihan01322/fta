# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""
利用 settings.py 与 settings_env.py 的常量，替代配置模板文件里的变量
python -m script.create_conf 模板文件名 生成的文件名
"""

import re
import sys

IF_BEGIN_NAME_MATCH = re.compile(r'\{\%\s*if\s*([\w\|]+)\s*\%\}')
IF_BEGIN_STR_MATCH = re.compile(r'\{\%\s*if\s*[\w\|]+\s*\%\}')
IF_END_STR_MATCH = re.compile(r'\{\%\s*endif\s*\%\}')
VAR_NAME_MATCH = re.compile(r'\{\{\s*([\w\|]+)\s*\}\}')
VAR_STR_MATCH = re.compile(r'\{\{\s*[\w\|]+\s*\}\}')


def replace_control(line, kwargs):
    if_begin_name_list = IF_BEGIN_NAME_MATCH.findall(line)
    if_begin_str_list = IF_BEGIN_STR_MATCH.findall(line)
    if_end_str_list = IF_END_STR_MATCH.findall(line)
    if not len(if_begin_name_list) == \
            len(if_begin_str_list) == \
            len(if_end_str_list) == 1:
        return line
    var_name = if_begin_name_list[0]
    if_begin_str = if_begin_str_list[0]
    if_end_str = if_end_str_list[0]
    if kwargs.get(var_name):
        line = line.replace(if_begin_str, "")
        line = line.replace(if_end_str, "")
    else:
        idx_begin = line.index(if_begin_str)
        idx_end = line.index(if_end_str) + len(if_end_str)
        line = line[:idx_begin] + line[idx_end:]
    return line


def replace_attr(line, kwargs):
    var_name_list = VAR_NAME_MATCH.findall(line)
    var_str_list = VAR_STR_MATCH.findall(line)
    for var_name, var_str in zip(var_name_list, var_str_list):
        var_value = kwargs.get(var_name, '')
        line = line.replace(var_str, unicode(var_value))
    return line


def create(from_file_path, to_file_path, kwargs):
    with open(from_file_path, 'r') as from_file:
        with open(to_file_path, 'w+') as to_file:
            for line in from_file.readlines():
                line = replace_control(line, kwargs)
                line = replace_attr(line, kwargs)
                to_file.write(line)


if __name__ == '__main__':
    import settings
    import settings_env
    d = settings.__dict__
    d.update(settings_env.__dict__)
    create(sys.argv[1], sys.argv[2], d)
