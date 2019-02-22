/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$("#clone_alarm_type").change(function(){
    var to_alarm_type = $("#clone_alarm_type").val();
    if (! to_alarm_type) {
        return
    }
    $.ajax({
        url: site_url + tip_id + '/alarm_def_copy/',
        data: {
            'alarm_type': to_alarm_type,
            'source_type': $("#clone_alarm_type").find("option:selected")[0].title,
            'alarm_def_id': $("#fta_alarm_def_id").val()
        },
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (result.success){
                new bkDialog({
                    type: 'dialog',
                    title: gettext("确认信息"),
                    icon: 'warning',
                    lock: true,
                    content: gettext('拷贝成功，现在即将转到拷贝好的新策略'),
                    confirmFn: function(){
                        location.href = site_url + tip_id + "/?include="+ tip_id + "/alarm_def/"+ result.new_id + '/'
                    },
                    okVal: gettext("确定"),
                    cancelFn: function(){},
                    cancelVal: gettext("取消")
                }).show();

            }
        }
    })
})
function open_cur_solution(){
    var cur_solution = $("#solution").val();
    var app_id = $("#solution").find("option:selected").attr('app_id');
    if(cur_solution == ""){
        show_msg(gettext("不处理的套餐，就是一切皆空"), 2);
    }else if(app_id == '0'){
        show_msg(gettext("快捷套餐就是系统定义的套餐"), 2);
    }else{
        defaultSolution = cur_solution
        include_open(tip_id + '/solution/' + cur_solution+'/');
    }
}

function validate_data(post_data){
    if(!validate_alarm_def(post_data)){
        show_msg(gettext("策略配置填写有误，无法提交，请重新填写"), 4);
        $('html,body').animate({'scrollTop': '0px'},500);
        return false;
    }
    if($("#solution").val()==""){
        show_msg(gettext("请选择处理告警的自愈套餐"), 4);
        $(".solution-error-tip").addClass("db").removeClass("dn");
        $("#solution_tip .select2-container").addClass('select2-container-active');
        $('html,body').animate({'scrollTop': $("#solution_div").offset().top},500);
        return false;
    }
    if(parseInt($("#timeout").val())<5 || $("#timeout").val()==""){
        show_msg(gettext("超时时间请填写大于5的整数"), 4);
        $("#timeout").focus();
        return false;
    }
    if($("#description").val()==""){
        show_msg(gettext("自愈方案名称不能为空"), 4);
        $("#description").focus();
        return false;
    }

    if($("#description").val().length>80){
        show_msg(gettext("自愈方案名称最长不超过80字符"), 4);
        $("#description").focus();
        return false
    }
    return true;
}

function add_alarm_def() {

    if($(".save_alarm").hasClass("disabled-btn")) return;

    var alarmType = $("#alarm_type").val();
    var responsible = $("#responsible").val();
    if(responsible){
        var responsible_str = responsible.join(';');
    }else{
        var responsible_str = '';
    }

    // 获取已选topo
    var formTopoList = [];
    var formTopoNameList = [];
    $("#topo_set_list a").each(function(){
        formTopoList.push($(this).attr("data-id"));
        formTopoNameList.push($(this).text());
    })
    // 获取已选module
    var formModuleList = [];
    var formModuleNameList = [];
    $("#module_set_list a").each(function(){
        formModuleList.push($(this).attr("data-id"));
        formModuleNameList.push($(this).text());
    })
    var post_data = {
        'cc_biz_id': tip_id,
        'alarm_type': $("#alarm_type").val(),
        'module_names': formModuleNameList.join(','),
        'set_names': formTopoNameList.join(','),

        'source_type': $("#alarm_type").find("option:selected")[0].title,
        'is_enabled': $("#is_enabled").is(':checked'),
        'solution': $("#solution").val(),
        'tnm_attr_id': $("#tnm_attr_id").val() || "",
        'process': $("#process").val() || "",
        'reg': $("#reg").val() || "",
        'timeout': $("#timeout").val(),
        'description': $("#description").val() || "",
        'responsible': responsible_str,
        'alarm_attr_id': $("#alarm_attr_id").val(),
        'module': formModuleList ? formModuleList.toString():"",
        'topo_set': formTopoList? formTopoList.toString():"",
        'set_attr': $("#set_attr").val()? $("#set_attr").val().toString():"",
        'notify': JSON.stringify({
            "begin_notify_wechat": $("#begin_notify_wechat").is(':checked'),
            "begin_notify_mail": $("#begin_notify_mail").is(':checked'),
            "begin_notify_sms": $("#begin_notify_sms").is(':checked'),
            "begin_notify_im": $("#begin_notify_im").is(':checked'),
            "begin_notify_phone": $("#begin_notify_phone").is(':checked'),
            "success_notify_wechat": $("#success_notify_wechat").is(':checked'),
            "success_notify_mail": $("#success_notify_mail").is(':checked'),
            "success_notify_sms": $("#success_notify_sms").is(':checked'),
            "success_notify_im": $("#success_notify_im").is(':checked'),
            "success_notify_phone": $("#success_notify_phone").is(':checked'),
            "failure_notify_wechat": $("#failure_notify_wechat").is(':checked'),
            "failure_notify_mail": $("#failure_notify_mail").is(':checked'),
            "failure_notify_sms": $("#failure_notify_sms").is(':checked'),
            "failure_notify_im": $("#failure_notify_im").is(':checked'),
            "failure_notify_phone": $("#failure_notify_phone").is(':checked'),
            "to_extra": $("#to_extra").is(':checked'),
            "to_role": $("#to_role").is(':checked'),
        })
    }

    // 校验必填的数据
    var flag = validate_data(post_data);
    if(!flag){
        return false;
    }

    $(".save_alarm").addClass("disabled-btn");
    $(".new_loading").show();

    $.ajax({
        url: site_url + tip_id + '/add_alarm_def/',
        data: post_data,
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (! result.result) {
                //alert(result.message);
                show_msg(result.message, 4);
                $(".new_loading").fadeOut();
                $(".save_alarm").removeClass("disabled-btn");
                $('html,body').animate({'scrollTop': '0px'},500)
            }else{
                get_add_id = result.def_id;
                $(".save_alarm").removeClass("disabled-btn");
                include_open(tip_id + '/alarm_def_list/','',1)
                //
                var url = tip_id + '/alarm_def/' + result.def_id + '/'
                  show_msg(gettext("恭喜你 成功接入自愈！"), 2);
            }
        }
    });
}

function edit_alarm_def() {

    if($(".save_alarm").hasClass("disabled-btn")) return;

    // 获取已选topo
    var formTopoList = [];
    var formTopoNameList = [];
    $("#topo_set_list a").each(function(){
        formTopoList.push($(this).attr("data-id"));
        formTopoNameList.push($(this).text());
    })
    // 获取已选module
    var formModuleList = [];
    var formModuleNameList = [];
    $("#module_set_list a").each(function(){
        formModuleList.push($(this).attr("data-id"));
        formModuleNameList.push($(this).text());
    })

    var responsible = $("#responsible").val();
    if(responsible){
        var responsible_str = responsible.join(';')
    }else{
        var responsible_str = ''
    }
    var module_name_list = [];
    $("#module").find("option:selected").each(function(){
        module_name_list.push($(this).text());
    })
    var set_name_list = [];
    $("#topo_set").find("option:selected").each(function(){
        set_name_list.push($(this).text());
    })
    var post_data = {
            'func_id': $("#fta_alarm_def_id").val(),
            'cc_biz_id': tip_id,
            'alarm_type': $("#alarm_type").val(),
            'module_names': formModuleNameList.join(','),
            'set_names': formTopoNameList.join(','),
            'source_type': $("#alarm_type").find("option:selected")[0].title,
            'is_enabled': $("#is_enabled").is(':checked'),
            'timeout': $("#timeout").val(),
            'solution': $("#solution").val(),
            'tnm_attr_id': $("#tnm_attr_id").val() || "",
            'alarm_attr_id': $("#alarm_attr_id").val(),
            'process': $("#process").val() || "",
            'reg': $("#reg").val() || "",
            'description': $("#description").val(),
            'responsible': $("#to_extra").is(':checked') ? responsible_str : '',
            'module': formModuleList ? formModuleList.toString():"",
            'topo_set': formTopoList? formTopoList.toString():"",
            'set_attr': $("#set_attr").val()? $("#set_attr").val().toString():"",
            'notify': JSON.stringify({
                "begin_notify_wechat": $("#begin_notify_wechat").is(':checked'),
                "begin_notify_mail": $("#begin_notify_mail").is(':checked'),
                "begin_notify_sms": $("#begin_notify_sms").is(':checked'),
                "begin_notify_im": $("#begin_notify_im").is(':checked'),
                "begin_notify_phone": $("#begin_notify_phone").is(':checked'),
                "success_notify_wechat": $("#success_notify_wechat").is(':checked'),
                "success_notify_mail": $("#success_notify_mail").is(':checked'),
                "success_notify_sms": $("#success_notify_sms").is(':checked'),
                "success_notify_im": $("#success_notify_im").is(':checked'),
                "success_notify_phone": $("#success_notify_phone").is(':checked'),
                "failure_notify_wechat": $("#failure_notify_wechat").is(':checked'),
                "failure_notify_mail": $("#failure_notify_mail").is(':checked'),
                "failure_notify_sms": $("#failure_notify_sms").is(':checked'),
                "failure_notify_im": $("#failure_notify_im").is(':checked'),
                "failure_notify_phone": $("#failure_notify_phone").is(':checked'),
                "to_extra": $("#to_extra").is(':checked'),
                "to_role": $("#to_role").is(':checked'),
            })
        }

    // 校验必填的数据
    var flag = validate_data(post_data);
    if(!flag){
        return false;
    }

    $(".save_alarm").addClass("disabled-btn");
    $(".new_loading").show();

    $.ajax({
        url: site_url + tip_id + '/edit_alarm_def/',
        data: post_data,
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (! result.result) {
                show_msg(gettext('告警修改失败：') + result.message, 4);
              $(".save_alarm").removeClass("disabled-btn");
              $(".new_loading").fadeOut();
            }
            else{
                include_open(tip_id + '/alarm_def_list/','',1)
                get_editor_id = $("#fta_alarm_def_id").val();
                show_msg(gettext("恭喜你， 自愈定义修改成功"), 2);
            }
        }
    })
}
