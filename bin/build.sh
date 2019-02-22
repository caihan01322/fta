#!/bin/bash

SHELL_FLODER=$(cd "$(dirname "$0")"; pwd)
ROOT_PATH="${CONF_HOME:-$(dirname $SHELL_FLODER)}"

WEB_APP_HOME=${ROOT_PATH}"/web_app"
SERVER_HOME=${ROOT_PATH}"/server"

function build_saas() {

    cd $ROOT_PATH

    APP_CODE="bk_fta_solutions"

    mkdir -p  ${APP_CODE} || exit 1
    mkdir -p $APP_CODE/src $APP_CODE/pkgs || exit 1

    rsync -av ${WEB_APP_HOME}/ ${APP_CODE}/src/ || exit 1

    # download python packages
    cp ${WEB_APP_HOME}/app.yml $APP_CODE/ || exit 1

    _CURRENT=`date "+%Y-%m-%d %H:%M:%S"`
    echo "!!python/unicode 'language': python" >> $APP_CODE/app.yml
    echo "!!python/unicode 'date': '${_CURRENT}'" >> $APP_CODE/app.yml
    echo "libraries:" >> $APP_CODE/app.yml
    grep -e "^[^#].*$" ${WEB_APP_HOME}/requirements.txt | awk '{split($1,b,"==");printf "- name: "b[1]"\n  version: "b[2]"\n"}' >> $APP_CODE/app.yml
    pip download -d ${APP_CODE}/pkgs/ -r ${WEB_APP_HOME}/requirements.txt || exit 1

    # generate release files
    CURRENT=`date "+%Y%m%d%H%M%S"`
    pkg_name="$APP_CODE-$CURRENT.tar.gz"
    echo "pkg: $APP_CODE-$CURRENT-$1.tar.gz"
    tar -zcvf "$APP_CODE-$CURRENT-$1.tar.gz" $APP_CODE 1>/dev/null 2>&1

    clear_build_env ${APP_CODE}
}


function build_server() {
    cd $ROOT_PATH

    APP_CODE="fta"

    mkdir -p ${APP_CODE} || exit 1
    mkdir -p $APP_CODE/fta || exit 1

    mkdir -p $APP_CODE/support-files || exit 1
    mkdir -p $APP_CODE/support-files/sql $APP_CODE/support-files/pkgs $APP_CODE/support-files/templates || exit 1

    rsync -av ${SERVER_HOME}/ ${APP_CODE}/fta/ || exit 1

    mv "${APP_CODE}/fta/project/settings_env.py" "$APP_CODE/support-files/templates/fta#project#settings_env.py"
    mv "${APP_CODE}/fta/project/supervisor-fta-fta.conf" "$APP_CODE/support-files/templates/#etc#supervisor-fta-fta.conf"
    cp "./sql/init_fta.sql" "$APP_CODE/support-files/sql/0001_fta_20180727-1814_mysql.sql"

    # download python packages
    cp ${SERVER_HOME}/project/release.md $APP_CODE/ || exit 1

    touch $APP_CODE/VERSION
    echo $1 > $APP_CODE/VERSION

    pip download -d ${APP_CODE}/support-files/pkgs/ -r ${SERVER_HOME}/requirements.txt || exit 1

    # generate release files
    CURRENT=`date "+%Y%m%d%H%M%S"`
    pkg_name="$APP_CODE-$CURRENT.tar.gz"
    echo "pkg: $APP_CODE-$CURRENT-$1.tar.gz"
    tar -zcvf "$APP_CODE-$CURRENT-$1.tar.gz" $APP_CODE 1>/dev/null 2>&1

    clear_build_env ${APP_CODE}
}

function clear_build_env() {
    if [ ! $1 ]; then
        echo ""
        exit 1
    else
        rm -rf $1 || exit 1
    fi
}


#############
# Main Loop #
#############
case $1 in
    web_app)
        build_saas $2
        ;;
    server)
        build_server $2
        ;;
    *)
        echo "usage $0 {web_app|server} {VERSION}"
        exit 1
        ;;
esac
