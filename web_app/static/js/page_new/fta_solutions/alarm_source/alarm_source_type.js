/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$(".match-model").on("click", "input", function () {
    if ($(this).attr("checked")) {
        return;
    } else {
        $(this).attr("checked", "checked").siblings().removeAttr("checked");
    }
});

function del_alarm_type(id) {
    var confirmDialog = new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext('您确定删除吗？'),
        confirmFn: function () {
            $.ajax({
                url: site_url + tip_id + "/alarm_type/del/",
                type: "POST",
                data: {
                    id: id
                },
                dataType: 'json',
                success: function (result) {
                    if (result.result) {
                        show_msg(gettext("告警类型删除成功！"), 2)
                        $('.alarm_type_table tr[id="alarm_type_' + id + '"]').remove();
                    } else {
                        show_msg(result.message, 4)
                    }
                }
            })

        },
        okVal: gettext("确定"),
        cancelFn: function () { },
        cancelVal: gettext("取消")
    });
    confirmDialog.show();

}

function edit_alarm_type(id) {
    $("#newStyles").click();
    var matchModeList = [gettext('字符串'), gettext('正则表达式'), gettext('通配符')];
    var curTr = eval($("#alarm_type_" + id)).find("span");
    var oStyleData = {
        title: gettext('编辑告警类型<input type="hidden" value="') + id + '" />',
        description: curTr.eq(0).text(),
        pattern: curTr.eq(1).text(),
        match_mode: $.inArray(curTr.eq(2).text(), matchModeList)
    }
    initMaskData(oStyleData)
}

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