/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
function del_def(id) {
    new bkDialog({

        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext('您确定删除吗？'),
        confirmFn: function(){
            $.ajax({
                url: site_url + tip_id + '/advice_fta_def/del/',
                data: {'id': id},
                type: 'POST',
                dataType: 'json',
                success: function(result){
                    if (!result.result) {
                        show_msg(result.message,4);
                    }
                    include_open(tip_id + '/advice_fta_def_list/');
                }
            });
        },
        okVal: gettext("确定"),
        cancelFn: function(){},
        cancelVal: gettext("取消")
    }).show();
}
function block_advice_fta_def(id){
    $.ajax({
        url: site_url + tip_id + '/advice_fta_def/block/',
        data: {"id": id},
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (!result.success) {
                alert_msg(result.message, 4);
            } else {
                include_open(tip_id + '/advice_fta_def_list/');
            }
        }
    })
}

 // 表格收起交互 公共部分说
$(".table-packup table").on("click",".text-switch",function(){
    // debugger
    $(this).closest("tr").children("td").children(".limitText").toggleClass("hd")
    $(this).closest("tr").toggleClass("open-text close-text");
})

$(".table-packup tr").hover(function(){
    // debugger
    var _this = $(this);
    var curFlag = false;
    $(this).find(".limitText").each(function(){
        var limitTextWidth = $(this).parent("td").children(".limitText").width();
        var hiddenTextWidth = $(this).parent("td").children(".hiddenText").width();
        if(hiddenTextWidth>limitTextWidth){
            curFlag = true;
        }
    });
    if(curFlag){
        $(this).addClass("overLine");
    }else{
        $(this).removeClass("overLine");
    }
}, function(){
    $(this).removeClass("overLine");
});