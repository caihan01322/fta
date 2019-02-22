/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
      $('.switch').bootstrapSwitch();
      $('.switch').on('switchChange.bootstrapSwitch', function (e, data) {
          $('#is_enabled_tips').html(gettext('* 请注意点保存哦！'))
      });

      $("#responsible").select2({
          placeholder: gettext("请选择额外通知人"),
          allowClear: true
      });
      // 业务Set属性发生改动时，重新render业务Set
      // 业务类型发生改动时，重新render业务模块
      $('#set_attr').bind('change', function(){
        var current_set_attrs = $("#set_attr").val() || [];
        var current_sets = $("#topo_set").val() || [];
        var related_sets = [];
        var related_sets_1 = [];
        var related_sets_2 = [];
        var related_sets_3 = [];

        $.each(current_set_attrs, function(i, set_attr){
          if (set_attr.indexOf("category") == 0){
            related_sets_1 = related_sets_1.concat(set_attr_to_topo_set_dict[set_attr] || []);
          }
        });
        $.each(current_set_attrs, function(i, set_attr){
          if (set_attr.indexOf("envi_type") == 0){
            related_sets_2 = related_sets_2.concat(set_attr_to_topo_set_dict[set_attr] || []);
          }
        });
        $.each(current_set_attrs, function(i, set_attr){
          if (set_attr.indexOf("service_state") == 0){
            related_sets_3 = related_sets_3.concat(set_attr_to_topo_set_dict[set_attr] || []);
          }
        });

        for (i = 0; i < related_sets_1.length; i = i + 1){
            if ((related_sets_2.length == 0 || related_sets_2.indexOf(related_sets_1[i]) >= 0) &&
                (related_sets_3.length == 0 || related_sets_3.indexOf(related_sets_1[i]) >= 0)){
                related_sets[related_sets.length] = related_sets_1[i];
            }
        }

        for (i = 0; i < related_sets_2.length; i = i + 1){
            if ((related_sets_1.length == 0 || related_sets_1.indexOf(related_sets_2[i]) >= 0) &&
                (related_sets_3.length == 0 || related_sets_3.indexOf(related_sets_2[i]) >= 0)){
                related_sets[related_sets.length] = related_sets_2[i];
            }
        }

        for (i = 0; i < related_sets_3.length; i = i + 1){
            if ((related_sets_2.length == 0 || related_sets_2.indexOf(related_sets_3[i]) >= 0) &&
                (related_sets_1.length == 0 || related_sets_1.indexOf(related_sets_3[i]) >= 0)){
                related_sets[related_sets.length] = related_sets_3[i];
            }
        }

        related_sets = $.unique(related_sets);
        RELATED_SETS = related_sets

        if (current_set_attrs.length === 0) {
          group_name = gettext('业务所有Set')
          set_list = all_set_list;
        }
        else {
          group_name = gettext('当前Set Attr相关');
          set_list = related_sets;
        }
        $('#topo_set').empty();

        $('#topo_set').append(render_optgroup(group_name, set_list, current_sets, 'set'));
        // $('#topo_set').selectDialog();
        $('#topo_set').change();
      })

      // 业务类型发生改动时，重新render业务模块
        $('#topo_set').bind('change', function(){
        var current_sets = $("#topo_set").val() || RELATED_SETS || [];
        var current_modules = $("#module").val() || [];
        var related_modules = [];
        $.each(current_sets, function(i, set_id){
          related_modules = related_modules.concat(topo_set_to_module_dict[set_id] || []);
        });

        // 把所有的modules分为两类，与当前选择SET相关/不相关
        related_modules = $.unique(related_modules);
        // unrelated_modules = module_list.filter(function(i){return related_modules.indexOf(i) < 0});
        // 修改module_list为当前相关modules

        if (current_sets.length === 0) {
          group_name = gettext('业务所有模块')
          module_list = all_module_list;
        }
        else {
          group_name = gettext('当前Sets相关');
          module_list = related_modules;
        }
        // 重新render select2
        $('#module').empty();
        $('#module').append(render_optgroup(group_name, module_list, current_modules, 'module'));
        // $('#module').append(render_optgroup("X 当前Sets无关", unrelated_modules, current_modules));
       // $('#module').selectDialog();
        });

        // 生成一个optgroup分组，用于业务模块处的select
        var render_optgroup = function(group_name, items, selected_list, type) {

        // 保留所有的已选择modules
        items = $.unique(selected_list.concat(items));
        if(type == 'module'){
            var selected_dict = module_name_dict;
        }else{
            var selected_dict = topo_set_name_dict;
        }
        var group = $('<optgroup>', {label: group_name});
          $.each(items, function(i, item) {
            var kwargs = {value: item, text: selected_dict[item]};
            if (selected_list.indexOf(item) !== -1) {
              kwargs['selected'] = 'true';
            }

            $('<option>', kwargs).appendTo(group);
          })

          return group;
        }

        $("#set_attr").change();
            $("#topo_set").change();
            function switchToMode(modeName) {
                $('#alarmdef_details').removeClass('mode-normal');
                $('#alarmdef_details').removeClass('mode-online');
                $('#alarmdef_details').removeClass('mode-customized');
                $('#alarmdef_details').removeClass('mode-process-missing');
                $('#alarmdef_details').removeClass('mode-sa-check');
                $('#alarmdef_details').removeClass('mode-bk');
                $('#alarmdef_details').addClass('mode-' + modeName);
            }
            if ($('#alarm_type').val() == 'customized') {
                switchToMode('customized');
            } else if ($('#alarm_type').val() == 'online') {
                switchToMode('online');
            } else if ($('#alarm_type').val() == 'process-missing') {
                switchToMode('process-missing');
            } else if ($('#alarm_type').val() == 'sa-check') {
                switchToMode('sa-check');
            }
            $('#alarm_type').change(function() {
                if ($('#alarm_type').val() == 'customized') {
                    switchToMode('customized');
                } else if ($('#alarm_type').val() == 'online') {
                    switchToMode('online');
                } else if ($('#alarm_type').val() == 'process-missing') {
                    switchToMode('process-missing');
                } else if ($('#alarm_type').val() == 'sa-check') {
                    switchToMode('sa-check');
                } else {
                    switchToMode('normal');
                }
            });
            $("#alarm_type").select2();
            $("#solution option").each(function() {
                // debugger
                // var _this = $(this)
                if($(this).text().trim() == comtom_name) {
                    // debugger
                        $(this).attr('selected', true);
                    }
            });
            $("#solution").select2();
            $("#clone_alarm_type").select2();
