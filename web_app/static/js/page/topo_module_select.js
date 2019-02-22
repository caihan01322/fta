/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

    // 存储集群列表数据字典
    var saveTopoList = {};
    $("#topo_set option").each(function(){
        saveTopoList[$(this).attr("value")] = $(this).text();
    })
    // 存储模块列表数据字典
    var saveModuleList = {};
    $("#module option").each(function(){
        saveModuleList[$(this).attr("value")] = $(this).text();
    })

    var dialogTpl = '<div style="padding:0;">'+
            '<div class="btn-group btn-group-sm" data-id="btn-group" style="margin-bottom: 10px;">'+
              '<a href="javascript: check_all()" class="btn btn-primary" data-id="check_all">' + gettext("全选") + '</a>'+
              '<a href="javascript: inverse()" class="btn btn-success" data-id="inverse">' + gettext("反选") + '</a>'+
            '</div>'+
          '</div>'+
          '<div class="btn-toolbar select-bar" id="module-content" style="max-height: 305px;overflow: auto;">';
    var curInput;
    var newModuleList = [];
    $(document).off('click', "#topo_set_list").on("click","#topo_set_list",function(){
        // 获取默认值
        var defaultSelect = $(this).find("input[type=hidden]").attr("selectedlist").split(",");
        curInput = "topo";
        var newTplStr = dialogTpl;
        var optionList = {}
        $("#topo_set option").each(function(){
            var curid=$(this).attr("value");
            var curtext=$(this).text();
            optionList[curid] = curtext
        })
        for (var id in optionList) {
            if ($.inArray(id, defaultSelect) == -1) {
                newTplStr += '<div class="btn-group btn-group-sm">' +
                    '<button class="btn" data-index="0" data-id="' + id + '">' + optionList[id] + '</button>' +
                    '</div>'
            } else {
                newTplStr += '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-primary" data-index="0" data-id="' + id + '">' + optionList[id] + '</button>' +
                    '</div>'
            }
        }

        newTplStr += '</div>';
        new bkDialog({
            type: 'dialog',
            title: gettext("选择集群"),
            width: 800,
            content: newTplStr,
            confirmFn: function () {
                creat_warp_content_new("topo");
            },
            okVal: gettext("确定"),
            cancelFn: function () {
            },
            cancelVal: gettext("取消")
        }).show();
    })
    $(document).off("click", "#module_set_list").on("click","#module_set_list",function(){
        // 获取默认值
        var defaultSelect = $(this).find("input[type=hidden]").attr("selectedlist").split(",");
        curInput = "module";
        var newTplStr = dialogTpl;
        // 获取与已选模型相关联的模块列表
        newModuleList = getRelatedList();
        
        $.each(newModuleList,function(i,set_id){
            if($.inArray(set_id,defaultSelect)==-1){
                newTplStr += '<div class="btn-group btn-group-sm">'+
                    '<button class="btn" data-index="0" data-id="' + set_id + '">' + module_name_dict[set_id]+'</button>'+
                '</div>'
            }else{
                newTplStr += '<div class="btn-group btn-group-sm">'+
                    '<button class="btn btn-primary" data-index="0" data-id="' + set_id + '">' + module_name_dict[set_id]+'</button>'+
                '</div>'
            }

        })

        newTplStr += '</div>';
        new bkDialog({
            type: 'dialog',
            title: gettext("选择模块"),
            width: 800,
            content: newTplStr,
            confirmFn: function () {
                creat_warp_content_new("module");
            },
            okVal: gettext("确定"),
            cancelFn: function () {
            },
            cancelVal: gettext("取消")
        }).show();
    })

    function getRelatedList(){
        var curSelectVal = [];
        // 获取当前已选集群列表
        $("#topo_set_list .btn-primary").each(function(){
            curSelectVal.push($(this).attr("data-id"))
        })

        // 获取集群可选列表
        var topoArrayList = [];
        $("#topo_set option").each(function(){
            topoArrayList.push($(this).attr("value"))
        })

        /**
         * 集群和模块值为空时，展示的选项默认是全部
        */
        var current_topo_sets = [];
        if(curSelectVal.length == 0){
            current_topo_sets = topoArrayList;
        }else{
            current_topo_sets = curSelectVal
        }

        var related_module_list = [];
        $.each(current_topo_sets, function(i, set_id){
            related_module_list = related_module_list.concat(topo_set_to_module_dict[set_id] || []);
        });

        var resList = related_module_list.filter(function (item, index, array) {
            return related_module_list.indexOf(item) === index;
        })
            
        return resList;
    }

    function creat_warp_content_new(type){
        var strTpl = "";
        var hiddenList = [];
        // 保存已选列表
        $(".btn-toolbar.select-bar .btn-primary").each(function(){
            var curId = $(this).attr("data-id");
            hiddenList.push(curId);
            strTpl += '<div class="btn-group"><a class="btn btn-primary btn-xs" data-id="'+curId+'">'+$(this).text()+'</a></div>'
        })
        if(strTpl==""){
            strTpl += '<span style="line-height: 30px;color: #CCC;">' + gettext('默认全选') + '</span>';
        }
        strTpl += '<input type="hidden" selectedList="'+hiddenList+'"/>'
        if(curInput=="topo"){
            $("#topo_set_list").html(strTpl);
        }
        if(curInput=="module"){
            $("#module_set_list").html(strTpl)
        }

        // 去除已选择不相关联选项
        var relatedList = getRelatedList();
        if(type == "topo"){
            // 选好集群 保留与集群关联模块
            var reVal = [];
            $("#module_set_list a").each(function(){
                var curId = $(this).attr("data-id");
                if($.inArray(curId,relatedList)==-1){
                    $(this).parent().remove();
                }else{
                    reVal.push(curId)
                }
            })
            $("#module_set_list input[type=hidden]").val(reVal.join(","))
        }

    }

    function check_all(){
        $(".btn-toolbar.select-bar .btn").addClass('btn-primary');
    }
    function inverse(){
        $(".btn-toolbar.select-bar .btn").each(function(){
            $(this).toggleClass("btn-primary");
        });
    }
