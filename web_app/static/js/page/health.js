/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    $.bootstrapSortable(false, 'reversed')

    $('.followup').click(
        function(){
            var advice_id = $(this).parents('li').data('advice-id')
            update_advice(advice_id, 'followup', gettext('有用'), function(){})
        }
    )

    $('.deny-with-feedback').click(function(){
            var advice_id = $(this).parents('li').data('advice-id')
            //var comment = $('#feedback-'+advice_id).val()
            update_advice(advice_id, 'deny', gettext('没用'), function(){})
        }
    )

    $('.tooyoung-toosimple').click(function(){
            //$(this).siblings('.feedback').removeClass('hide');
            var advice_id = $(this).parents('li').data('advice-id')
            //var comment = $('#feedback-'+advice_id).val()
            update_advice(advice_id, 'deny', gettext('没用'), function(){})
        }
    )

    $('.finish').click(function(){
            var advice_id = $(this).parents('li').data('advice-id')
            update_advice(advice_id, 'finish', undefined, function(){
                clear_advice("followup")
            })
        }
    )

    $('.unfollow').click(function(){
            var advice_id = $(this).parents('li').data('advice-id')
            update_advice(advice_id, 'fresh', undefined, function(){
                clear_advice("followup")
            })
        }
    )

    $('.refollowup').click(function(){
            var advice_id = $(this).parents('li').data('advice-id')
            update_advice(advice_id, 'followup', undefined, function(){
                clear_advice("finish")
            })
        }
    )

    $('.fresh-button').click(function(){
            $('.fresh-button').addClass('selected-button');
            $('.followup-button').removeClass('selected-button');
            $('.finish-button').removeClass('selected-button');

            setTimeout(function(){
                $('#fresh-advice-list').removeClass('hide');
            }, 300);
            $('#followup-advice-list').addClass('hide');
            $('#finish-advice-list').addClass('hide');
        }
    )

    $('.followup-button').click(function(){
            $('.fresh-button').removeClass('selected-button');
            $('.followup-button').addClass('selected-button');
            $('.finish-button').removeClass('selected-button');

            $('#fresh-advice-list').addClass('hide');
            setTimeout(function(){
                $('#followup-advice-list').removeClass('hide');
            }, 300);
            $('#finish-advice-list').addClass('hide');
        }
    )

    $('.finish-button').click(function(){
            $('.fresh-button').removeClass('selected-button');
            $('.followup-button').removeClass('selected-button');
            $('.finish-button').addClass('selected-button');

            $('#fresh-advice-list').addClass('hide');
            $('#followup-advice-list').addClass('hide');
            setTimeout(function(){
                $('#finish-advice-list').removeClass('hide');
            }, 300);
        }
    )

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
    
    Date.prototype.format = function(format) {
           var date = {
                  "M+": this.getMonth() + 1,
                  "d+": this.getDate(),
                  "h+": this.getHours(),
                  "m+": this.getMinutes(),
                  "s+": this.getSeconds(),
                  "q+": Math.floor((this.getMonth() + 3) / 3),
                  "S+": this.getMilliseconds()
           };
           if (/(y+)/i.test(format)) {
                  format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
           }
           for (var k in date) {
                  if (new RegExp("(" + k + ")").test(format)) {
                         format = format.replace(RegExp.$1, RegExp.$1.length == 1
                                ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
                  }
           }
           return format;
    }
