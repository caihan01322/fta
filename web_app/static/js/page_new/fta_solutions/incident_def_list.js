/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

locateRightNav("li-incident")
    
function block_inc(inc_id){
    $.ajax({
        url: site_url + tip_id + '/block_incident/',
        data: {"id": inc_id},
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (!result.success) {
                alert_msg(result.message, 4);
            } else {
                include_open(tip_id + '/incident/');
            }
        }
    })
}
function del_inc(inc_id){
    new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext("确定删除该收敛策略吗？"),
        confirmFn: function () {
            $.ajax({
                url: site_url + tip_id + '/del_incident/',
                data: {"id": inc_id},
                type: 'POST',
                dataType: 'json',
                success: function(result){
                    if (!result.success) {
                        alert_msg(result.message, 4);
                    } else {
                        include_open(tip_id + '/incident/');
                    }
                }
            })
        },
        okVal: gettext("确定"),
        cancelFn: function () {
        },
        cancelVal: gettext("取消")
    }).show();
}
$("#form_submit").click(function(){
    if($(this).hasClass("disabled-btn")) return;
    $(this).addClass("disabled-btn");
    $('input[name=timedelta]').val();
    $('input[name=count]').val();
    $.ajax({
        url: site_url + tip_id + '/add_incident/',
        data: $("#incident_form").serialize(),
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (!result.success) {
                showWarning("-1",result.message);
                $("#form_submit").removeClass("disabled-btn");
            } else {
                include_open(tip_id + '/incident/');
            }
        }
    })
    return false;
});
