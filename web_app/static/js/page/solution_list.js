/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    $.bootstrapSortable(false, 'reversed');
    $(".copy_select").select2();
    $(document).click(function(){
        $(".copy_select").hide();
        $(".copy_button").show();
    })

    // 表格收起交互
    // $(".access-tab table").on("click",".text-switch",function(){
    //     $(this).closest("tr").toggleClass("open-text close-text");
    // })

    // $(".access-tab tr").hover(function(){
    //     var _this = $(this);
    //     var curFlag = false;
    //     $(this).find(".limitText").each(function(){
    //         if($(this).find("span").height()>42){
    //             curFlag = true;
    //         }
    //     });
    //     if(curFlag){
    //         $(this).addClass("overLine");
    //     }else{
    //         $(this).removeClass("overLine");
    //     }
    // },function(){
    //     $(this).removeClass("overLine");
    // })
