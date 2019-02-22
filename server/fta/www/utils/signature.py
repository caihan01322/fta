# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""API签名公共类"""
import datetime
import hashlib
import hmac
import json
import re
import time
from functools import wraps

from sqlalchemy.orm.exc import NoResultFound

from flask import request
from fta import settings
from fta.storage.mysql import session
from fta.storage.tables import AlarmApplication
from fta.utils import logging
from fta.utils.i18n import _

logger = logging.getLogger(__name__)


class SignError(Exception):
    pass


class Sign(object):

    def __init__(self, fta_application_id):
        self.fta_application_id = fta_application_id
        self.request = request

        if settings.SIGNATURE_HOST:
            self.host = settings.SIGNATURE_HOST
        else:
            self.host = request.host
        if settings.SIGNATURE_PREFIX:
            self.url = settings.SIGNATURE_PREFIX + request.path
        else:
            self.url = request.path

        self.method = request.method

        self.clean_field = ['clean_nonce', 'clean_timestamp']

    def clean_nonce(self):
        """随机字符串，Nonce验证"""
        nonce = self.request.args.get('Nonce')
        if not nonce:
            raise SignError(_("Nonce does not exist"))

        if len(nonce) > 32:
            raise SignError(_("Nonce must be less than 32 chars in length"))

        return nonce

    def clean_timestamp(self):
        """时间戳验证"""
        timestamp = self.request.args.get('Timestamp')
        if not timestamp:
            raise SignError(_("Timestamp does not exist"))

        if not re.match(r'^[1-9][0-9]*$', timestamp):
            raise SignError(_("Timestamp must be a positive integer"))

        now = int(time.time())

        max_offset = 300
        timestamp = int(timestamp)

        if timestamp < now - max_offset or timestamp > now + max_offset:
            raise ValueError(
                _("Timestamp invalid. Time error must be within %(offset)s second(s). Current server time: %(now)s",
                  offset=max_offset, now=now))

        return timestamp

    def get_signature(self):
        signature = self.request.args.get('Signature')
        if not signature:
            raise ValueError(_("Signature does not exist"))
        return signature

    def get_app_secret(self):
        try:
            app = session.query(AlarmApplication).filter_by(
                app_id=self.fta_application_id,
                is_enabled=True,
                is_deleted=False).first()
            return app.app_secret
        except NoResultFound:
            raise SignError(_("APP does not exist"))

    @classmethod
    def compute_signature(cls, method, host, url, params, app_secret):
        """生成签名"""
        message = '%s%s%s?%s' % (method, host, url, params)
        signature = hmac.new(app_secret, message, hashlib.sha256).hexdigest()
        return signature

    def clean_get(self):
        params = dict(self.request.args.items())
        params.pop(u"Signature", None)
        params = '&'.join(['%s=%s' % (i, params[i]) for i in sorted(params)])
        return params

    def clean_post(self):
        params = dict(self.request.args.items())
        params.pop(u"Signature", None)
        raw_data = self.request.get_data()
        params['Data'] = raw_data
        params = '&'.join(['%s=%s' % (i, params[i]) for i in sorted(params)])
        return params

    def validate(self):
        for i in self.clean_field:
            _clean = getattr(self, i)
            _clean()
        app_secret = self.get_app_secret()
        clean_signature = self.get_signature()

        if self.method == 'GET':
            params = self.clean_get()
        elif self.method == 'POST':
            params = self.clean_post()
        else:
            raise SignError(_("Support GET, POST only"))

        _signature = self.compute_signature(self.method, self.host, self.url, params, app_secret)
        if _signature != clean_signature:
            raise SignError(_("Signature error, please confirm app_secret and signature algorithm"))


def check_app_secret(fta_application_id):
    """检查app_secret
    """
    app = session.query(AlarmApplication).filter_by(
        app_id=fta_application_id,
        is_enabled=True,
        is_deleted=False).first()
    if not app:
        raise SignError(_("app not exist"))

    # flask不管大小写，会标准成X-Secret
    app_secret = request.headers.get('X-Secret') or request.args.get('secret')
    if not app_secret:
        raise SignError(_("Secret does not exist. Please add X-Secret to header or add secret to request parameter."))

    if app.app_secret != app_secret:
        raise SignError(_("Secret invalid"))

    return app


def signature_required(view_func):
    """使用check_app_secret检查头部
    """
    @wraps(view_func)
    def _wrapped_view(fta_application_id, *args, **kwargs):
        try:
            app = check_app_secret(fta_application_id)
            session.query(AlarmApplication).filter_by(id=app.id).update({
                "activate_time": datetime.datetime.utcnow(),
            })
        except SignError as error:
            content = {'message': u"%s" % error, 'result': False, 'data': {}, 'code': '1400'}
            return json.dumps(content)
        except Exception as error:
            logger.exception('signature_required error')
            content = {'message': _("API error, please contact admin for resolution"),
                       'result': False, 'data': {}, 'code': '1500'}
            return json.dumps(content)
        return view_func(fta_application_id, cc_biz_id=app.cc_biz_id, *args, **kwargs)
    return _wrapped_view
