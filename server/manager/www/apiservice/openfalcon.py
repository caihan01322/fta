# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from flask import request
from fta.utils import logging
from fta.utils.i18n import i18n
from fta.www.utils import response, validate
from fta.www.utils.signature import signature_required
from manager.poll_alarm import openfalcon
from manager.www.apiservice import api_page as app

logger = logging.getLogger(__name__)


@app.route("/event/open-falcon/<fta_application_id>/", methods=["GET"])
@response.log
@signature_required
def event_openfalcon(fta_application_id, cc_biz_id):
    """OPEN-FALCON callback上报数据
    1，需要配置callback URL
    2，配置agent hostname为IP地址
    """
    try:
        data = dict(request.args.items())

        # 参数校验
        data = validate.is_required(data, ['endpoint', 'time', 'metric'])
        data = validate.is_cc_uniq_hostname(data, data['endpoint'], replace=True)
        ip = data['_CC_HOST_INNER_IP']

        data = validate.is_cc_uniq_company(data, ip, replace=True)
        cc_biz_id = data['_CC_COMPANY_INFO']['ApplicationID']

        i18n.set_biz(cc_biz_id)
        # 只验证,不替换
        data['source_time'] = data['time'].replace('+', ' ')
        data = validate.is_datetime(data, ['source_time'], replace=True, tzinfo=i18n.get_timezone())

        # 验证ip是否在CC中合法
        # 验证后添加 _CC_HOST_INFO
        data = validate.is_cc_host(data, cc_biz_id, ip, replace=True)

        event = openfalcon.OpenFalconEventAlarm(data, cc_biz_id)
        event.start()

        # code 200 OK
        result = {'result': True, 'message': 'push openfalcon event success', 'data': {}, 'code': 1200}
    except validate.ValidateError as error:
        # code 400 Bad Request
        result = {'result': False, 'message': u'%s' % error, 'data': {}, 'code': 1400}
    except Exception as error:
        logger.exception('handle openfalcon event error')
        # code 500 Internal Server Error
        result = {'result': False, 'message': 'push openfalcon event error', 'data': {}, 'code': 1500}
    return json.dumps(result)
