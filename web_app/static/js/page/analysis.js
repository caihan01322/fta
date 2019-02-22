/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$(function(){
    dateType(1);//查询30天数据
    setTimeout(function(){
            $('#selectTrendDate').daterangepicker({
                locale : {
                    "format" : 'YYYY-MM-DD'
                },
                autoApply: true,
                'opens': 'left'
            });

            show_mixed_trend();

            $('#selectTrendDate').on("apply.daterangepicker",function(){
                update_data()
            })

    },500);
    $(".time-group").hide();

    $('a[href=#mixed_trend]').on('shown.bs.tab', function (e) {
        //如果是首次打开, 则自动加载第一个图表, 并且将类型数字显示出来
        $(".time-group").hide();
        show_mixed_trend();
    })
    $('a[href=#failure]').on('shown.bs.tab', function (e) {
        $(".time-group").hide();
        show_failure();
    })
    show_trend_by_today();
})
function sort_by_tot(type) {
    var tot_html = '';
    var mark_list = [];

    var i = 0;
    $('.li_'+type).each(function() {
        mark_list[i] = 0;
        i += 1;
    })

    var pos = 0;
    for (var j = 0; j < mark_list.length; j ++) {
        var i = 0;
        var max = -1;
        var html = '';
        $('.li_'+type).each(function() {
            var count = Number($("#ul_"+type+" #"+$(this).attr("id").replace('li', 'count')).html());
            if (mark_list[i] == 0 && count > max ) {
                pos = i;
                max = count;
                html = '<li class="li_'+type+'" id="'+$(this).attr('id')+'">'+$(this).html()+'</li>';
            }
            i += 1;
        })
        mark_list[pos] = 1;
        tot_html += html;
    }
    $("#ul_"+type).html(tot_html);
}

