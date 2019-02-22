/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$("#alarm_type").on('change', function(){
    var data = $("#alarm_type").select2("data");
    var source_type = data.element[0].title;
    var alarm_type_text = data.text;
    if (source_type == 'ALERT' && !alarm_type_text.startsWith('[主机监控]') && !alarm_type_text.startsWith('[Host Monitor]')){
        $('.onchange-alarm-type-tip').text(gettext("蓝鲸监控的指标配置时维度包含IP、bk_cloud_id，否则在套餐中指定执行的IP"));
        $('.onchange-reg-tip').html(gettext('填写监控名称可区分不同的监控项') + '，<a href="http://docs.bk.tencent.com/product_white_paper/fta/Bk_Monitor_Distinguishing_Item.html" target="_blank">' + gettext('点击查看详情')+'</a>')
        $('.onchange-error-tip').show();
    }else{
        $('.onchange-error-tip').hide();
    }
})