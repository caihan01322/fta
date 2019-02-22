/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
$(document).ready(function(){

    var solution_data = $.parseJSON($("#real_solutions").val());

    var solution_type = {
        "success": "success",
        "~success": "failure",
    }
    var data_type = {
        "success": "success",
        "failure": "~success",
    }

    var data = transform_solution_data(solution_data, solution_type)

    bk = $('#bktopo').bkTopology({
        data:data,  //配置数据源
        autoPosition:true,
        readonly:false,  //是否可编辑
        lineType:[  //配置线条的类型
            {type:'success',value:gettext('成功'),lineColor:'#46c37b'},
            {type:'failure',value:gettext('失败'),lineColor:'red'},
            {type:'skip',value:gettext('跳过'),lineColor:'#888580'},
            {type:'authorize',value:gettext('授权'),lineColor:'#3675c5'},
            {type:'check',value:gettext('检查'),lineColor:'#f3b760'}
        ],
        onDbLineClick:function(event,data){  //点击连线的时候触发
            var thisTarget = $(this).data().target;
            var count = 0;            
            data.forEach(function(v,i){
                if(v.target == thisTarget){
                    count++;
                }
            });
            if(count>1){
                alert(gettext('删除路径'));
               bk.remove($(this));
               bk.reLoad();
            }
            $("#real_solutions").val(JSON.stringify(transform_data(data_type)));
        },
        onConnection:function(event,ldata){
            //return false;
            // 连线的时候触发该事件，return false 可阻止联线;
            edge_list = bk.getEdges();
            for (var i in edge_list){
                if(edge_list[i].source == ldata.source && edge_list[i].target == ldata.target){
                    bk.remove($('[data-id="'+edge_list[i].id+'"]'))
                    break
                }
            }
            $("#real_solutions").val(JSON.stringify(transform_data(data_type)));
        }
    });

    $('#bktopo').on('click','.option-group span',function(e){
        var type = $(this).prop('class').split(' ');
        var edgesType ='';       
        if(type.indexOf('success') != -1){
            edgesType= 'success';
        }else if(type.indexOf('failure') != -1){
            edgesType= 'failure'
        }else if(type.indexOf('other') != -1){
            edgesType= 'check'
        }
        var temp=[];
        var id = bk.getUUid();
        var source = $(this).parent().siblings('i').data('nodeId');           
        temp['nodes']={"id": id, "text": gettext('双击选择套餐'), "solution_id": 0, height : '80', width : '130'}
        temp['edges'] ={ "source": source, "target": id, edgesType:edgesType}
        bk.reLoad(temp);
        console.debug("data", data)
        $("#real_solutions").val(JSON.stringify(transform_data(data_type)));
       
    }).on('click','.fa-close',function(e){
        var dataid = $(this).attr('data-node-id');
        var parent = []
        var children = []
        var temp = []
          
        for(var i in data.edges){
            if(data.edges[i].source == dataid){
                children.push(data.edges[i])
            }
            else if(data.edges[i].target == dataid){
                parent.push(data.edges[i])
            }
        }
        if(children.length<2 || parent.length<2){
            bk.remove($('[data-id='+dataid+']'));
            for(var i in parent){
                for(var j in children){
                    temp['edges'] ={ "source": parent[i].source, "target": children[j].target, edgesType:children[j].edgesType}
                    bk.reLoad(temp);
                }
            }
        }
        else{
            alert(gettext("该节点暂不支持删除"))
        }
        $("#real_solutions").val(JSON.stringify(transform_data(data_type)));
    })

    /*双击节点文本显示修改窗口*/
    if(!bk.getConfig().readonly){
        $('#bktopo').on('dblclick','.node-text',function(){
            $('#editNodeText').modal('show');
            $('#editNodeText-btns').data({t:$(this)});
            var solution_id = $(this).parent().parent().data('solution_id');
            $('#editNodeText-btns').find('[data-id="'+solution_id+'"]').addClass('btn-primary');
        });
        /*对话框修改事件*/
        $('#editNodeText').on('click','.modal-edit',function(){            
            var node = $('#editNodeText-btns').data('t');
            $(node[0]).html($('#editNodeText-btns .btn-primary').html());
            var solution_id = $('#editNodeText-btns .btn-primary').data('id');
            $(node[0]).parent().parent().data({'solution_id':solution_id});
            $('#editNodeText').modal('hide');
            $("#real_solutions").val(JSON.stringify(transform_data(data_type)));
        });
    } 
    $('#editNodeText').on('hidden.bs.modal', function (e) {
        $('#editNodeText-btns .btn-primary').removeClass("btn-primary");
    })
})
 
    //  bk.remove('#node1'); //删除节点或者线，可接受字符串,jQuery对象
    //  bk.getNodes();  //获取所有的节点信息
    //  bk.getEdges();  //获取所有的连线信息
    //  bk.drawNode(object);  //创建节点 格式：{"id": "id1", "text": "node1 ", "left": 450, "top": 30  ,height : '50', width : '110'}必须包含id.否则自动生成uuid
    //  bk.drawPath({source:"window1",target:'window5',edgesType:'success'})
    //  bk.reLoad(data);
    // bk.reLoad("edges",{ "source": "window1", "target": "window4", edgesType:"authorize"})

function transform_solution_data(solution_data, solution_type){
    var nodes = []
    var edges = []
    //加入node_id
    for(var i in solution_data){
        var id = get_uuid();
        solution_data[i].push(id)
    }
    for(var i in solution_data){
        nodes.push({"id": solution_data[i][3], "text": solution_data[i][2], "solution_id": solution_data[i][1], height: '60', width: '130'})
        var relation = solution_data[i][0]
        if(relation != {}){
            for(var re in relation){
                edges.push({"source": solution_data[i][3], "target": solution_data[re][3], edgesType: solution_type[relation[re][0]]})
            }
        }
    }
    return {"nodes": nodes, "edges": edges}
}

function transform_data(data_type){
    var nodes = bk.getNodes();
    var edges = bk.getEdges();
    var solution_data = []
    for(var i in nodes){
        var relation = {}
        for(var j in edges){
            var source = edges[j].source
            if(nodes[i].id == source){
                var index = get_index_from_id(nodes, edges[j].target)
                var type = edges[j].edgesType
                relation[index] = [data_type[type]]
            }
        }
        var node = [relation, nodes[i].solution_id]
        solution_data.push(node)
    }
    return solution_data
}

function get_index_from_id(nodes, node_id){
    for(i in nodes){
        if(nodes[i].id == node_id){
            return i
        }
    }
}

function get_uuid(){
    var s = [];
    var hexDigits = "0123456789abcdef";
    for (var i = 0; i < 36; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
    }
    s[14] = "4";  
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1); 
    s[8] = s[13] = s[18] = s[23] = "-";
         
    var uuid = s.join("");
    return uuid;
}

