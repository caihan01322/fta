/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    //编辑按钮
    $(".edit_config").on("click",function(){
        $(this).hide().next().show();
        $(".custom_input").removeAttr("readonly");
        $(".custom_select").removeAttr("disabled");
    });
    // 建议的正则
    function isURL(str) {
        return !str.match(/https?:\/\/.+?$/g);
    }
    // 参数验证
    function check_custom_input(){
        $(".notice_tips").text('')
        var app_url = $("#app_url").val();
        if(isURL(app_url)){
            $(".app_url_tips").text(gettext('拉取告警地址请输入http服务地址'));
            $("#app_url").focus();
            return false;
        }
        var exception_max_num = $("#exception_max_num").val();
        if(!(parseInt(exception_max_num) >= 0)){
            $(".exception_num_tips").text(gettext('异常阈值请输入非负整数'));
            $("#exception_max_num").focus();
            return false;
        }
        return true
    }
    //保存、取消按钮
    $(".resave_config").on("click",function(){
        var flag = true;
        flag = check_custom_input();
        if(!flag){return false;}
        $(".saveBtnList").hide().prev().show();
    });
    $(".cancel_config").on("click",function(){
        $(".saveBtnList").hide().prev().show();
        $(".custom_input").attr("readonly","readonly");
        $(".custom_select").attr("disabled", "disabled");
    });
    function save_config(obj,is_edit){
        flag = true;
        flag = check_custom_input();
        if(!flag){return false;}
        $(".custom_input").attr("readonly","readonly");
        $(".custom_select").attr("disabled", "disabled");
        var source_id = $("#source_id").val();
        if(source_id){
            var url = site_url + tip_id + "/alarm_source/config_custom/"+source_id+"/";
        }else{
            var url = site_url + tip_id + "/alarm_source/config_custom/0/";
        }
        $.post(url, {
            'app_name': $("#app_name").val(),
            'app_url': $("#app_url").val(),
            'app_method': $("#app_method").val(),
            'source_type': $("#alarm_source_head_custom_source_type").val(),
            'exception_max_num': $("#exception_max_num").val(),
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

        $(".custom_input").attr("readonly","readonly");
        $(".custom_select").attr("disabled", "disabled");

    }