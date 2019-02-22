/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
   
    if(!$("#li-alarm_instance_list").hasClass("open")) {
        $("#li-alarm_instance_list").trigger("click")
    }

    function filter_refresh(page){
        var url = tip_id + '/alarm_instance_list/?' + get_query_string(page);
        include_open(url);
        // 切换分页时滚至页面顶部
        setTimeout(function () {
            $('html,body').animate({'scrollTop': '0px'},500);
        }, 500)
    }

    function export_unimportant_alarm(){
        var url = tip_id + '/alarm_instance_list/?export=unimportant_alarm&' + get_query_string();
        include_open(url);
    }

    function get_unimportant_count(){
        var url = tip_id + '/alarm_instance_list/?export=unimportant_alarm_count&' + get_query_string();
        $.ajax({
            url: site_url+url,
            type: 'GET',
            success: function(result){
                $("#unimportant_count").html(result);
            }
        })

    }

    function export_ip(){
        if($("#selectDate").val()){
            begin_date = $("#selectDate").val().split(' - ')[0];
            end_date = $("#selectDate").val().split(' - ')[1];
            $(".time_selct_show").html('('+begin_date + gettext('至') + end_date+')')
        }else{
            begin_date = export_ip_begin_date;
            end_date = export_ip_end_date;
            $(".time_selct_show").html('('+begin_date + gettext('至') + end_date+')')
        }
        var url = tip_id + '/alarm_instance_list/?export=ip&' + get_query_string();
        $.ajax({
            url: site_url+url,
            type: 'GET',
            success: function(result){
                $("#instance-body").html(result);
            },
            error: function(){
                $("#instance-body").html(gettext('服务暂时不可用，请联系开发人员！'))
            }
        })
        $('#instance-dialog').modal('show');
    }

    function modal_open(url) {
        $.ajax({
            url: site_url+url,
            type: 'GET',
            success: function(result){
                $("#instance-body").html(result);

            },
            error: function(){
                $("#instance-body").html(gettext('服务暂时不可用，请联系开发人员！'))
            }
        })
        $('#instance-dialog').modal('show');
    }

    function modal_iframe_open(url) {
        result = "<iframe id='alarm_instance_detail' style='width:100%; height:95%;' scroll-behavior='inherit' frameBorder='0' src='"+site_url+url+"'></iframe>"
        $("#instance-body").html(result);
        $('#instance-dialog').modal('show');
    }
    function change_alarm_type(alarm_type){
        $("#alarm-type-filter").select2("val", alarm_type);
        $("#alarm-type-filter").trigger('change');
    }