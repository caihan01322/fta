/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
locateRightNav("li-alarm_source_list")
function show_exception_data(obj){
    var tr_obj = $(obj).parents('tr').next('.exception_data');
        // 显示、隐藏组件内容    
        var is_hiden = $(tr_obj).is(":hidden");
        if(is_hiden){
            $(tr_obj).css('display', '');
        }else{
            $(tr_obj).css('display', 'none');
        }
        
}
function del_def(id) {
    var delDialog = new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext('您确定删除吗？<br><br> 禁用后已接入的自愈处理会同时被禁用'),
        confirmFn: function(){
            $.ajax({
                url: site_url + tip_id + '/alarm_source/del/',
                data: {'id': id},
                type: 'POST',
                dataType: 'json',
                success: function(result){
                    if (!result.result) {
                        show_msg(result.message,4);
                    }
                    include_open(tip_id + '/alarm_source/list/');
                }
            });
        },
        okVal: gettext("确定"),
        cancelFn: function(){},
        cancelVal: gettext("取消")
    });
    delDialog.show();
}

 // 表格收起交互 公共部分说
$(".table-packup table").on("click",".text-switch",function(){
    
    $(this).closest("tr").children("td").children(".limitText").toggleClass("hd")
    $(this).closest("tr").toggleClass("open-text close-text");
})

$(".table-packup tr").hover(function(){
    
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

$(".errorTip").tooltip()

$(".admin_manage_alram_source").on('click', function () {
    var msg = $("#admin_manage_alram_source_text_id").text()
    show_msg(msg, 4);
})