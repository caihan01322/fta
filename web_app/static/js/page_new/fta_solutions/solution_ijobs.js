/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$(document).ready(function() {
    //create_ijobs_taskt_select();

    $('.ijobs_select2_src').select2()
    $("#r_retry_time").val($("#retry_time").val());
    $("#r_retry_count").val($("#retry_count").val());
    tags_change_taskt($("#app_id"));
});

$(".refresh-btn").on("click", function() {
    tags_change_taskt($("#app_id"));
})

function create_ijobs_taskt_select(){
    $.ajax({
        url: site_url + tip_id + '/component/job/get_task/',
        data: {'kwargs': '{"app_id": '+$("#app_id").val()+'}'},
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (result.success) {
                $("#ijobs_taskt_id").html("")
                $("#ijobs_taskt_id").append("<option value=''>----------</option>")
                for (i in result.message) {
                    var taskt = result.message[i];
                    if (taskt.id == s_ijobs_taskt_id) {
                        $("#ijobs_taskt_id").append("<option selected value='"+taskt.id+"'>"+taskt.name+"</option>")
                    } else {
                        $("#ijobs_taskt_id").append("<option value='"+taskt.id+"'>"+taskt.name+"</option>")
                    }
                }
                tags_change_taskt($("#ijobs_taskt_id"));
            } else {
                //alert(result.message);
                show_msg(result.message, 4);
            }
        }
    })
}

$("#app_id").change(function() {
    create_ijobs_taskt_select()
})

$("#retry,#parms,#argv").on("click",function() {
    $(this).parents(".form-group").next().toggle();
})

$("#retry_time").on('input', function() {
    $("#r_retry_time").val($("#retry_time").val());
})

$("#retry_count").on('input', function() {
    $("#r_retry_count").val($("#retry_count").val());
})


// 修改作业名
function tags_change_taskt(obj){
    var taskt_id = $(obj).val();
    var tag_ijobs_taski_id_obj = $("#tag_ijobs_taski_id");
    var option_html = '';
    if(taskt_id){
        tag_ijobs_taski_id_obj.next(".fa-spinner").removeClass('hide');
        tag_ijobs_taski_id_obj.select2("val", "");
        tag_ijobs_taski_id_obj.html(option_html);
        $.ajax({
            url: site_url + tip_id + '/component/job/get_task/',
            data: {'kwargs': '{"app_id": '+$("#app_id").val()+'}'},
            type: 'POST',
            dataType: 'json',
            success: function(result){
                if (result.success) {
                    option_html += '<option value=""></option>'
                    $.each(result.message, function(i,item){
                        if (item['id'] == s_task_id){
                            option_html += '<option selected value="'+ item['id'] +'">'+ item['name'] + ' (' + item['id'] + ')' +'</option>';
                        } else {
                            option_html += '<option value="'+ item['id'] +'">'+ item['name'] + ' (' + item['id'] + ')' +'</option>';
                        }
                    });
                    
                    tag_ijobs_taski_id_obj.html(option_html);
                    $('.ijobs_select2_src').select2("destroy")
                    $('.ijobs_select2_src').select2({
                        placeholder: gettext("请选择作业")
                    });
                    tag_ijobs_taski_id_obj.next(".fa-spinner").addClass('hide');
                    create_ijobs_taski_detail();
                    
                } else {
                    option_html += '<option value="" disabled>' + gettext('作业列表为空，请在作业平台创建作业') + '</option>'
                    tag_ijobs_taski_id_obj.html(option_html);
                    $('.ijobs_select2_src').select2("destroy")
                    $('.ijobs_select2_src').select2({
                        placeholder: gettext("作业列表为空，请在作业平台创建作业")
                    });
                    show_msg(result.message, 4);
                }

            }
        });
    }else{
        tag_ijobs_taski_id_obj.html(option_html);
    }
}

function tags_change_taski(obj){
    var taski_name = $(obj).find("option:selected").text();
    $('input[name=ijobs_taski_name]').val(taski_name);
    create_ijobs_taski_detail();
}

function create_ijobs_taski_detail(){
    $("#taski_detail").html("")
    if (!$("#tag_ijobs_taski_id").val()) {
        return
    }
    $.ajax({
        url: site_url + tip_id + '/component/job/get_task_detail/',
        data: {'kwargs': '{"task_id": '+$("#tag_ijobs_taski_id").val()+', "app_id": '+$("#app_id").val()+'}'},
        type: 'POST',
        dataType: 'json',
        success: function(result){
            if (result.success) {
                var tot_steps = 0;
                for (i in result.message.nmStepBeanList) {
                    var task_step = result.message.nmStepBeanList[i];
                    if (task_step['type'] != '1'){
                        continue
                    }
                    $("#taski_detail").append(
                        '<div class="input-group flex-group">'+
                        '<span class="input-group-unit">'+task_step.name+'</span>'+
                        '<input type="text" name="parms'+(task_step['ord']-1)+'" value="'+(STEP_PARMS[task_step['ord']-1] || '')+'" class="form-control" placeholder="' + gettext('请输入脚本参数')+ '"/></div>')
                    if (task_step['ord'] > tot_steps){
                        tot_steps = task_step['ord']
                    }
                }
                $("#steps").val(tot_steps);
            } else {
                //alert(result.message);
                show_msg(result.message, 4);
            }
        }
    })
}