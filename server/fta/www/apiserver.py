# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from flask import Flask
from fta import settings
from fta.www.apiservice import fta_api_page
from fta.www.apiservice.health import app as fta_admin_app
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
# 对于多数的server框架, debug设置为True可能导致内存泄露
app.debug = False

app.register_blueprint(fta_api_page, url_prefix="/fta")
app.register_blueprint(fta_admin_app)

try:
    from project.www.apiservice import api_page as project_api_page
    app.register_blueprint(project_api_page)
except Exception as e:
    pass

try:
    from manager.www.apiservice import api_page as manager_api_page
    app.register_blueprint(manager_api_page)
except Exception as e:
    pass

if __name__ == "__main__":
    p = Pool(30)    # at most 30 greenlet
    http = WSGIServer(('0.0.0.0', settings.APISERVER_PORT), app, spawn=p)
    http.serve_forever()
