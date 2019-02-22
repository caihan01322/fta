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
from manager.poll_alarm import rest_api
from manager.www.apiservice import api_page as app

logger = logging.getLogger(__name__)


@app.route("/event/api/<fta_application_id>/", methods=["POST"])
@response.log
@signature_required
def event_restapi(fta_application_id, cc_biz_id):
    """通过api上报告警数据
    """
    try:
        # 参数校验
        data = validate.is_json(request.get_data())
        data = validate.is_required(data, ['ip', 'source_id', 'source_time', 'alarm_type', 'alarm_content'])
        data = validate.is_ip(data, ['ip'])
        # 只验证,不替换
        data = validate.is_datetime(data, ['source_time'], replace=True, tzinfo=i18n.get_timezone())
        # 验证，替换解析后的值
        data = validate.is_format(data, ['alarm_content'], format=data.get('format'), replace=True)

        # 验证ip是否在CC中合法
        # 验证后添加 _CC_COMPANY_INFO
        data = validate.is_cc_uniq_company(data, data['ip'], replace=True)
        cc_biz_id = data['_CC_COMPANY_INFO']['ApplicationID']
        i18n.set_biz(cc_biz_id)
        # 验证后添加 _CC_HOST_INFO
        data = validate.is_cc_host(data, cc_biz_id, data['ip'], replace=True)
        # 替换source_id
        data = validate.fix_field_by_app(data, ["source_id"], fta_application_id)

        event = rest_api.RestApiEventAlarm(data, cc_biz_id)
        event.start()

        # code 200 OK
        result = {'result': True, 'message': 'push restapi event success', 'data': {}, 'code': 1200}
    except validate.ValidateError as error:
        # code 400 Bad Request
        result = {'result': False, 'message': u'%s' % error, 'data': {}, 'code': 1400}
    except Exception as error:
        logger.exception('handle restapi event error')
        # code 500 Internal Server Error
        result = {'result': False, 'message': 'push restapi event error', 'data': {}, 'code': 1500}
    return json.dumps(result)
