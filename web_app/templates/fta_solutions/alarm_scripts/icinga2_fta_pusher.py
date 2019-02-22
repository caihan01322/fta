#!/usr/bin/env python
# coding: utf-8

import argparse
import base64
import json
import logging
import logging.config
import os
import ssl
import sys
import time
import urllib2
from datetime import datetime

FTA_APPLICATION_ID = '{{ fta_application_id }}'
FTA_APPLICATION_SECRET = '{{ fta_application_secret }}'
FTA_DEFAULT_FORMAT = '{{ format|default:"base64" }}'
ENDPOINT = "{{ endpoint }}".rstrip("/")
URL = "%s/icinga2/%s/?format=%s"
CONFIG_TEMPLATE = '''
object User "fta-pusher" {
  import "generic-user"

  display_name = "FTA Pusher"
  groups = [ "fta-pushers" ]
}

object UserGroup "fta-pushers" {
  display_name = "FTA Pusher Group"
}

object NotificationCommand "fta-host-push-command" {
  command = [ SysconfDir + "/icinga2/scripts/fta_push.py" ]

  env = {
    FTAALARMTYPE = "host"
    HOSTADDRESS = "$address$"
    TIME = "$icinga.timet$"
    HOSTSTATE = "$host.state$"
    HOSTOUTPUT = "$host.output$"
    HOSTSTATETYPE = "$host.state_type$"
  }
}

object NotificationCommand "fta-service-push-command" {
  command = [ SysconfDir + "/icinga2/scripts/fta_push.py" ]

  env = {
    FTAALARMTYPE = "service"
    HOSTADDRESS = "$address$"
    TIME = "$icinga.timet$"
    SERVICEDESC = "$service.name$"
    SERVICESTATE = "$service.state$"
    SERVICEOUTPUT = "$service.output$"
    SERVICESTATETYPE = "$service.state_type$"
  }
}

apply Notification "fta-service-push" to Service {
  command = "fta-service-push-command"
  users = ["fta-pusher"]
  user_groups = ["fta-pushers"]
  types = [ "Problem" ]
  states = [ "Warning", "Critical", "Unknown" ]
  period = "24x7"

  assign where service.name
  ignore where host.vars.fta_disabled == true
}

apply Notification "fta-host-push" to Host {
  command = "fta-host-push-command"

  users = ["fta-pusher"]
  user_groups = ["fta-pushers"]
  types = [ "Problem" ]
  states = [ "Down" ]
  period = "24x7"

  assign where host.name
  ignore where host.vars.fta_disabled == true
}
'''

logging.config.dictConfig({
    "version": 1,
    "loggers": {
        "fta": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "/tmp/fta_icinga2_event_handler.log",
            "when": "D",
        },
    },
    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s %(levelname)-8s %(process)-8d"
                "%(name)-15s %(filename)20s[%(lineno)03d] %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    }
})
logger = logging.getLogger("fta")

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError as e:
    logger.info('ssl set _create_unverified_https_context error %s ' % e)
    pass


def push_to_fta(
        fta_application_id, fta_application_secret,
        address, alarm_type_list, source_time, alarm_content,
        format_, retry_times=3, delay_seconds=1,
):
    data = json.dumps({
        "ip": address,
        "source_id": "icinga2-%s%s%s%s" % (
            source_time, hash(fta_application_id),
            hash(address), hash(alarm_content),
        ),
        "alarm_type": ",".join(i for i in alarm_type_list if i),
        "source_time": source_time,
        "alarm_content": (
            base64.b64encode(alarm_content)
            if format_ == "base64" else alarm_content
        ),
        "format": format_,
    })
    code = 1
    message = "push to fta failed"
    for i in range(retry_times):
        if i:
            time.sleep(delay_seconds)  # sleep 3 seconds
        try:
            response = urllib2.urlopen(urllib2.Request(
                URL % (ENDPOINT, fta_application_id, format_,),
                data,
                headers={"X-Secret": fta_application_secret},
            ))
            code = response.code / 100 - 2  # 2xx for success
            logger.info("push response: %s", response.read())
            if not code:
                sys.exit(code)
        except Exception as err:
            message = str(err)
            logger.exception("retry: %s", err)
    print(message)
    sys.exit(code)


def push(parser):
    alarm_type = os.getenv("FTAALARMTYPE")
    time_ts = float(os.getenv("TIME", 0))
    alarm_type_list = []
    state_type = "SOFT"
    alarm = {
        "address": os.getenv("HOSTADDRESS"),
        "source_time": datetime.fromtimestamp(
            time_ts or time.time(),
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "alarm_type_list": alarm_type_list,
    }
    if alarm_type == "host":
        alarm_type_list.append("hostalarm")
        host_state = os.getenv("HOSTSTATE")
        if host_state:
            alarm_type_list.append("host-state-%s", host_state)
        alarm.update({
            "alarm_content": os.getenv("HOSTOUTPUT"),
        })
        state_type = os.getenv("HOSTSTATETYPE", state_type)
    elif alarm_type == "service":
        service_name = os.getenv("SERVICEDESC")
        if service_name:
            alarm_type_list.append(service_name)
            service_state = os.getenv("SERVICESTATE")
            if service_state:
                alarm_type_list.append("%s-%s" % (service_name, service_state))
        alarm.update({
            "alarm_content": os.getenv("SERVICEOUTPUT"),
        })
        state_type = os.getenv("SERVICESTATETYPE", state_type)
    else:
        return

    if state_type != "HARD":
        logger.info("ignore alarm with state type: %s", state_type)
        return
    error = False
    for k, v in alarm.items():
        if not v:
            error = True
            logger.error("%s is empty", k)
    if error:
        return

    push_to_fta(
        fta_application_id=FTA_APPLICATION_ID,
        fta_application_secret=FTA_APPLICATION_SECRET,
        format_=FTA_DEFAULT_FORMAT,
        **alarm
    )


def usage(parser):
    parser.print_usage()


def install(parser):
    parser.add_argument(
        "path", default="/etc/icinga2/",
        help="path to icinga2"
    )
    args = parser.parse_args()
    logger.info("installing fta pusher to %s", args.path)
    with open(os.path.join(args.path, "conf.d/fta_push.conf", ), "wt") as fp:
        fp.write(CONFIG_TEMPLATE)

    fta_push_path = os.path.join(args.path, "scripts/fta_push.py")
    with open(fta_push_path, "wt") as fp1:
        with open(__file__, "rt") as fp2:
            fp1.write(fp2.read())
    os.chmod(fta_push_path, 0755)


def main():
    parser = argparse.ArgumentParser(
        description="icinga2 notification command",
    )
    parser.add_argument(
        "-c", "--command", default="push",
        help="install to icinga2",
    )
    args, _ = parser.parse_known_args()

    handlers = {
        "install": install,
        "push": push,
        "usage": usage,
    }
    handler = handlers.get(args.command, usage)
    return handler(parser)


if __name__ == '__main__':
    main()
