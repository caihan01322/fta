/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    function initSolution(){
      var defaultVal = $("#solution option").eq(0).attr("value");
      // $("#solution").select2("val",defaultVal);
    }
    initSolution();
    $(function(){
        $("#alarm_type_tip .select2-container").addClass('select2-container-active');
        $("#solution_tip .select2-container").addClass('select2-container-active');
        $('body').click(function(){
            var alarm_typ = $("#alarm_type").val();
            if(alarm_typ == ""){
                $(".error-tip").addClass("db").removeClass("dn")
                $("#alarm_type_tip .select2-container").addClass('select2-container-active')
            }else{
                $(".error-tip").removeClass("db").addClass("dn")
            }
        });
        $("#timeout").blur(function(){
            var timeout = $("#timeout").val();
            if(timeout == ""){
               $(".time-error-tip").addClass("db").removeClass("dn")
            }else{
                $(".time-error-tip").removeClass("db").addClass("dn")
            }
        });
    })

    $("#solution option").each(function() {
        // var _this = $(this)
        if($(this).text().trim() == comtom_name) {
                $(this).attr('selected', true);
            }
    });
    function validate_alarm_def(data){
        if(data.alarm_type == "customized"){
            var v = parseInt(data.tnm_attr_id)
            if(isNaN(v)){
                return false;
            }
        }
        return true;
    }

    function validate_data(post_data){
        if(!validate_alarm_def(post_data)){
            show_msg(gettext(gettext("策略配置填写有误，无法提交，请重新填写")), 4);
            $('html,body').animate({'scrollTop': '0px'},500);
            return false;
        }
        if($("#solution").val()==""){
            show_msg(gettext(gettext("请选择处理告警的自愈套餐")), 4);
            $(".solution-error-tip").addClass("db").removeClass("dn");
            $("#solution_tip .select2-container").addClass('select2-container-active');
            $('html,body').animate({'scrollTop': $("#solution_div").offset().top},500);
            return false;
        }
        if(parseInt($("#timeout").val())<1 || $("#timeout").val()==""){
            show_msg(gettext(gettext("超时填写不合法，请重新填写")), 4);
            $("#timeout").focus();
            return false;
        }
        if($("#description").val()==""){
            show_msg(gettext(gettext("自愈方案名称不能为空")), 4);
            $("#description").focus();
            return false;
        }

        if($("#description").val().length>80){
            show_msg(gettext(gettext("自愈方案名称最长不超过80字符")), 4);
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
        var post_data = {
            'alarm_type': $("#alarm_type").val(),
            'source_type': $("#alarm_type").find("option:selected")[0].title,
            'solution_id': $("#solution").val(),
            'reg': $("#reg").val() || "",
            'timeout': $("#timeout").val(),
            'description': $("#description").val() || "",
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
        var alarm_def_id = $("input[name=fta_admin_alram_def_id]").val();
        $.post(
            site_url + 'fta_admin/alarm_def/'+alarm_def_id+'/',
            JSON.stringify(post_data),
            function(result){
                if (!result.result) {
                    show_msg(result.message, 4);
                    $(".new_loading").fadeOut();
                    $(".save_alarm").removeClass("disabled-btn");
                    $('html,body').animate({'scrollTop': '0px'},500)
                }else{
                    $(".save_alarm").removeClass("disabled-btn");
                    include_open('fta_admin/alarm_defs/','',1)
                    show_msg(gettext(gettext("恭喜你 成功接入自愈！")), 2);
                }
        }, 'json');
    }
