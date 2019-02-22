#!/bin/bash
# init script

SHELL_FLODER=$(cd "$(dirname "$0")"; pwd)
ROOT_PATH="${CONF_HOME:-$(dirname $SHELL_FLODER)}"
TEMPLATE_HOME=${ROOT_PATH}'/fta/templates/conf'
LOGS_HOME=${ROOT_PATH}'/logs'
TMP_DIR=${ROOT_PATH}'/tmp'

function init_tmp() {
    mkdir -p ${TMP_DIR}
}

# 选择代码目录
function init_dir() {
    mkdir -p ${LOGS_HOME}
}

# 选择配置文件
function init_settings() {
    cp ${TEMPLATE_HOME}/settings_local.py project/settings_env.py
}

# 生成配置
function init_conf() {
    cp project/settings.py ${TMP_DIR}/settings_env.py
    cp fta/settings.py ${TMP_DIR}/settings.py
    cp ${TEMPLATE_HOME}/supervisord_template.conf ${TMP_DIR}/supervisord_template.conf
    cp ${TEMPLATE_HOME}/__init__.py ${TMP_DIR}/__init__.py
    cp fta/script/create_conf.py ${TMP_DIR}/create_conf.py

    python -m tmp.create_conf ${TMP_DIR}/supervisord_template.conf supervisor-fta-fta.conf
}

function clear_tmp() {
    rm -rf ${TMP_DIR}
}

cd ${ROOT_PATH}
init_tmp
init_dir
init_settings
init_conf
clear_tmp

