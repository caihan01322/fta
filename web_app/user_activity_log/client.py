# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
上报日志
"""
import json
import logging

from django.utils import timezone
from django.utils.translation import ugettext as _

from .django_conf import REDIS_QUEUE_NAME, ES_STORED, LOG_STORED_TYPE
from .exceptions import DBValidationError, ESValidationError, ParamsValidationError
from .serializers import LogFieldHandler
from .utils import redisdb, get_search_params

logger = logging.getLogger('root')


class UserActivityLogClient(object):
    def __init__(self, log_stored_type=LOG_STORED_TYPE):
        self.log_stored_type = log_stored_type

    def save_data_to_db(self, username, activity_name, log_id=None, app_code=None,
                        activity_type=None, request_params=None, before_data=None,
                        after_data=None, remarks=None, data_limit_size=None,
                        activity_time=None):
        """ db存储数据
            uuid: 用以标识一次操作多表的多条记录
            data_limit_size: 存储数据的大小限制
        """
        from .models import UserActivityLog as UAL

        # 参数有效性
        log_field_validator = LogFieldHandler({
            'log_id': log_id,
            'app_code': app_code,
            'username': username,
            'activity_type': activity_type,
            'activity_name': activity_name,
            'request_params': request_params,
            'before_data': before_data,
            'after_data': after_data,
            'remarks': remarks,
            'data_limit_size': data_limit_size
        })
        if not log_field_validator.is_valid():
            raise ParamsValidationError(log_field_validator.error_message(log_field_validator.errors))
        try:
            save_data = log_field_validator.cleaned_data
            # 如果指定上报时间，则以指定为准
            if activity_time:
                save_data['activity_time'] = activity_time
            log_record = UAL(**save_data)
            log_record.save()
            return log_record.log_id
        except Exception, e:
            logger.exception(u'log error')
            raise DBValidationError(e.message)

    def save_data_to_es(self, username, activity_name, log_id=None, app_code=None,
                        activity_type=1, request_params=None, before_data=None,
                        after_data=None, remarks=None, data_limit_size=None,
                        activity_time=None):
        """ es存储数据
            uuid: 用以标识一次操作多表的多条记录
            data_limit_size: 存储数据的大小限制
        """
        if not redisdb:
            raise ESValidationError(_(u'没有可用的REDIS配置，请参考文档配置'))
        # 参数有效性
        log_field_validator = LogFieldHandler({
            'log_id': log_id,
            'app_code': app_code,
            'username': username,
            'activity_type': activity_type,
            'activity_name': activity_name,
            'request_params': request_params,
            'before_data': before_data,
            'after_data': after_data,
            'remarks': remarks,
            'data_limit_size': data_limit_size
        })
        if not log_field_validator.is_valid():
            raise ParamsValidationError(log_field_validator.error_message(log_field_validator.errors))

        log_data = log_field_validator.cleaned_data
        # 如果指定上报时间，则以指定为准
        log_data['activity_time'] = activity_time or timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            redisdb.rpush(REDIS_QUEUE_NAME, json.dumps(log_data))
            return log_data['log_id']
        except Exception, e:
            logger.exception(u'log error')
            raise ESValidationError(e.message)

    def search_log_from_es(self):
        """现阶段先不支持es的查询
        原因是由于es的版本及需要es包
        """
        pass

    def search_log_from_db(self, log_id=None, app_code=None,
                           username=None, activity_type=None,
                           activity_name=None, start_time=None, end_time=None):
        """数据库记录查询"""
        if not start_time:
            raise ParamsValidationError(_(u'查询的起始时间参数[start_time]不能为空'))
        # 如果结束时间不存在，默认取当前时间
        end_time = end_time or timezone.now()
        # 处理参数
        search_params = get_search_params(
            {
                'log_id': log_id,
                'app_code': app_code,
                'username': username,
                'activity_type': activity_type,
                'activity_name': activity_name,
            }
        )
        from .models import UserActivityLog as UAL
        return UAL.objects.filter(activity_time__lte=end_time, activity_time__gte=start_time, **search_params)

    def log(self, *args, **kwargs):
        """存储数据"""
        if self.log_stored_type == ES_STORED:
            return self.save_data_to_es(*args, **kwargs)
        else:
            return self.save_data_to_db(*args, **kwargs)

    def search_log(self, *args, **kwargs):
        """查询记录"""
        if self.log_stored_type == ES_STORED:
            raise ESValidationError(_(u'暂不支持ES记录查询！'))
        else:
            return self.search_log_from_db(*args, **kwargs)


# client
UserActivityLog = UserActivityLogClient()
