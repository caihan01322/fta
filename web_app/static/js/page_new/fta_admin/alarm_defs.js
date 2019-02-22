/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$("#type-" + get_add_id).parent('.close-text').addClass('active');
$("#type-" + get_editor_id).parent('.close-text').addClass('active');

getAvctiveVisible();

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
function del_def(id) {
    var delDialog = new bkDialog({
        type: 'dialog',
        title: gettext(gettext("确认信息")),
        icon: 'warning',
        lock: true,
        content: gettext(gettext('您确定删除吗？')),
        confirmFn: function(){
               $.ajax({
                    url: site_url + 'fta_admin/alarm_def/'+id+'/',
                    type: 'DELETE',
                    dataType: 'json',
                    success: function(result){
                        if (!result.result) {
                            show_msg(result.message, 4);
                        }
                        include_open('fta_admin/alarm_defs/');
                    }
                });
            },
            okVal: gettext(gettext("确定")),
            cancelFn: function(){},
        cancelVal: gettext(gettext("取消"))
    });
    delDialog.show();
}


 // 表格收起交互 公共部分说
$(".table-packup table").on("click", ".text-switch",function(){
    // debugger
    $(this).closest("tr").children("td").children(".limitText").toggleClass("hd")
    $(this).closest("tr").toggleClass("open-text close-text");
})

$(".table-packup tr").hover(function(){

    var _this = $(this);
    var curFlag = false;
    $(this).find(".limitText").each(function(){
        // debugger
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
