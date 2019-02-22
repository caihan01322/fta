/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$(document).ready(function(){

    locateRightNav("li-alarm_def_list")

    $('.responsible-tips').tooltip({
        'content': gettext('提示:第一个负责人会被用作套餐执行人'),
        'position': {my: "left top"}
    })
    $('th[data-toggle=tooltip]').tooltip()
    $.bootstrapSortable(false, 'reversed')

    $('#update-resp').click(function(){
        
        if(!is_resp){
            new bkDialog({
                    type: 'dialog',
                    title: gettext("提示信息"),
                    icon: 'warning',
                    lock: true,
                    content: gettext("您不属于该业务负责人，请联系负责人修改，谢谢！"),
                    confirmFn: function(){},
                    okVal: gettext("确定")
            }).show();
            return;
        }

        $.ajax({
            url: site_url + tip_id + '/api/v1/bizconf/' + biz_resp_id +'?format=json',
            data: $.toJSON({
                'cc_biz_id': tip_id,
                'responsible': $('#responsible').val(),
            }),
            type: biz_type,
            dataType: 'json',
            contentType: 'application/json',
            success: function(result){
                include_open(tip_id + '/alarm_def_list/');//需要刷新请求的put/post方法
                show_msg(gettext("告警负责人修改成功"), 2);
            },
            error: function(result){
                new bkDialog({
                    type: 'dialog',
                    title: gettext("修改失败"),
                    icon: 'error',
                    lock: true,
                    content: gettext("告警负责人修改失败, 请联系开发或管理员！"),
                    confirmFn: function(){},
                    okVal: gettext("确定")
                }).show();
            }
        })
    })
});
$("#type-" + get_add_id).parent('.close-text').addClass('active');
$("#type-" + get_editor_id).parent('.close-text').addClass('active');

getAvctiveVisible();

function show_edit_msg(source_type){
    show_msg(gettext('请先到[管理告警源]中启用:')+ source_type, 4);
}
// 判断当前选中自愈是否在可见范围
function getAvctiveVisible(){
  if($(".alarm-list-table tbody tr.active").length>0){
    var activeHeight = $(".alarm-list-table tbody tr.active").offset().top,
        winHeight = $(window).innerHeight();
    if(activeHeight>=winHeight){
      $('html,body').animate({'scrollTop': activeHeight-winHeight+90+'px'},500);
    }
  }

}

$(".my_edit_button").click(function(){   //清空全局套餐名称
    comtom_name = "";
})
$(".block_alarm_def").on('click', function(){
    var is_available = $(this).attr('is_available');
    var is_disabled = $(this).attr('is_disabled');
    var source_type = $(this).prev('.alarm_def_source_type').text();
    var fun_id = $(this).attr('fun_id');
    if(is_disabled=='1' && is_available=='0'){
        show_msg(gettext('请先到[管理告警源]中启用:')+source_type, 4);
        return false;
    }
    $.ajax({
        url: site_url + tip_id + '/block_alarm_def/',
        data: {"id": fun_id},
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (!result.success) {
                alert_msg(result.message, 4);
            } else {
                include_open(tip_id + '/alarm_def_list/');
            }
        }
    })
})

function del_def(id) {
    var delDialog = new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext('您确定删除吗？'),
        confirmFn: function(){
               $.ajax({
                    url: site_url + tip_id + '/del_def/alarm/',
                    data: {'id': id},
                    type: 'POST',
                    dataType: 'json',
                    success: function(result){
                        if (!result.result) {
                            show_msg(result.message, 4);
                        }
                        include_open(tip_id + '/alarm_def_list/');
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
$(".table-packup table").on("click", ".text-switch",function(){
    
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