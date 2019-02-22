#!/bin/bash

SHELL_FLODER=$(cd "$(dirname "$0")"; pwd)
CONF_HOME="${CONF_HOME:-$(dirname $SHELL_FLODER)}"
PROJECT_HOME="${PROJECT_HOME:-$(dirname $SHELL_FLODER)}"

# 配置文件目录
SUPERVISOR_CONF="$CONF_HOME/supervisor-fta-fta.conf"
SUPERVISOR_IDENTIFIER="supervisord.*$SUPERVISOR_CONF"

# 检查环境变量是否OK
function check_env() {
    if [ ! $CONF_HOME ]; then
        echo 'shell env [CONF_HOME] not config'
        return 0
    fi
    if [ ! $PROJECT_HOME ]; then
        echo 'shell env [PROJECT_HOME] not config'
        return 0
    fi
    return 1
}

if check_env; then
    echo '[exited].'
    exit 1
fi

# 判断 supervisor是否已经启动
function is_supervisor_exists() {
    ps -ef | grep "$SUPERVISOR_IDENTIFIER" | grep -vq grep
    return $?
}

# 启动 supervisor
function start_supervisor() {
    if ! is_supervisor_exists; then
        echo "starting supervisor..."
        supervisord -c $SUPERVISOR_CONF -i $SUPERVISOR_IDENTIFIER
        welcome
    fi
    echo "starting fta..."

    if [ -z "$2" ] || [ "$2" == "all" ]; then
        supervisorctl -c $SUPERVISOR_CONF start fta:
        supervisorctl -c $SUPERVISOR_CONF start common:
        supervisorctl -c $SUPERVISOR_CONF start all
    else
        supervisorctl -c $SUPERVISOR_CONF start $2:
    fi

    cd $PROJECT_HOME && python -m fta.script.rebuild_dimension > /dev/null 2>&1
    echo "[started]."
}

# 停止 supervisor
function stop_supervisor() {
    if is_supervisor_exists; then
        echo "stopping fta..."

        if [ -z "$2" ] || [ "$2" == "all" ]; then
            supervisorctl -c $SUPERVISOR_CONF stop fta:
            supervisorctl -c $SUPERVISOR_CONF stop common:
            supervisorctl -c $SUPERVISOR_CONF stop all
        else
            supervisorctl -c $SUPERVISOR_CONF stop $2:
        fi

        echo "[stopped]."
    else
        echo "supervisor is not running."
    fi
}

# 状态 supervisor
function status_supervisor() {
    if is_supervisor_exists; then
        supervisorctl -c $SUPERVISOR_CONF status
    else
        echo "supervisor is not running."
    fi
}

function reload_supervisor() {
    if is_supervisor_exists; then
        supervisorctl -c $SUPERVISOR_CONF update
        echo "[reloaded]."
    else
        echo "supervisor is not running."
    fi
}

function shutdown_supervisor() {
    if is_supervisor_exists; then
        supervisorctl -c $SUPERVISOR_CONF "shutdown"
        echo "[supervisord is down]."
    else
        echo "supervisor is not running."
    fi
}

# Project Name
function welcome() {
    echo "      ___                         ___      "
    echo "     /\__\                       /\  \     "
    echo "    /:/ _/_         ___         /::\  \    "
    echo "   /:/ /\__\       /\__\       /:/\:\  \   "
    echo "  /:/ /:/  /      /:/  /      /:/ /::\  \  "
    echo " /:/_/:/  /      /:/__/      /:/_/:/\:\__\ "
    echo " \:\/:/  /      /::\  \      \:\/:/  \/__/ "
    echo "  \::/__/      /:/\:\  \      \::/__/      "
    echo "   \:\  \      \/__\:\  \      \:\  \      "
    echo "    \:\__\          \:\__\      \:\__\     "
    echo "     \/__/           \/__/       \/__/     "
    echo "                                           "
}


#############
# Main Loop #
#############

case $1 in
    start)
        start_supervisor
        ;;
    stop)
        stop_supervisor
        ;;
    restart)
        stop_supervisor
        start_supervisor
        ;;
    reload)
        reload_supervisor
        ;;
    status)
        status_supervisor
        ;;
    shutdown)
        shutdown_supervisor
        ;;
    *)
        echo "usage $0 {start|stop|restart|reload|status|shutdown}"
        exit 1
        ;;
esac
