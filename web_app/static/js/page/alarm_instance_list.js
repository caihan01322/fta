/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

    dateType(0);//查询当天数据
    // $('#instance_count').html($('.alarm_instance_row').length);
    $('#incident_count').html($('.inc_back').length);

    // 下拉框渲染
    $(".select2_src").select2({"dropdownAutoWidth" : true});

    // 时间控件渲染
    setTimeout(function(){
        // 选择日期范围
        $('#selectDate').daterangepicker({
            locale : {
                "format" : 'YYYY-MM-DD'
            },
            autoApply: true
        })
        $('#selectDate').on("apply.daterangepicker",function(){
            filter_refresh(1);
        })
        get_unimportant_count();
    },1000)

    function get_query_string(page){
        var start_date = $("#selectDate").val().split(' - ')[0];
        var end_data = $("#selectDate").val().split(' - ')[1];
        if($("#selectDate").val()){
            begin_date = $("#selectDate").val().split(' - ')[0];
            end_date = $("#selectDate").val().split(' - ')[1];
            $(".time_selct_show").html('('+begin_date + gettext('至') + end_date+')')    
        }else{
            begin_date = '${begin_date}';
            end_date = '${end_date}';
            $(".time_selct_show").html('('+begin_date + gettext('至') + end_date+')') 
        }
        return 'ip='+ $('#ip-i').val()  + '&status=' + $('#status-filter').val()
                + '&cc_topo_set=' + $('#cc-topo-set-filter').val()
                + '&cc_app_module=' + $('#cc-app-module-filter').val()
                + '&alarm_type=' + $('#alarm-type-filter').val()
                + '&date=' + start_date + ' to ' + end_data
                + '&page='+ page;
    }

    //如果列表不多，就加入更多前端效果，否则禁用前端效果，防止卡
    if($('.alarm_instance_row').length < 50){
        $('a[data-toggle=tooltip]').tooltip()
    }

    function toggle_incident(incident_id){
        var alarms = $('.inc-' + incident_id)
        if(alarms.hasClass('hide')){
            alarms.removeClass('hide')
            $("#inc-icon-"+ incident_id).removeClass("fa-plus-square-o").addClass("fa-minus-square-o")
        }else{
            alarms.addClass('hide')
            $("#inc-icon-"+ incident_id).removeClass("fa-minus-square-o").addClass("fa-plus-square-o")
        }
    }
