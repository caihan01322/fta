/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

    dateType(1);//查询30天数据
    $('.data_select').select2({'width':'resolve'});
    // $("#search_btn").click(function(){
    //     // debugger
    //     $("#cc_biz_id").select2("val","");
    //     $('#alarm_type').select2("val","");
    //     $('#biz_team').select2("val","");
    //     $('#solution_type').select2("val","");
    //     $('#source_type').select2("val","");
    //     $('#source_type').select2("val","");
    //     $('#is_off_time').select2("val","");
    //     $("#selectDate2").val("");
    // })

    $('#start_time').datepicker({
        dateFormat: "yy-mm-dd"
    });
    $('#end_time').datepicker({
        dateFormat: "yy-mm-dd"
    });

    setTimeout(function(){

        $('#selectDate2').daterangepicker({
            locale : {
                "format" : 'YYYY-MM-DD'
            },
            autoApply: true
        })
        $('#selectDate2').on("apply.daterangepicker",function(){

        })
        update_chart();
    },1000)
