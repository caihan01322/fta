/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$(".step-td").hover(
    function () {
        $(".instance_log[data-step_name=" + $(this).data('step_name') + "]").css("color", "red");
    }, function () {
        $(".instance_log[data-step_name=" + $(this).data('step_name') + "]").css("color", "black");
    }
);
$('#retry-form').submit(function (e) {
new bkDialog({
    type: 'dialog',
    title: gettext("确认信息"),
    icon: 'warning',
    lock: true,
    content: gettext("确定重试该任务吗？"),
    confirmFn: function () {
        e.preventDefault();
        this.submit();
        $('#retry-task').attr('disabled', 'disabled');
        $('#retry-task').html(gettext('重试中'));
    },
    okVal: gettext("确定"),
    cancelFn: function () {
    },
    cancelVal: gettext("取消")
}).show();
});

$('#bktopo').on('click','.fa-refresh', function(e){
var nodes = bk.getNodes()
for(var i in nodes){
    if(nodes[i].id == $(this).attr('data-node-id')){
        retry_flow(alarm_id, i)
        break;
    }
}
});

//终止流程
function stop_flow(id) {
new bkDialog({
    type: 'dialog',
    title: gettext("确认信息"),
    icon: 'warning',
    lock: true,
    content: gettext("是否确定终止"),
    confirmFn: function () {
        $.getJSON(site_url + alarm_cc_biz_id + "/stop/flow/", {
            id: id,
        }, function (feedback) {
            if (feedback.result) {
                showRes(gettext("终止成功"),true);
                setTimeout(function(){
                    window.location.reload();
                },3000)
            } else {
                showRes(gettext("终止失败:")+feedback.msg,true)
            }
        })
    },
    okVal: gettext("确定"),
    cancelFn: function () {
    },
    cancelVal: gettext("取消")
}).show();

}

//重试流程
function retry_flow(id, node_index) {
// $(".confirmAlert p").text(gettext("是否确定从#")+node_index+gettext("开始重试?"));
// $(".mako-alert").fadeIn();
// curID = id;
// curIndex = node_index;
new bkDialog({
    type: 'dialog',
    title: gettext("确认信息"),
    icon: 'warning',
    lock: true,
    content: gettext("是否确定从#")+node_index+gettext("开始重试?"),
    confirmFn: function (e) {
        $.getJSON(site_url + alarm_cc_biz_id + "/retry/flow/", {
            id: id,
            node_index: node_index
        }, function (feedback) {
            if (feedback.result) {
                showRes(gettext("成功开始重试"),true);
                window.location.reload();
            } else {
                $(".resAlert").addClass("wrongD").removeClass("rightD");
                $(".resAlert .resCenter").text(gettext("重试失败:")+feedback.msg);
                $(".resAlert").fadeIn();
            }
        })
    },
    okVal: gettext("确定"),
    cancelFn: function () {
    },
    cancelVal: gettext("取消")
}).show();
}

$(".selfFresh").on("click",function(){
window.location.reload();
});

$(".sureBtn").on("click",function(){
$(".resAlert").fadeOut();
});

//审批通过
function approve_flow(id, approve) {
    if($("#approve_text").val()!=""){
        $.getJSON(site_url + alarm_cc_biz_id + "/approve/flow/", {
            id: id,
            message: $("#approve_text").val(),
            approve: approve
        }, function (feedback) {
            if (feedback.result) {
                showRes(gettext("审批成功"),true)
            } else {
                showRes(gettext("审批失败:")+feedback.msg,false)
            }
            window.location.reload()
        })
    }else{
        showRes(gettext("请输入审批意见！"),false)
    }
}

function showRes(msg,flag){
    if(flag){
        $(".resAlert").addClass("rightD").removeClass("wrongD");
    }else{
        $(".resAlert").addClass("wrongD").removeClass("rightD");
    }
    $(".resCenter").text(msg);
    $(".resAlert").fadeIn();
    setTimeout(function(){
        $(".resAlert").fadeOut();
    },3000)
}

// setInterval("window.location.reload()",60000)
$('#log-content').scrollTop( $('#log-content')[0].scrollHeight );