/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    $("#responsible").select2({
          placeholder: gettext("请选择额外通知人"),
          allowClear: true
    });
    $(function(){
        $("#advice_def").trigger('change');
        // $(".error-tip").hide();
        $("#alarm_type_tip .select2-container").addClass('select2-container-active')
        $("#timeout").blur(function(){
            var timeout = $("#timeout").val();
            if(timeout == ""){
               $(".time-error-tip").addClass("db").removeClass("dn");
            }else{
                $(".time-error-tip").removeClass("db").addClass("dn");
            }
        });
        $("#advice").blur(function(){
            var advice = $("#advice").val();
            if(advice == ""){
               $(".advice-error-tip").addClass("db").removeClass("dn");
            }else{
                $(".advice-error-tip").removeClass("db").addClass("dn");
            }
        });
    })
    function show_advice_def(obj){
        var advice_def_id = $(obj).val();
        if(advice_def_id){
            var url = site_url + tip_id + "/advice_fta_def/advice_def/"+advice_def_id+"/";
            $.get(url, function(data){
                $("#advice_def_detail").html(data);
            })
        }else{
            $("#advice_def_detail").html('');
        }
    }
    function open_cur_solution(){
        var cur_solution = $("#solution").val();
        var app_id = $("#solution").find("option:selected").attr('app_id');
        if(cur_solution == ""){
            show_msg(gettext("不处理的套餐，就是一切皆空"), 2);
        }else if(app_id == '0'){
            show_msg(gettext("快捷套餐就是系统定义的套餐"), 2);
        }else{
            include_open(tip_id + '/solution/' + cur_solution + '/');
        }
    }
    function validate_data(){
        if(!$("#alarm_type").val()){
            show_msg(gettext("请选择告警类型"), 4);
            $('html,body').animate({'scrollTop': '0px'},500);
            return false;
        }
        if(parseInt($("#interval").val())<1 || $("#interval").val()==""){
            show_msg(gettext("考察时长填写不合法，请重新填写"), 4);
            $("#interval").focus();
            return false;
        }
        if(parseInt($("#threshold").val())<1 || $("#threshold").val()==""){
            show_msg(gettext("考察阈值填写不合法，请重新填写"), 4);
            $("#threshold").focus();
            return false;
        }
        if($("input[name='handle_type']:checked").attr('data')=='solution' && !$("#solution").val()){
            show_msg(gettext("请选择预警套餐"), 4);
            $(".solution-error-tip").addClass("db").removeClass("dn");
            $("#solution_tip .select2-container").addClass('select2-container-active');
            $('html,body').animate({'scrollTop': $("#solution_div").offset().top},500);
            return false;
        }
        if($("input[name='handle_type']:checked").attr('data')=='advice' && !$("#advice").val()){
            show_msg(gettext("建议不能为空"), 4);
            $("#advice").focus();
            return false;
        }
        if(parseInt($("#timeout").val())<1 || $("#timeout").val()==""){
            show_msg(gettext("超时填写不合法，请重新填写"), 4);
            $("#timeout").focus();
            return false;
        }
        return true;
    }
    function add_advice_fta_def() {
        if($(".save_fta_def").hasClass("disabled-btn")) return;

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
        // 校验必填的数据
        var flag = validate_data();
        if(!flag){
            return false;
        }
        var post_data = {
            'cc_biz_id': tip_id,
            // 'advice_def_id': $("#advice_def").val(),
            'alarm_type': $("#alarm_type").val(),
            'interval': $("#interval").val(),
            'threshold': $("#threshold").val(),
            'advice': $("#advice").val(),
            'handle_type': $("input[name='handle_type']:checked").attr('data'),

            'module_names': formModuleNameList.join(','),
            'set_names': formTopoNameList.join(','),
            'is_enabled': $("#is_enabled").is(':checked'),
            'solution': $("#solution").val(),
            'timeout': $("#timeout").val(),
            'description': $("#description").val() || "",
            'responsible': responsible_str,
            'module': formModuleList ? formModuleList.toString():"",
            'topo_set': formTopoList? formTopoList.toString():"",
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
        $(".save_fta_def").addClass("disabled-btn");
        $(".new_loading").fadeIn();
        $.ajax({
            url: site_url + tip_id + '/advice_fta_def/save/0/',
            data: post_data,
            type: 'POST',
            dataType: 'json',
            success: function(result){
                if (! result.result) {
                    //alert(result.message);
                    show_msg(result.message, 4);
                    $(".new_loading").fadeOut();
                    $(".save_fta_def").removeClass("disabled-btn");
                }else{
                    show_msg(gettext("恭喜你 成功接入预警！"), 2);
                    include_open(tip_id + '/advice_fta_def_list/');
                }
            }
        })
    }

    function edit_advice_fta_def() {
      if($(".save_fta_def").hasClass("disabled-btn")) return;

        var responsible = $("#responsible").val();
        if(responsible){
            var responsible_str = responsible.join(';')
        }else{
            var responsible_str = ''
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

        // 校验必填的数据
        var flag = validate_data();
        if(!flag){
            return false;
        }
        var post_data = {
                'cc_biz_id': tip_id,
                // 'advice_def_id': $("#advice_def").val(),
                'alarm_type': $("#alarm_type").val(),
                'interval': $("#interval").val(),
                'threshold': $("#threshold").val(),
                'advice': $("#advice").val(),
                'handle_type': $("input[name='handle_type']:checked").attr('data'),

                'module_names': formModuleNameList.join(','),
                'set_names': formTopoNameList.join(','),
                'is_enabled': $("#is_enabled").is(':checked'),
                'timeout': $("#timeout").val(),
                'solution': $("#solution").val(),
                'description': $("#description").val(),
                'responsible': responsible_str,
                'module': $("#module").val()? $("#module").val().toString():"",
                'topo_set': $("#topo_set").val()? $("#topo_set").val().toString():"",
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
        var advice_fta_def_id = $("#advice_fta_def_id").val();
        $(".save_fta_def").addClass("disabled-btn");
        $(".new_loading").fadeIn();
        $.ajax({
            url: site_url + tip_id + '/advice_fta_def/save/' + advice_fta_def_id +'/',
            data: post_data,
            type: 'POST',
            dataType: 'json',
            success: function(result){
                if (! result.result) {
                    show_msg(gettext('告警修改失败：') + result.message, 4);
                    $(".save_fta_def").removeClass("disabled-btn");
                    $(".new_loading").fadeOut();
                }
                else{
                    include_open(tip_id + '/advice_fta_def_list/');
                    show_msg(gettext("恭喜你， 预警定义修改成功"), 2);
                }
            }
        })
    }