/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
    setTimeout(function(){
        refreshItemPos();
    },0)

    setTimeout(function(){
        $(".real_solution_div").show();
    },0)

    setTimeout(function(){
        flush_plumb(); //刷新连线
    },0)
function create_left(father_id) {
    var node_id = father_id * 2;
    create_node(node_id);
    setTimeout(function(){
        refreshItemPos();
    },0)

    setTimeout(function(){
        $("#real_solution_div_"+node_id).fadeIn();
    },10)

    setTimeout(function(){
        flush_plumb(); //刷新连线
    },200)

    refresh_data();
}

function create_right(father_id) {
    var node_id = father_id * 2 + 1;
    create_node(node_id);
    setTimeout(function(){
        refreshItemPos();
    },0)

    setTimeout(function(){
        $("#real_solution_div_"+node_id).fadeIn();
    },10)

    setTimeout(function(){
        flush_plumb(); //刷新连线
    },200)

    refresh_data();
}

var allItemsInfo = {};

function create_node(node_id){
    //如果已经创建过子节点则退出
    if ($("#real_solution_"+node_id).length > 0){
        show_msg(gettext("已经存在该节点")+node_id,4);
        return;
    }

    //计算是第几层
    var level = 1;
    while (Math.pow(2, level) <= node_id) { level+=1 }

    //没有层 DIV 就创建
    if (!$("#level-"+level).length > 0) {
        $("#widget-content").append('<div class="level" id="level-'+level+'"></div><div style="clear:both;height:30px;"></div>');
    }

    var pId = 1 ;
    if(node_id>1){
        if(node_id%2==0){
            pId = node_id/2;
        }else{
            pId = (node_id-1)/2;
        }
    }

    //创建子节点
    $("#level-"+level).append($("#template_real_solution").html().replace(/0/g, node_id));
    allItemsInfo[node_id] = {
        "parentID": pId,
        "prevs": "0"
    }

    //删除 select2
    $("#level-"+level).find('.real_solution').each(function(_, solution){
        $(solution).select2("destroy");
    })

    //重新排序
    var sort_ele = $("#level-"+level).find('.real_solution_div').sort(function(a, b){
        return $(a).data("id") > $(b).data("id");
    });
    $("#level-"+level).empty().append(sort_ele);

    //建立 select2
    $("#level-"+level).find('.real_solution').each(function(_, solution){
        $(solution).select2(SELECT_OPTION);
    })

    //有改动刷新数据
    $(".real_solution").off("change"); //先解除事件，避免事件列表内重复
    $(".real_solution").on("change", function(e){
        refresh_data();
    })
}

function delete_node(node_id){
    //根套餐无法被删除
    if (node_id == 1){
        show_msg(gettext("根套餐无法被删除"), 4);
        return
    }
    var left_node = $("#real_solution_"+(node_id*2));
    var right_node = $("#real_solution_"+(node_id*2+1));
    var real_solutions = $.parseJSON($("#real_solutions").val());
    //有两个子节点无法删除
    if (left_node.length != 0 && right_node.length != 0){
        show_msg(gettext("有两个子分支的套餐无法被删除"), 4);
        return
    }
    //无子节点直接删除
    if (left_node.length == 0 && right_node.length == 0){
        var nodeId = "real_solution_div_"+node_id
        jsPlumb.detachAllConnections(nodeId)
        $("#" + nodeId).remove();
        delete real_solutions[node_id]
        $("#real_solutions").val($.toJSON(real_solutions));
        return
    }
    //对只有一个子节点的套餐连接父子后重新绘图
    //清空界面，初始化新的组合套餐
    jsPlumb.deleteEveryEndpoint();
    $(".real_solution_div").not("#real_solution_div_0").remove();
    var new_real_solutions = {};
    var node_relation = {0:0};
    for (i in real_solutions){
        if (i == node_id){
            node_relation[i] = Math.floor(i/2);
            continue
        }
        //判断是否是当前节点的子孙节点
        var temp_i = i;
        while (Math.floor(temp_i/2) >= node_id){
            temp_i = Math.floor(temp_i/2);
        }
        //子孙节点则往上顺移，否则保持原位
        if (temp_i == node_id){
            var base_i = node_relation[Math.floor(i/2)];
            if ((Math.floor(i/2) != node_id && i % 2 == 1) ||
                (Math.floor(i/2) == node_id && node_id % 2 == 1)){
                new_real_solutions[base_i*2+1] = real_solutions[i];
                node_relation[i] = base_i*2+1;
            } else {
                new_real_solutions[base_i*2] = real_solutions[i];
                node_relation[i] = base_i*2;
            }
        } else {
            new_real_solutions[i] = real_solutions[i];
            node_relation[i] = i;
        }
    }
    //重新绘制
    $("#real_solutions").val($.toJSON(new_real_solutions));
    create_flowchart();
    refresh_data();
    setTimeout(function(){
        refreshItemPos();
    },0)

    setTimeout(function(){
        $(".real_solution_div").show();
    },10)

    setTimeout(function(){
        flush_plumb(); //刷新连线
    },20)
}

function insert_node(node_id){
    //清空界面，初始化新的组合套餐
    jsPlumb.deleteEveryEndpoint();
    $(".real_solution_div").not("#real_solution_div_0").remove();
    var real_solutions = $.parseJSON($("#real_solutions").val());
    var new_real_solutions = {};
    var node_relation = {0:0};
    for (i in real_solutions){
        //判断是否是当前节点的子孙节点
        var temp_i = i;
        while (Math.floor(temp_i/2) >= node_id){
            temp_i = Math.floor(temp_i/2);
        }
        //子孙节点(包含自己)则往下顺移，否则保持原位
        if (temp_i == node_id){
            if (i == node_id){
                var base_i = i;
            } else {
                var base_i = node_relation[Math.floor(i/2)];
            }
            if (i % 2 == 1){
                new_real_solutions[base_i*2+1] = real_solutions[i];
                node_relation[i] = base_i*2+1
            } else {
                new_real_solutions[base_i*2] = real_solutions[i];
                node_relation[i] = base_i*2
            }
        } else {
            new_real_solutions[i] = real_solutions[i];
            node_relation[i] = i
        }
    }
    new_real_solutions[node_id] = "";
    //重新绘制
    $("#real_solutions").val($.toJSON(new_real_solutions));
    create_flowchart();
    setTimeout(function(){
        refreshItemPos();
    },0)

    setTimeout(function(){
        $(".real_solution_div").show();
    },10)

    setTimeout(function(){
        flush_plumb(); //刷新连线
    },10)
}

function change_node(node_id){
    //清空界面，初始化新的组合套餐
    jsPlumb.deleteEveryEndpoint();
    $(".real_solution_div").not("#real_solution_div_0").remove();
    var real_solutions = $.parseJSON($("#real_solutions").val());
    var new_real_solutions = {};
    for (i in real_solutions){
        //判断是否是当前节点的子孙节点
        var temp_i = i;
        var remainder_path = [];
        while (Math.floor(temp_i/2) >= node_id){
            remainder_path[remainder_path.length] = temp_i % 2;
            temp_i = Math.floor(temp_i/2);
        }
        //对于子孙节点左右替换
        if (temp_i == node_id && node_id != i){
            var new_i = node_id;
            remainder_path[remainder_path.length-1] = 1 - remainder_path[remainder_path.length-1];
            for (j = remainder_path.length-1; j >= 0; j = j - 1){
                new_i = new_i * 2 + remainder_path[j];
            }
            new_real_solutions[new_i] = real_solutions[i];
        } else {
            new_real_solutions[i] = real_solutions[i];
        }
    }
    //重新绘制
    $("#real_solutions").val($.toJSON(new_real_solutions));
    create_flowchart();
    setTimeout(function(){
        refreshItemPos();
    },0)

    setTimeout(function(){
        $(".real_solution_div").show();
    },10)

    setTimeout(function(){
        flush_plumb(); //刷新连线
    },10)
}

function refresh_data(){
    var solution = {};
    $(".real_solution").each(function(_, real_solution){
        if ($(real_solution).data("id")){
            solution[String($(real_solution).data("id"))] = $(real_solution).val();
        }
    })
    $("#real_solutions").val($.toJSON(solution));
}

function flush_plumb(){

    //删除连线
    jsPlumb.deleteEveryEndpoint();

    //绘制连线
    $('.real_solution_div').each(function (_, $solution_div) {
        $solution_div = $($solution_div);
        var id = $solution_div.data("id")
        if (id > 1){
            var father_id = Math.floor(id/2);
            if (id%2 == 0){
                connect_success($("#real_solution_div_"+father_id), $solution_div);
            } else {
                connect_failure($("#real_solution_div_"+father_id), $solution_div);
            }
        }
    });
    jsPlumb.repaintEverything();
}

var sourceSuccessEndpoint = {
    endpoint: "Blank",
    isSource: true,
    connector: [ "Flowchart", { curviness: 20 } ],
    connectorStyle: {
        lineWidth: 2,
        strokeStyle: "#b6f2c8",
        joinstyle: "round"
    }
};
var sourceFailureEndpoint = {
    endpoint: "Blank",
    isSource: true,
    connector: [ "Flowchart", { curviness: 20 } ],
    connectorStyle: {
        lineWidth: 2,
        strokeStyle: "#fdc8c8",
        joinstyle: "round"
    }
};
var targetEndpoint = {
    endpoint: "Blank",
    isTarget: true
};

function connect_success(src, target) {
    jsPlumb.connect({
        source: jsPlumb.addEndpoint(src, sourceSuccessEndpoint, { anchor: [0.355, 1, 0, 1] }),
        target: jsPlumb.addEndpoint(target, targetEndpoint, { anchor: [0.355, 0, 0, 0] }) });
}

function connect_failure(src, target) {
    jsPlumb.connect({
        source: jsPlumb.addEndpoint(src, sourceFailureEndpoint, { anchor: [0.655, 1, 0, 1] }),
        target: jsPlumb.addEndpoint(target, targetEndpoint, { anchor: 'TopCenter' })
    });
}

function create_flowchart() {

    var real_solutions = $.parseJSON($("#real_solutions").val());

    //根据当前的套餐生成流程图
    for (i in real_solutions){
        create_node(parseInt(i));
        $("#real_solution_"+i).select2("val", real_solutions[i]);
    }

    flush_plumb(); //刷新连线 //setTimeout(function(){},2000);
}

$(document).ready(function() {
    jsPlumb.ready(function () {
        jsPlumb.importDefaults({
            ConnectionOverlays : [
                [ "Arrow", { location:0, width: 1} ]
            ]
        });

        jsPlumb.Defaults.Container = $('#widget-content');

        create_flowchart();
        setTimeout(function() {
          flush_plumb();
        });

    });

    // 画布超出视野支持滚动查看
    $(".canvas-outer-container").scroll(function () {
        var scrollLeftNum = $(".canvas-outer-container").scrollLeft()
        $(".canvas-outer-container svg").css("margin-left", "-"+scrollLeftNum+"px")
    })
});

function get_pre_items(id){
    var arrayList = $('#widget-content .real_solution_div[data-id="'+id+'"]').prevAll();
    var allNum = 0;
    $.each(arrayList,function(index,value){
        var s_num = 0;
        var curValueId = value.id.split("real_solution_div_")[1];
        $.inArray((2*curValueId),arrayIds)!=-1?s_num++:0;
        $.inArray((2*curValueId+1),arrayIds)!=-1?s_num++:0;
        s_num==0?s_num=1:0;
        allNum += s_num;
    })
    return allNum;
}

var arrayIds = [];//所有存在节点的ID值列表
var arrayItems = [];//所有存在节点参数列表
function refreshItemPos(){
    // 获取所有节点集合
    var all_solutions = JSON.parse($("#real_solutions").val());
    var all_solution_ids = [];
    var all_solution_info = {};
    $.each(all_solutions,function(item){
        all_solution_ids.push(parseInt(item));
        all_solution_info[item] = 0;
    })

    // 找到所有列的尾节点（所有没子节点的节点）
    var allColLast = [];
    var allItemPrevs = {};//所以节点前面节点数
    $.each(all_solution_ids,function(i,v){
        // 判断是否存在子节点
        allItemPrevs[v] = $("#real_solution_div_"+v).prevAll().length;
        if($.inArray((2*v),all_solution_ids)!=-1 || $.inArray((2*v+1),all_solution_ids)!=-1) return ;
        allColLast.push(v);
    });

    // 根据最后子节点查找该列其他元素列表
    var allColItems = [];
    $.each(allColLast,function(i,v){
        var curpos = v;
        var curList = [curpos];
        // 当前列尾节点偶数的时候
        var linkNum = curpos;
        while(linkNum!=1){
            all_solution_info[linkNum]++;
            // 子节点是偶数的时候
            if(linkNum%2==0){
                linkNum = linkNum/2;
            }else{
                // 奇数
                linkNum = (linkNum-1)/2;
            }
            curList.push(linkNum)
        }
        if(linkNum==1){
            all_solution_info[1]++;
        }
        allColItems.push(curList)

    })

    // 保存每个节点之前占位长度
    var all_prevs_info = {};
    $.each(all_solution_ids,function(i,s_id){
        var beforeNum = allItemPrevs[s_id];
        all_prevs_info[s_id] = 0
        var allWid = 0;
        for(var j= beforeNum - 1;j>=0;j--){
            var curIndex = eval($("#real_solution_div_"+s_id)).prevAll().eq(j).attr("data-id");
            allWid += all_solution_info[curIndex]
        }
        all_prevs_info[s_id] = allWid;
        // 当前节点和父节点对比
        var pId = 1 ;
        if(s_id>1){
            if(s_id%2==0){
                pId = s_id/2;
            }else{
                pId = (s_id-1)/2;
            }
        }
        var parentWid = all_prevs_info[pId];
        if(allWid > parentWid){
            allItemsInfo[s_id].prevs = allWid
        }else{
            allItemsInfo[s_id].prevs = parentWid
        }

        // 判断是否存在兄弟节点
        if(s_id%2!=0){
            if($.inArray((s_id-1),all_solution_ids)!=-1 && allItemsInfo[s_id].prevs==allItemsInfo[s_id-1].prevs){
                allItemsInfo[s_id].prevs += 1;
            }
        }
        $("#real_solution_div_"+s_id).css("left",allItemsInfo[s_id].prevs*170+"px")

    })

}

$("#widget-content").on("click",".right-list-icon",function(){
    $(this).prev().fadeToggle();
})
