/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

locateRightNav("li-solution_list")

var maxHeight = $(window).innerHeight() -318;
$(".current-explain").css({
    "max-height":maxHeight+"px",
    "overflow": "auto"
});
$(document).ready(function() {
    $("#solution-details").fadeIn();
    $('#solution_type').select2({
        formatSelection:function(item){return "<div class='solution-type-style'>" + item.text+"</div>"},
    })
    $("#copy_cc_biz_id").select2();
});

function calcurnum(){

    var curStr = $("#title").val();
    var curLen = getLength(curStr);

    var curValLen = curStr.length;
    var nflag = 0;
    var numNote;
    for(var i=0;i<curValLen;i++){

        nflag += getLength(curStr.charAt(i))
        if(nflag == 30){
            numNote = i;
            break ;
        }
        if(nflag > 30){
            numNote = i-1
            break ;
        }
    }
    $("#title").val($("#title").val().substr(0,numNote));

}

//计算字符长度
function getLength(str) {

    var len = str.length;
    var reLen = 0;
    for (var i = 0; i < len; i++) {
        if (str.charCodeAt(i) < 27 || str.charCodeAt(i) > 126) {
            // 全角
            reLen += 2;
        } else {
            reLen++;
        }
    }
    return reLen;
}

function refresh_solution_form(){

        var link_id = $(".saveBtnPanel button").attr('id');
        var curVal = $('#solution_type').val();
        $("#solution-details").fadeOut();
        if(link_id){
            include_open(tip_id + '/solution/' + s_solution_id+ '/?type_to_show=' + curVal);
        }else{
            include_open(tip_id + '/solution/' + s_solution_id+ '/?js_item=1&type_to_show=' + curVal);
        }

}

function get_solution_config(){
    var config = {}
    $('input,select,textarea', '#solution_form').not('.not_submit').each(function(item,index){
            var curVal = '' ;
            if($(this).attr('name')){

                if($(this).attr('rel') == "checkbox"){
                    if(!$(this).attr('checked')){
                        if($(this).attr('name') == 'replace_execute_ip')
                        {
                            curVal = "off"
                        }
                        else{
                            return ;
                        }
                    }else{
                        curVal = "on"
                    }
                }else{
                    if($(this).attr('type') == "radio" && !$(this).is(':checked')){
                        return; //如果radio没有选中则直接忽略
                    }
                    if($(this).attr('type') == "checkbox" && !$(this).is(':checked')){
                        return; //如果checkbox没有选中则直接忽略
                    }
                    curVal = $(this).val();
                }

                config[$(this).attr('name')] = curVal
            }

    })
    return config
}

$("#copy_cc_biz_id").change(function(){
    var to_cc_biz_id = $("#copy_cc_biz_id").val();
    if (! to_cc_biz_id) {
        return
    }
    $.ajax({
        url: site_url + tip_id + '/solution_copy/',
        data: {
            'cc_biz_id': to_cc_biz_id,
            'solution_id': s_solution_id
        },
        type: 'POST',
        dataType: 'json',
        success: function(result){
            var msg = gettext("是否跳转到目标业务");
            if(!result.success){
                msg = result.message+"<br\><br\>"+msg;
            }
            new bkDialog({
                    type: 'dialog',
                title: gettext("确认信息"),
                icon: 'warning',
                lock: true,
                content: msg,
                confirmFn: function(){
                    location.href = site_url+to_cc_biz_id+"/?include="+to_cc_biz_id+"/solution_list/";
                },
                okVal: gettext("确定"),
                cancelFn: function(){},
                cancelVal: gettext("取消")
            }).show();
        }
    })
})

//检查组合套餐里没有空套餐
function check_diy_solution(){
    var diy_config = $.evalJSON(get_solution_config().real_solutions)
    for(var i in diy_config){
        if(!diy_config[i]){
            return false;
        }
    }
    return true;
}

//检查新版组合套餐里没有空套餐
function check_graph_solution(){
    var graph_config = JSON.parse(get_solution_config().real_solutions)
    for(var i in graph_config){
        if(graph_config[i][1] == 0){
            return false;
        }
    }
    return true;
}

//验证按时间汇总套餐
function check_collect_solution(){
    var collect_config = get_solution_config()
    var keys = ["range_time", "range_count_floor", "range_count"]
    for(var i in keys){
        var k = keys[i]
        var v = parseInt(collect_config[k])
        if(isNaN(v) || v < 0 || v > 1000){
            return false;
        }
    }
    return true;
}

    // 验证套餐名称
    function check_solution_title () {
        var url  = site_url + tip_id + '/check_solution_title/'+ check_solution_id+ '/';
        var re_code = false;
        $.ajax({
            type: 'GET',
            url: url,
            data:  {'title': $("#title").val()},
            success: function(d){
                    if(d.result){
                        re_code = true
                    }else{
                        show_msg(d.message, 4);
                        re_code = false;
                        $('.save_solution').removeClass('disabled-btn').removeAttr('disabled');
                    }
            },
            dataType: 'json',
            async: false,
        });
        return re_code;
    }

function save_solution() {
    if ($(".save_solution").hasClass('disabled-btn')||!validate_inputs_and_alert("#solution_form")){
        return;
    }
    var data = {
        'title_name':$("#title").val(),
        'ling_id' : $(".saveBtnPanel button").attr('data-id'),
        'cc_biz_id': tip_id,
        'solution_type': $('#solution_type').select2('val'),
        'codename': $("#codename").val(),
        'title': $("#title").val(),
        'creator': save_solution_creator,
        'config': JSON.stringify(get_solution_config()),
        'sleep_txt':$("input[name = 'seconds']")
    }

    comtom_name = data.title_name;

    if(!data.title){
        show_msg(gettext('请输入套餐名'),4);
        return;
    } else if(data.title.length>30){
        show_msg(gettext('套餐名不能超过30个字符'),4);
        return;
    }

    switch (data.solution_type) {
        case 'diy':
            var diy_valid = check_diy_solution();
            if(!diy_valid){
                show_msg(gettext('组合套餐配置有误：有步骤没有指定原子套餐'),4);
                $('.save_solution').removeClass('disabled-btn')
                return;
            }
            break;
        case 'graph':
            var graph_valid = check_graph_solution();
            if(!graph_valid){
                show_msg(gettext('组合套餐配置有误：有步骤没有指定原子套餐'),4);
                $('.save_solution').removeClass('disabled-btn')
                return;
            }
            break;
        case 'collect':
            config = get_solution_config();
            config["dimension"] = ["cc_idc_unit", "cc_topo_set", "cc_app_module"];
            data.config = JSON.stringify(config);
            var collect_valid = check_collect_solution();
            if(!collect_valid){
                show_msg(gettext('汇总配置请填写数字，并且是0~1000以内'),4);
                $('.save_solution').removeClass('disabled-btn')
                return;
            }
            break;
        case 'clean':
            var curVal = $("input[name=clean_catalog]").val();
            validateCatelog(curVal);
            if(data.solution_type == 'clean' && !catalogFlag){
                show_msg(gettext('磁盘清理的目录不合法'),4);
                $('.save_solution').removeClass('disabled-btn')
                return;
            }
            break;
        case 'sleep':
            var reg =/^[0-9.]+$/ ;
            var inputVal = $("input[name=seconds]").val();
            if(!reg.test(inputVal)){
                show_msg(gettext('等待时间框里含有非数字符号'),4);
                $('.save_solution').removeClass('disabled-btn')
                return;
            }
            break;
        case 'http_callback':
            var http_url = $("input[name=url]").val()
            if( http_url == ''){
                show_msg(gettext('请输入回调地址！'),4);
                $('.save_solution').removeClass('disabled-btn')
                return;
            }
            break;
        default:

    }

    if($("#fileDate").select2("val")=="self"){
        var CustomData = $("input[name=clean_date_custom]").val();
        if( CustomData == ''|| CustomData == 0 ||CustomData < 0){
            show_msg(gettext('日期必须大于0'),4);
            return;
        }
    }

    $('.saveBtnPanel button').addClass('disabled-btn').attr('disabled','disabled');

    // 判断套餐名是否重复
    if (check_solution_title() == false){
        return false;
    }
    $.ajax({
        url: site_url + tip_id + '/api/v1/solution/'+ save_solution_id + '?format=json',
        data: JSON.stringify(data),
        type: s_type,
        dataType: 'json',
        contentType: 'application/json',
        beforeSend:function(){
            $(".new_loading").show();
        },
        success: function(result){
            comtom_name_id = result.id
            if(data.ling_id == 'link' && typeof(window.recover_by_solution != "undefined")){
                recover_by_solution(result);
            }else if(data.solution_type == 'graph'){
                include_open(tip_id + '/solution/'+result.id)
            }else{
                include_open(tip_id + '/solution_list/');//需要刷新请求的put/post方法
            }
            show_msg(gettext('自愈套餐保存成功'), 2);
            $('.saveBtnPanel button').removeAttr('disabled').removeClass('disabled-btn');

        },
        complete: function(){
            $(".new_loading").hide();
        }
    })
}
