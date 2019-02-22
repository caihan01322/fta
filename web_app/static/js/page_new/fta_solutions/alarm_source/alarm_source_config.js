/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
function reset_config(obj){
    
    var data = $(obj).attr('data');
    var source_id = $(obj).attr('source_id')
    new bkDialog({
        type: 'dialog',
        title: gettext("确认信息"),
        icon: 'warning',
        lock: true,
        content: gettext('重置是安全选项，会重新生成SecureKey')+ '<br>'+ data+ '<br><br>'+ gettext('请确认是否重置')+'？',
        confirmFn: function(){
            $.ajax({
                url: site_url + tip_id + '/alarm_source/reset/'+ source_id + '/',
                type: 'POST',
                dataType: 'json',
                success: function(data){
                    if(data.result){
                        $("#alarm_source_config").html(data.message);
                    }else{
                        show_msg(data.message, 4);
                    }
                }
            });
        },
        okVal: gettext("确定"),
        cancelFn: function(){},
        cancelVal: gettext("取消")
    }).show();
}