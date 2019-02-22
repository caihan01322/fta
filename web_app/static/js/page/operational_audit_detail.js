/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    $("#opt_type,#opt_obj,#opt_user").select2();

    var date = new Date();
    date.setDate(date.getDate() + 1);
    var end_date = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
    date.setDate(date.getDate() - 7);
    var start_date = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
    $('#selectDate3').daterangepicker({
        locale : {
            "format" : 'YYYY-MM-DD'
        },
        startDate: start_date,
        endDate: end_date,
        autoApply: true
    });

    // 分页样式控制
    var page_limit = parseInt($(".infoLimitNum").val());// 每一页数据量
    var all_page = parseInt($(".all_info_num span").text());//表格信息总数
    var int_num = parseInt(all_page/page_limit);
    var point_num = all_page%page_limit;
    point_num>0?point_num=1:point_num=0;
    var page_account = int_num+point_num;
    var ifSearch=0;

    var curParam;
    $("#opt_search_btn").click(function(){
        ifSearch = 1;
        curParam = {
            "page": 1,
            "limit": page_limit,
            "user": $("#opt_user").select2("val"),
            "object": $("#opt_obj").select2("val"),
            "operator_type": $("#opt_type").select2("val"),
            "content": $("#opt_content").val(),
            "start_time": $("#selectDate3").val().split(" - ")[0],
            "end_time": $("#selectDate3").val().split(" - ")[1]
        };
        refreshdata('',0);
    })

    paginationset(page_account,all_page);
    function paginationset(n,num){
        $(".all_info_num span").text(num);
        var pagination_html = '<li class="PreviousPage">'
                +'<a href="javascript:;" aria-label="Previous">'
                    +'<span aria-hidden="true">«</span>'
                +'</a>'
            +'</li>';

        for(var i=1;i<=n;i++){
            pagination_html += '<li class="pagenum"><a href="javascript:getPageData('+i+');">'+i+'</a></li>'
        }
        pagination_html += '<li class="NextPage">'
            +'<a href="javascript:;" aria-label="Next">'
                +'<span aria-hidden="true">»</span>'
            +'</a>'
        +'</li>';
        $(".pagination").html(pagination_html);
        $(".pagination li").eq(1).addClass("active");
        $(".pagination .PreviousPage").addClass("disabled");
        page_account==0||page_account==1?$(".pagination .NextPage").addClass("disabled"):0;
    }

    // 分页切换交互
    var curParam;
    function getPageData(n){
        var curPageIndex = $(".pagination li.active").index();
        if(n==curPageIndex) return ;
        $(".pagination li").eq(n).addClass("active").siblings().removeClass("active");
        refreshdata(n);
        n==1?$(".pagination .PreviousPage").addClass("disabled"):$(".pagination .PreviousPage").removeClass("disabled");
        n==$(".pagination li.pagenum").length?$(".pagination .NextPage").addClass("disabled"):$(".pagination .NextPage").removeClass("disabled");
    }

    // 上一页下一页
    $(".pagination").on("click",".PreviousPage", function(){
        if($(this).hasClass("disabled")) return ;
        var curPageIndex = $(".pagination li.active").index();
        getPageData(curPageIndex-1)
    })
    $(".pagination").on("click",".NextPage", function(){
        if($(this).hasClass("disabled")) return ;
        var curPageIndex = $(".pagination li.active").index();
        getPageData(curPageIndex+1)
    })

    function refreshdata(curindex,x){
        var isFlag = 0;
        if(x==0){
            isFlag = 1;
        }
        if(ifSearch == 1){
            if(curindex){
                curParam['page']=curindex;
            }
        }else{
            curParam = {
                "page": curindex
            }
        }

        $.ajax({
            url: location.pathname + "operational_audit_detail/?format=json",
            type: 'GET',
            beforeSend:function(){
                $(".new_loading").show();
            },
            data: curParam,
            success: function(result){
                var tabdata = result.details;
                var tabdatalen = result.total;
                var tabbodyHtml = ''
                if(tabdatalen==0){// 数据为空
                    $(".operational_audit_tab .none-data-note").hide();
                    tabbodyHtml = '<tr><td colspan="5" style="text-align:center;">' + gettext('无数据') + '</td></tr>';
                }else{
                    $.each(tabdata,function(index,value){

                        tabbodyHtml += '<tr><td>'+value.user+'</td>'
                            +'<td class="overflowing-td">'+htmlspecialchars(value.content)+'</td>'
                            +'<td>'+htmlspecialchars(value.object)+'</td>'
                            +'<td>'+value.operator_type+'</td>'
                            +'<td>'+value.time+'</td></tr>'
                    });
                }
                $(".operational_audit_tab table tbody").html(tabbodyHtml);
                // 分页样式重置
                if(isFlag==1){
                    var newpagesnum = parseInt(tabdatalen/page_limit);
                    tabdatalen%page_limit>0||newpagesnum==0?newpagesnum++:0;
                    paginationset(newpagesnum,tabdatalen);
                    $(".all_info_num span").text(tabdatalen)
                }
                setTimeout(function(){
                    $(".new_loading").hide();
                },500)
            }
        })
    }
