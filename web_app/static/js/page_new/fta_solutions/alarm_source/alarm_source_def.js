/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
// 文本复制
var clipboard = new Clipboard('.mycopy');

clipboard.on('success', function(e) {
    show_msg(gettext('复制成功！'),2);
});

clipboard.on('error', function(e) {
    show_msg(gettext('复制失败！'),4);
});
function generate_config(obj,is_edit){

    // 判断应用名称是否已填，app_name 在 alarm_source_head.part 页面中
    var app_name = $("#app_name").val();
    var source_id = $("#alarm_source_def_source_id").val();
    if(is_edit){
        var source_id = $("#source_id").val();
        var url = site_url + tip_id + "/alarm_source/config/"+source_id+"/";
    }else{
        var url = site_url + tip_id + "/alarm_source/config/"+source_id+"/";
    }
    var source_type = $("#alarm_source_def_source_type").val();
    var page_type = $("#alarm_source_def_page_type").val();
    $.post(url, {
        'app_name': app_name,
        'source_type': source_type,
        'page_type': page_type
    },function(data){
        if(data.result){
            $(obj).hide();
            $("#alarm_source_config").html(data.message);
            initMask({
                el: '#newStyles',
                closed: function(element){
                    var oStyleData = {
                        title: gettext('新建告警类型'),
                        description: '',
                        pattern: '',
                        match_mode: 0
                    }
                    initMaskData(oStyleData)
                }
            });
        }else{
            show_msg(data.message, 4);
        }
    }, 'json')

    $(".edit_config").show().prev().hide();

    $("#app_name").attr("readonly","readonly");

}

function addAlarmType(){
    //告警名称
    var alarm_name = $(".alarm_name_new").val();
    //告警规则
    var alarm_rules = $(".alarm_rules_new").val();
    //匹配模式
    var alarm_pattern = $(".alarm_pattern_new input[checked]").attr("thisval");
    var curTrID = $(".new_slide .bk-mask-title input").val();
    var matchModeList = [gettext('字符串'),gettext('正则表达式'),gettext('通配符')];

    if(alarm_name==""||alarm_rules==""){
        showWarning(0,gettext("请填写完整名称和规则！"))
        return ;
    }

    if($(".new_slide .bk-mask-title span").text()==gettext("编辑告警类型")){
        // 修改告警类型
        $.ajax({
            url: site_url + tip_id + "/api/v1/alarmtype/"+curTrID,
            type: "PUT",
            contentType: 'application/json',
            data: JSON.stringify({
                pattern: alarm_rules,
                description: alarm_name,
                match_mode: alarm_pattern,
                source_type: $("input[name=source_type]").val(),
            }),
            success: function (result) {
                var changeObj = eval($("#alarm_type_"+curTrID+" span"))
                changeObj.eq(0).text(result.description);
                changeObj.eq(1).text(result.pattern);
                changeObj.eq(2).text(matchModeList[result.match_mode]);
                $(".new_slide #close").click();

            },
        })

    }else{
        // 新增告警类型
        var oStyleData = {
            title: gettext('新建告警类型'),
            description: '',
            pattern: '',
            match_mode: matchModeList[0]
        }
        initMaskData(oStyleData)
        $.ajax({
            url: site_url + tip_id + "/api/v1/alarmtype/",
            type: "POST",
            contentType: 'application/json',
            data: JSON.stringify({
                cc_biz_id: tip_id,
                is_enabled: true,
                is_hidden: false,
                source_type: $("input[name=source_type]").val(),
                alarm_type: "",
                pattern: alarm_rules,
                description: alarm_name,
                match_mode: alarm_pattern
            }),
            success: function (result) {

                var strTrTmpl = '<tr class="close-text" id="alarm_type_'+result.id+'">'+
                    '<td class="pl35">'+
                        '<span>'+result.description+'</span>'+
                    '</td>'+
                    '<td class="pl20">'+
                        '<span class="report-num">'+result.pattern+'</span>'+
                    '</td>'+
                    '<td class="pl20">'+
                       ' <span class="report-num">'+matchModeList[result.match_mode]+'</span>'+
                    '</td>'+
                    '<td class="pl20 inline-btn-panel">'+
                        '<a class="f_r border-box edit_button" href="javascript:edit_alarm_type('+result.id+');"></a>'+
                        '<a class="f_r border-box del_button" href="javascript:del_alarm_type('+result.id+');"></a>'+
                    '</td>'+
                '</tr>';
                $(".new_slide #close").click();
                $(".alarm_type_table tbody").append(strTrTmpl);
            },
        })

    }
}

function initMaskData(oStyleData){
    $(".new_slide .bk-mask-title span").html(oStyleData.title);
    $(".alarm_name_new").val(oStyleData.description);
    $(".alarm_rules_new").val(oStyleData.pattern);
    $("#match_mode"+oStyleData.match_mode).attr("checked","checked").siblings().removeAttr("checked");
}