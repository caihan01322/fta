#!/usr/bin/env python
# coding: utf-8

import sys
import json
import base64
import urllib2
import argparse
import time
import logging
import ssl
from datetime import datetime

FTA_APPLICATION_SECRET = '{{ fta_application_secret }}'
FTA_APPLICATION_ID = '{{ fta_application_id }}'
FTA_DEFAULT_FORMAT = '{{ format|default:"base64" }}'
ENDPOINT = "{{ endpoint }}".rstrip("/")
URL = "%s/nagios/%s/?format=%s"
NAGIOS_TEMPALTE = '''
define command {
        command_name    fta_push_host_alarm
        command_line    /usr/local/nagios/libexec/eventhandlers/nagios_fta_event_handler.py host "$HOSTADDRESS$" "hostalarm" "$HOSTEVENTID$" "$HOSTSTATE$" "$HOSTSTATETYPE$" "$HOSTOUTPUT$" -s "$ARG1$" -g "$HOSTGROUPNAMES$"
}

define command {
        command_name    fta_push_service_alarm
        command_line    /usr/local/nagios/libexec/eventhandlers/nagios_fta_event_handler.py service "$HOSTADDRESS$" "$SERVICEDESC$" "$SERVICEEVENTID$" "$SERVICESTATE$" "$SERVICESTATETYPE$" "$SERVICEOUTPUT$" -s "$ARG1$" -g "$SERVICEGROUPNAMES$"
}

define host {
        name    fta_alarm_host_template
        event_handler_enabled   1
        event_handler   fta_push_host_alarm
        register        0
}

define service {
        name    fta_alarm_service_template
        event_handler_enabled   1
        event_handler   fta_push_service_alarm
        register        0
}

global_host_event_handler = fta_push_host_alarm
global_service_event_handler = fta_push_service_alarm
'''  # noqa

logging.basicConfig(
    level=logging.INFO,
    filename="/tmp/fta_nagios_event_handler.log",
)
logger = logging.getLogger()

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError as e:
    logger.info('ssl set _create_unverified_https_context error %s ' % e)
    pass


def main():
    parser = argparse.ArgumentParser(description="Nagios event handler for fta")
    parser.add_argument(
        "type", choices=["host", "service", "test"],
        default="service", help="event handler type",
    )
    parser.add_argument(
        "address", help="host ip address($HOSTADDRESS$)",
    )
    parser.add_argument(
        "service", help="event description($SERVICEDESC$)",
    )
    parser.add_argument(
        "source_id", help="event id($SERVICEEVENTID$/$HOSTEVENTID$)",
    )
    parser.add_argument(
        "status", help="event status($SERVICESTATE$/$HOSTSTATE$)",
    )
    parser.add_argument(
        "status_type",
        help="event status type($SERVICESTATETYPE$/$HOSTSTATETYPE$)",
    )
    parser.add_argument(
        "info", help="event info($SERVICEOUTPUT$/$HOSTOUTPUT$)",
    )
    parser.add_argument(
        "-i", "--fta_application_id", default=FTA_APPLICATION_ID,
        help="fta application id",
    )
    parser.add_argument(
        "-s", "--fta_application_secret", default=FTA_APPLICATION_SECRET,
        help="fta application secret",
    )
    parser.add_argument(
        "-t", "--time", default=None,
        help="alram time($SHORTDATETIME$)",
    )
    parser.add_argument(
        "-g", "--groups", default="",
        help="event groups",
    )
    parser.add_argument(
        "-f", "--format", default=FTA_DEFAULT_FORMAT,
        help="request format",
    )
    parser.add_argument(
        "-n", "--retry_times", default=3,
        help="max retry times",
    )
    parser.add_argument(
        "-d", "--delay_seconds", default=3,
        help="delay seconds before retry",
    )
    parser.add_argument(
        "--unavailable_status_type", nargs="+",
        default=["SOFT"],
    )
    parser.add_argument(
        "--unavailable_status", nargs="+",
        default=["OK", "UP"],
    )

    args = parser.parse_args()

    if args.status_type in args.unavailable_status_type:
        return

    if args.status in args.unavailable_status:
        return

    fta_application_id = (
        args.fta_application_id or FTA_APPLICATION_ID
    )
    fta_application_secret = (
        args.fta_application_secret or FTA_APPLICATION_SECRET
    )
    source_time = args.time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alarm_type_list = args.groups.split(",")
    alarm_type_list.append(args.service.replace(",", "."))
    code = -1
    data = json.dumps({
        "ip": args.address,
        "source_id": "nagios-%s-%s" % (args.type, args.source_id),
        "alarm_type": ",".join(i for i in alarm_type_list if i),
        "source_time": source_time,
        "alarm_content": (
            base64.b64encode(args.info)
            if args.format == "base64" else args.info
        ),
        "format": args.format,
    }) if args.type != "test" else ""
    logger.info("push event data: %s", data)

    for i in range(args.retry_times):
        if i:
            time.sleep(args.delay_seconds)  # sleep 3 seconds
        try:
            response = urllib2.urlopen(urllib2.Request(
                URL % (ENDPOINT, fta_application_id, args.format), data,
                headers={"X-Secret": fta_application_secret},
            ))
            code = response.code / 100 - 2  # 2xx for success
            if not code:
                print("ok!")
                sys.exit(code)
        except Exception as err:
            logger.exception("retry: %s", err)
    sys.exit(code)


if __name__ == '__main__':
    main()
