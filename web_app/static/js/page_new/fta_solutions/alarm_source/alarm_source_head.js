/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
function block_def(id, source_type, source_type_name) {
    data = $("#source_switch").attr('data');
    if (data == '1') {
        var content = gettext('您确定禁用') + source_type_name + '？<br><br> ' + gettext('禁用后已接入的') + source_type_name + gettext('会同时被禁用');
        var enable = 0;
    } else {
        var content = gettext('您确定启用') + source_type_name + '？'
        var enable = 1;
    }
    new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: content,
        confirmFn: function () {
            var url = site_url + tip_id + '/alarm_source/switch/'
            $.ajax({
                url: url,
                data: {
                    'id': id,
                    'source_type': source_type,
                    'enable': enable
                },
                type: 'POST',
                dataType: 'json',
                success: function (result) {
                    if (!result.result) {
                        show_msg(result.message, 4);
                    } else {
                        // 变更开启状态
                        if (data == '1') {
                            $("#source_span").html('<i class="switchery switchery-middle" id="source_switch"data="0"> <middle></middle> </i>')
                        } else {
                            $("#source_span").html('<i class="switchery-on switchery-middle" id="source_switch" data="1"> <middle></middle> </i>')
                        }
                    }
                }
            });
        },
        okVal: gettext("确定"),
        cancelFn: function () { },
        cancelVal: gettext("取消")
    }).show();
}