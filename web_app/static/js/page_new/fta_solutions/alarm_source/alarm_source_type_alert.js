/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
// 表格收起交互 公共部分说
$(".table-packup table").on("click", ".text-switch", function () {

    $(this).closest("tr").children("td").children(".limitText").toggleClass("hd")
    $(this).closest("tr").toggleClass("open-text close-text");
})

$(".table-packup tr").hover(function () {

    var _this = $(this);
    var curFlag = false;
    $(this).find(".limitText").each(function () {

        if ($.trim($(this).find("span").text()).length > 0) {
            curFlag = true;
        }
    });
    if (curFlag) {
        $(this).addClass("overLine");
    } else {
        $(this).removeClass("overLine");
    }
}, function () {
    $(this).removeClass("overLine");
});

// 获取告警类型列表
function get_alarm_type_list() {
    $.ajax({
        url: site_url + tip_id + "/alarm_type/alert/list/",
        type: "GET",
        dataType: 'html',
        success: function (data) {
            $("#alert_alarm_list").html(data);
        }
    })  
}

// 刷新告警类型
$("#refresh_alarm_type").click(function(){
    new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext("确认要刷新蓝鲸监控的告警类型") + '?',
        confirmFn: function () {
            $("#alert_alarm_list").html('<div style = "padding: 10% 40%;" class="pure-title"><i class="bk-icon icon-refresh" style="font-size:40px;color:silver"></i></div>')
            $.ajax({
                url: site_url + tip_id + "/alarm_type/alert/refresh/",
                type: "POST",
                dataType: 'json',
                success: function (result) {
                    if (result.result) {
                        show_msg(gettext("刷新成功"), 2);
                        get_alarm_type_list();
                    } else {
                        show_msg(result.message, 4);
                    }
                }
            })
        },
        okVal: gettext("确定"),
        cancelFn: function () { },
        cancelVal: gettext("取消")
    }).show();
})