# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fta import settings

engine = create_engine(
    'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (
        settings.MYSQL_USER, settings.MYSQL_PASSWORD,
        settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_NAME),
    pool_recycle=30)
Session = sessionmaker(bind=engine)
session = Session(autoflush=True, expire_on_commit=True, autocommit=True)


def type_convert(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def orm_2_dict(orm_obj):
    if hasattr(orm_obj, '__iter__'):
        orm_obj_list = orm_obj
    else:
        orm_obj_list = [orm_obj]
    dict_list_obj = [{
        c.name: type_convert(getattr(obj, c.name)) for c in obj.__table__.columns
    } for obj in orm_obj_list]
    if hasattr(orm_obj, '__iter__'):
        return dict_list_obj
    else:
        return dict_list_obj[0]
