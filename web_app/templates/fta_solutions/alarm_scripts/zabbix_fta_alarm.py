#!/usr/bin/env python
# -*- coding: utf-8 -*
import base64
import getopt
import json
import logging
import sys
import time
import ssl

# python3 compatibility
try:
    import urllib2 as request
except Exception:
    from urllib import request

try:
    from urlparse import urlparse
except Exception:
    from urllib.parse import urlparse

# python2 encoding compatibility
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except Exception:
    pass

LOG_FORMAT = '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
LOG_FILE = '/tmp/zabbix_fta_alarm.log'
LOG = logging.getLogger('fta')

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError as e:
    LOG.info('ssl set _create_unverified_https_context error %s ' % e)
    pass

FTA_APPLICATION_ID = '{{ fta_application_id }}'
FTA_SECERT = '{{ fta_application_secret }}'
FTA_FORMAT = '{{ format|default:"base64" }}'
ENDPOINT = "{{ endpoint }}".rstrip("/")
FTA_URL = '%s/zabbix/v3.0/%s/' % (ENDPOINT, FTA_APPLICATION_ID)

# 告警消息体
ACTION_MESSAGE_BODY = '''
========================
HOST.IP: {HOST.IP}
HOST.CONN: {HOST.CONN}
HOST.HOST: {HOST.HOST}
HOST.DESCRIPTION: {HOST.DESCRIPTION}
ITEM.ID: {ITEM.ID}
ITEM.KEY: {ITEM.KEY}
ITEM.VALUE: {ITEM.VALUE}
ITEM.DESCRIPTION: {ITEM.DESCRIPTION}
TRIGGER.ID: {TRIGGER.ID}
TRIGGER.NAME: {TRIGGER.NAME}
TRIGGER.EXPRESSION: {TRIGGER.EXPRESSION}
TRIGGER.DESCRIPTION: {TRIGGER.DESCRIPTION}
TRIGGER.URL: {TRIGGER.URL}
TRIGGER.SEVERITY: {TRIGGER.SEVERITY}
TRIGGER.STATUS: {TRIGGER.STATUS}
EVENT.ID: {EVENT.ID}
EVENT.TIME: {EVENT.TIME}
EVENT.DATE: {EVENT.DATE}
EVENT.VALUE: {EVENT.VALUE}
ACTION.ID: {ACTION.ID}
ACTION.NAME: {ACTION.NAME}
========================
'''


def _setup_logging(verbose=None, filename=None):
    """设置日志级别
    """
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format=LOG_FORMAT, level=level, filename=filename)


def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    return s.encode(encoding, errors)


def force_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    if issubclass(type(s), str):
        return s

    if isinstance(s, bytes):
        s = str(s, encoding, errors)
    else:
        s = str(s)

    return s


def http_post(url, data, resp_fmt='json'):
    """POST方法封装
    data is dict or string
    """
    st = time.time()

    if isinstance(data, dict):
        data = json.dumps(data)
    data = force_bytes(data)

    LOG.debug("curl -X POST '%s' -d '%s' -H 'Content-Type: application/json'", url, data)

    req = request.Request(url, data=data, headers={'Content-Type': 'application/json', 'X-Secret': FTA_SECERT})
    resp = request.urlopen(req, timeout=5).read()
    LOG.debug('RESP: %.2fms %s', (time.time() - st) * 1000, resp)
    if resp_fmt == 'json':
        resp = json.loads(resp)
    return resp


class APIError(Exception):
    pass


class ZabbixApi(object):

    def __init__(self, parse_url, user, password):
        self.parse_url = parse_url
        self.user = user
        self.password = password
        self.path = '/zabbix/api_jsonrpc.php'
        self.url = '%s://%s%s' % (parse_url.scheme, parse_url.netloc, parse_url.path or self.path)

        self.auth_token = None
        self.userid = None
        self.mediatypeid = None
        self.usrgrpid = 7  # Zabbix administrators

        self.script_name = 'zabbix_fta_alarm.py'
        self.media_name = 'FTA_Event_Handler'
        self.user_name = 'FTA_Mgr'
        self.action_name = 'FTA_Act'

    def user_login(self):
        """用户登录，获取token
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password
            },
            "id": 1,
            "auth": None
        }
        resp = http_post(self.url, data=payload)
        token = resp.get('result')
        LOG.info('get auth token: %s' % token)
        if not token:
            raise APIError(u"Zabbix账号密码不正确，请输入管理员账号密码")
        self.auth_token = token

    def mediatype_get(self):
        """
        获取以前老的mediatype
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "mediatype.get",
            "params": {
                "output": "mediatypeid",
                "filter": {'description': self.media_name},
            },
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'mediatype_get success: %s', resp)
        return [i['mediatypeid'] for i in resp['result']]

    def mediatype_delete(self, media_type_ids):
        """
        删除mediatype
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "mediatype.delete",
            "params": media_type_ids,
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'mediatype_delete success: %s', resp)

    def mediatype_create(self):
        """
        创建脚本
        """
        exec_params = [
            # '{ALERT.SUBJECT}',
            '{ALERT.MESSAGE}',
        ]
        payload = {
            "jsonrpc": "2.0",
            "method": "mediatype.create",
            "params": {
                "description": self.media_name,
                "exec_path": self.script_name,
                "exec_params": '\r\n'.join(exec_params) + '\r\n',
                "type": 1,  # script type
                "status": 0  # enable default

            },
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info('mediatype_create success: %s', resp)
        self.mediatypeid = resp['result']['mediatypeids'][0]

    def user_get(self):
        """
        获取以前老的mediatype
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "user.get",
            "params": {
                "output": "userid",
                "filter": {'alias': self.user_name},
            },
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'user_get success: %s', resp)
        return [i['userid'] for i in resp['result']]

    def user_delete(self, user_ids):
        """
        删除mediatype
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "user.delete",
            "params": user_ids,
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'user_delete success: %s', resp)

    def user_create(self):
        """创建FTA用户
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "user.create",
            "params": {
                "alias": self.user_name,
                "name": self.user_name,
                "surname": self.user_name,
                "passwd": FTA_APPLICATION_ID,
                "type": 3,  # Zabbix super admin
                "usrgrps": [
                    {
                        "usrgrpid": self.usrgrpid
                    }
                ],
                "user_medias": [
                    {
                        "mediatypeid": self.mediatypeid,
                        "sendto": self.user_name,
                        "active": 0,
                        "severity": 63,  # all severity
                        "period": "1-7,00:00-24:00"
                    }
                ]
            },
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'user_create success: %s', resp)
        self.userid = resp['result']['userids'][0]

    def action_get(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "action.get",
            "params": {
                "output": "actionids",
                "filter": {'name': self.action_name},
            },
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'action_get success: %s', resp)
        return [i['actionid'] for i in resp['result']]

    def action_delete(self, action_ids):
        """
        删除mediatype
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "action.delete",
            "params": action_ids,
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'action_delete success: %s', resp)

    def action_create(self):
        """创建触发器
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "action.create",
            "params": {
                "name": self.action_name,
                "eventsource": 0,
                "status": 0,
                "esc_period": 3600,
                "def_shortdata": self.action_name + " {TRIGGER.NAME}: {TRIGGER.STATUS}",
                "def_longdata": ACTION_MESSAGE_BODY,
                "filter": {
                    "evaltype": 0,  # and/or
                    "conditions": [
                        {
                            "conditiontype": 16,  # Maintenance status
                            "operator": 7,  # not in
                            "value": ''  # Maintenance must be empty
                        },
                        # zabbix 3.2/3.4 don't have trigger value
                        # {
                        #     "conditiontype": 5,  # trigger value
                        #     "operator": 0,  # =
                        #     "value": 1  # problem
                        # }
                    ]
                },
                "operations": [
                    {
                        "operationtype": 0,  # send message
                        "esc_period": 0,
                        "esc_step_from": 1,
                        "esc_step_to": 1,
                        "evaltype": 0,
                        "opmessage_usr": [{
                            "userid": self.userid
                        }],
                        "opmessage": {
                            "default_msg": 1,
                            "mediatypeid": self.mediatypeid
                        }
                    }
                ]
            },
            "auth": self.auth_token,
            "id": 1
        }
        resp = http_post(self.url, data=payload)
        LOG.info(u'action_create success: %s', resp)

    def clean(self):
        """清理数据
        """
        action_ids = self.action_get()
        if action_ids:
            self.action_delete(action_ids)

        user_ids = self.user_get()
        if user_ids:
            self.user_delete(user_ids)

        media_type_ids = self.mediatype_get()
        if media_type_ids:
            self.mediatype_delete(media_type_ids)


class Event(object):

    def __init__(self, message, format='base64'):
        self.message = message
        self.format = format

    def parse(self, data):
        alarm = {}
        data = data.strip('=\r\n ')
        # 格式化数据
        for line in data.splitlines():

            try:
                key, value = line.split(':', 1)
            except Exception as error:
                LOG.info(u"parse line %s error: %s, just ignore." % (line, error))
                continue

            key = key.strip()
            value = value.strip()
            alarm[key] = value
        return alarm

    def clean_ip(self, alarm):
        return alarm['HOST.IP']

    def clean_source_time(self, alarm):
        return '%s %s' % (alarm['EVENT.DATE'].replace('.', '-'), alarm['EVENT.TIME'])

    def clean_source_id(self, alarm):
        return '%s-%s-%s-%s' % (alarm['ITEM.ID'], alarm['TRIGGER.ID'], alarm['EVENT.ID'], alarm['ACTION.ID'])

    def clean_alarm_type(self, alarm):
        return alarm["ITEM.KEY"]

    def clean_alarm_content(self, alarm):
        return '%s(%s)' % (alarm['TRIGGER.NAME'], alarm['TRIGGER.DESCRIPTION'])

    def clean_data(self):
        alarm = self.parse(self.message)
        ip = self.clean_ip(alarm)
        source_time = self.clean_source_time(alarm)
        source_id = self.clean_source_id(alarm)
        alarm_type = self.clean_alarm_type(alarm)
        alarm_content = self.clean_alarm_content(alarm)
        alarm_raw = json.dumps(alarm)

        if self.format == 'base64':
            alarm_content = force_str(base64.b64encode(force_bytes(alarm_content)))
            alarm_raw = force_str(base64.b64encode(force_bytes(alarm_raw)))

        data = {'ip': ip,
                'source_time': source_time,
                'source_id': source_id,
                'alarm_type': alarm_type,
                'alarm_content': alarm_content,
                'alarm_raw': alarm_raw,
                'format': self.format}
        return data

    def send(self):
        """消息处理函数
        """
        data = self.clean_data()
        resp = http_post(FTA_URL, data=data, resp_fmt=None)
        LOG.info(u'send alarm resp: %s', resp)


def launcher(init, verbose, params):
    if init:
        _setup_logging(verbose)
        # params[0] is api host
        # params[1] is api user
        # params[2] is api password
        # 注意文件权限

        if len(params) < 3:
            raise APIError(u"初始化参数不正确，请依次输入Zabbix API地址, 管理员账号, 管理员账号密码")
        # 校验URL
        parse_url = urlparse(params[0])
        if parse_url.scheme not in ['http', 'https'] or not parse_url.netloc:
            raise APIError(u"Zabbix API（%s）地址不正确" % params[0])

        api_client = ZabbixApi(parse_url, params[1], params[2])
        api_client.user_login()

        api_client.clean()

        api_client.mediatype_create()
        api_client.user_create()
        api_client.action_create()
    else:
        # params[0] is {ALERT.MESSAGE}
        _setup_logging(True, filename=LOG_FILE)
        event = Event(params[0], FTA_FORMAT)
        event.send()


USAGE = """
usage: zabbix_fta_alarm.py [-h] [--init] [--verbose] params [params ...]

Blueking FTA Application

positional arguments:
  params         zabbix params

optional arguments:
  -h, --help     show this help message and exit
  --init         init zabbix action config
  --verbose, -v  verbose mode
"""


def usage():
    print(USAGE.strip())


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose", "init"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    init = False
    verbose = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("--init",):
            init = True
        else:
            print(u"unhandled option, (%s, %s)" % (o, a))
            sys.exit(2)

    if not args:
        usage()
        sys.exit(2)

    try:
        launcher(init, verbose, args)
    except APIError as error:
        # 安装提示错误
        LOG.error(u'%s', error)
    except Exception:
        LOG.exception('fta script error')
        sys.exit(1)


if __name__ == "__main__":
    main()
