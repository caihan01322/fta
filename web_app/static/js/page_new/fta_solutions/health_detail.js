/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

$(".offline_handle").on('click', function(){
    var advice_id = $(this).attr('data');
    var obj = $(this);
    new bkDialog({
        type: 'dialog',
        title: gettext("提示"),
        icon: 'warning',
        lock: true,
        content: gettext("已经线下处理该风险了吗？"),
        confirmFn: function () {
            $.ajax({
                url: site_url + tip_id + '/advice/handle/' + advice_id + '/',
                type: 'POST',
                dataType: 'json',
                success: function(result){
                    if (!result.result) {
                        alert_msg(result.message, 4);
                    } else {
                        var new_html = '<a href="' + site_url + tip_id + '/advice/show/'+advice_id+'/" '+
                                        'target="_blank" title="' + gettext('已经线下处理该风险') + '" ' + 
                                        'data-toggle="tooltip" data-placement="bottom" class="alarm_status_img">' +
                                        '<img src="'+ static_url+ 'images/status/success.png" widht="25" height="25"></a>'
                        $(obj).parent('td').html(new_html);
                    }
                }
            })
        },
        okVal: gettext("是"),
        cancelFn: function () {
        },
        cancelVal: gettext("否")
    }).show();
})


$(".table-packup table").on("click",".text-switch",function(){
    $(this).closest("tr").children("td").children(".limitText").toggleClass("hd")
    $(this).closest("tr").toggleClass("open-text close-text");
})
$(".table-packup tr").hover(function(){
    var _this = $(this);
    var curFlag = false;
    $(this).find(".limitText").each(function(){
        var limitTextWidth = $(this).parent("td").children(".limitText").width();
        var hiddenTextWidth = $(this).parent("td").children(".hiddenText").width();
        if(hiddenTextWidth>limitTextWidth){
            curFlag = true;
        }
    });
    if(curFlag){
        $(this).addClass("overLine");
    }else{
        $(this).removeClass("overLine");
    }
}, function(){
    $(this).removeClass("overLine");
});
