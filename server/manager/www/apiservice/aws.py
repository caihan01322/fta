# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

import arrow

from flask import request
from fta.utils import logging
from fta.utils.i18n import _, i18n
from fta.www.utils import response, validate
from fta.www.utils.signature import signature_required
from manager.poll_alarm import aws as _aws
from manager.www.apiservice import api_page as app
from project.utils.component import bk

logger = logging.getLogger(__name__)


@app.route("/event/aws/<fta_application_id>/", methods=["POST"])
@response.log
@signature_required
def aws(fta_application_id, cc_biz_id):
    """http://docs.aws.amazon.com/zh_cn/sns/latest/dg/SendMessageToHttp.html
    """
    try:
        # 参数校验
        data = validate.is_json(request.get_data())

        msg_type = data.get('Type')
        # aws订阅后确认逻辑
        if msg_type == 'SubscriptionConfirmation':
            subscribe_url = data.get('SubscribeURL')
            if not subscribe_url:
                raise validate.ValidateError('SubscribeURL Not Found')

            try:
                resp = bk.fta.http_relay__api(
                    app_id=1, method='GET', url=subscribe_url,
                    kwargs={'verify': False, 'timeout': 5})
                logger.info('SubscriptionConfirmation url: %s result: %s' % (subscribe_url, resp))
            except Exception as error:
                logger.error('SubscriptionConfirmation url: %s failed: %s' % (subscribe_url, error))

        elif msg_type == 'Notification':
            data = validate.is_format(data, ['Message'], format='json', replace=True)
            data['Timestamp'] = arrow.get(data['Timestamp']).to('utc').format('YYYY-MM-DD HH:mm:ss')

            dimensions = data['Message']['Trigger']['Dimensions']
            instances = filter(lambda x: x['name'] == 'InstanceId', dimensions)
            if not instances:
                raise validate.ValidateError(_("Not a host-related alarm"))
            instance_id = instances[0]['value']

            # 验证后添加 _CC_HOST_INFO
            data = validate.is_cc_uniq_sn(data, instance_id, replace=True)
            ip = data['_CC_HOST_INNER_IP']

            data = validate.is_cc_uniq_company(data, ip, replace=True)
            cc_biz_id = data['_CC_COMPANY_INFO']['ApplicationID']

            i18n.set_biz(cc_biz_id)

            # 验证后添加 _CC_HOST_INFO
            data = validate.is_cc_host(data, cc_biz_id, ip, replace=True)

            event = _aws.AWSEventAlarm(data, cc_biz_id)
            event.start()
        else:
            raise validate.ValidateError(_("This message format unsupported"))

        # code 200 OK
        result = {'result': True, 'message': 'push aws event success', 'data': {}, 'code': 1200}
    except validate.ValidateError as error:
        # code 400 Bad Request
        result = {'result': False, 'message': u'%s' % error, 'data': {}, 'code': 1400}
    except Exception as error:
        logger.exception('handle aws event error')
        # code 500 Internal Server Error
        result = {'result': False, 'message': 'push aws event error', 'data': {}, 'code': 1500}
    return json.dumps(result)
