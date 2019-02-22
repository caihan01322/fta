/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

$(".step-td").hover(
    function() {
        $(".instance_log[data-step_name="+$(this).data('step_name')+"]").css("color", "red");
    }, function () {
        $(".instance_log[data-step_name="+$(this).data('step_name')+"]").css("color", "black");
    }
);
$('#retry-form').submit(function(e) {
    new bkDialog({
           type: 'dialog',
    	title: gettext("确认信息"),
    	icon: 'warning',
    	lock: true,
    	content: gettext("确定重试该任务吗？"),
    	confirmFn: function(){
    		e.preventDefault();
    	    this.submit();
    	    $('#retry-task').attr('disabled', 'disabled');
    	    $('#retry-task').html(gettext('重试中'));
    	},
    	okVal: gettext("确定"),
    	cancelFn: function(){},
    	cancelVal: gettext("取消")
    }).show();
});

$('#approval-task').click(function(e) {
    new bkDialog({
           type: 'dialog',
    	title: gettext("确认信息"),
    	icon: 'warning',
    	lock: true,
    	content: gettext("确定提交审批？"),
    	confirmFn: function(){
            var data = {}
            $('#approval-form').serializeArray().map(function(x){data[x.name] = x.value;});
            $.ajax({
                url: site_url + 'yes_or_no/',
                data: data,
                type: 'POST',
                beforeSend: function(){
                    $('#approval-task').attr('disabled', 'disabled');
                    $('.radio-x').attr('disabled', 'disabled');
                },
                success: function(){
                    $('#approval-task').html(gettext('已提交'));
                },
                error: function(){
                    $('#approval-task').html(gettext('提交失败'));
                }
            })
    	},
    	okVal: gettext("确定"),
    	cancelFn: function(){},
    	cancelVal: gettext("取消")
    }).show();
});
$('td[data-toggle=tooltip]').tooltip()