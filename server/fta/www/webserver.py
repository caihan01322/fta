# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import gevent.monkey
from flask import Flask  # noqa
from fta import settings  # noqa
from fta.www.webservice import fta_simple_page  # noqa
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_socket()
gevent.monkey.patch_time()

app = Flask(__name__)
# 对于多数的server框架, debug设置为True可能导致内存泄露
app.debug = False

app.register_blueprint(fta_simple_page, url_prefix="/fta")

try:
    from manager.www.webservice import simple_page as project_simple_page

    app.register_blueprint(project_simple_page)
except Exception as e:
    import traceback

    print u'!!!!! NOT USER WEBSERVER DEFINE !!!!!'
    print traceback.format_exc()

if __name__ == "__main__":
    p = Pool(30)  # at most 30 greenlet
    http = WSGIServer(('0.0.0.0', settings.WEBSERVER_PORT), app, spawn=p)
    http.serve_forever()
