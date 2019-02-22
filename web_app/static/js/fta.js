/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
//此为自愈app的公用js

last_included_url = "" //上个页面的记录，用于返回
current_included_url = "" //当前小页面的记录

var arrayHistory = [];
var arrayHistoryUrls = [];
var alarmName = ''

$(document).on("click",".btn-toolbar.select-bar .btn",function(){
    $(this).toggleClass("btn-primary");
})

function htmlspecialchars(str){
    var r_str = String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
    return String(r_str).replace(/&lt;br\/&gt;/g, "<br/>")
}

function open_dialog(message, title){
    var d = new bkDialog({
        title: title,
        content: message,
        cancel: false,
    });
    d.show();
}

function resize_window() {
    if (!$("#sideNav").hasClass("lock-side")) {
        $(window).trigger('resize');
    }
}

//整体页面框架性函数，对右侧的主窗体进行刷新和加载的主函数
function include_open(url, on_included,isNav) {

    // debugger
    if(isNav == 1){
        arrayHistory = [];
        arrayHistoryUrls = [];
    }
    $('#include_loading').removeClass('hide');

    // 保存上一次请求的URL
    last_included_url = current_included_url;
    current_included_url = url;
    if(last_included_url == ""){
        last_included_url = current_included_url; //第一次加载，保证都有值
    }

    jsPlumb.deleteEveryEndpoint();

    $.ajax({
        url: site_url+url,
        type: 'GET',
        beforeSend:function(){
            $(".new_loading").show();
        },
        success: function(result){
          // debugger
            arrayHistory.push(result);
            arrayHistoryUrls.push(url)

            if(arrayHistoryUrls.length>1){
                $(".go_back_contain").show();
            }else{
                $(".go_back_contain").hide();
            }

            // 套餐管理-->接入自愈  定位套餐
            if (url.indexOf("/alarm_def/add/?name=")!=-1) {
              alarmName = url.split("name=")[1]
            } else {
              alarmName = ""
            }

            window.result = result;
            $("#open-content").html(result);
            setTimeout(function(){
                $(".new_loading").hide();
            },500)

            // 收敛规则 ---> 新建收敛规则
            if(url.indexOf("incident/?id=")!=-1){
                $("#bk_mask").fadeIn();
                $("#bk_mask_content").css("right","0");
            }


            // 告警源页面返回按钮处理
            if(url.indexOf("alarm_source/add")!=-1){
                $(".go_back_contain a").attr("onclick","goback(1)");
            }else{
                $(".go_back_contain a").attr("onclick","goback()");
            }
            //保存自愈套餐跳转按钮处理
            // alert(url.indexOf('link'))
            if(url.indexOf('js_item=1')!=-1){
              $('.saveBtnPanel button').attr('data-id', 'link');
            }
            if(url.indexOf('js_item=2')!=-1){
              $('.saveBtnPanel button').attr('id','link_type');
            }

            resize_window();
            $(".curActive", ".sidebar").removeClass("curActive");
            //selects = ['chart', 'alarm_def', 'decision', 'detection', 'action', 'report', 'wechat',
            //    'alarm_instance', 'intro', 'data_report_v2', 'solution', 'incident', 'analysis', 'advice', 'health']

            $.each($('.sidebar li[id]'), function(i, v){
              var key = $(v).attr('id').replace('li-', '');
              if (url.indexOf(key) >= 0) {
                $(v).addClass('curActive');
              }
            });

            $('#include_loading').addClass('hide');
            if(on_included){
                on_included.call();
            }
        },
        error: function(data){
            // ajax 异常统一在 settings.js 处理过，不再单独处理
        }
    })
}

// 导航定位
function locateRightNav (id) {
    var optParentItem = '$("#'+id+'")'
    var optItem = '$("#'+id+' a")'
    var optParentObj = eval(optParentItem)
    var optObj = eval(optItem)

    if(!optObj.hasClass("curActive")) {
        optObj.trigger("click")
        optParentObj.parent().show().parent().siblings().find("ul.subnav-list").slideUp()
    }
}

function open_external_url(external_url){
    var url = 'external_wrap/' + '?url=' + external_url;
    include_open(url, function(){
        $('.modal').modal('hide');
        $('.modal-backdrop').hide()});
}

function validate_inputs(container, inputs) {

    var is_validity = true;
    var container_el = $(container || "form");
    var input_q = inputs || "input:visible, input[type=number], select:visible, textarea:visible, .input:visible, .input-validate";
    container_el.find(input_q).each(function (idx, el) {
        if (!$(this).is(':hidden') && typeof(el.checkValidity) !== "undefined") {
            var input_el = $(el);
            input_el.removeClass("input-valid");
            input_el.removeClass("input-invalid");

            if (el.type === 'number' && el.value[0] === '0') {
                is_validity = false;
                input_el.addClass("input-invalid");
            } else if (el.checkValidity()) {
                input_el.addClass("input-valid");
            } else {
                is_validity = false;
                input_el.addClass("input-invalid");
            }
        }

    });
    return is_validity;
}

function validate_inputs_and_alert(container, content, inputs) {
    if (!validate_inputs(container, inputs)) {
        var invalid_input = $(container).find(".input-invalid:eq(0)");
        invalid_input.focus();
        content = content || invalid_input.data("error");
        show_msg(content || gettext("请完善配置"), 4);
        return false;
    }
    return true;
}

function go_back(){
    include_open(last_included_url);
}

function update_bpm_swtich_btn(bpm_on){
    if(bpm_on){
        $('#bpm_running').addClass('active btn-success').text('Running')
        $('#bpm_shutdown').removeClass('active btn-danger').text(gettext('自愈总开关'))
    }
    else{
        $('#bpm_running').removeClass('active btn-success').text(gettext('自愈总开关'))
        $('#bpm_shutdown').addClass('active btn-danger').text('Shutdown')
    }
}

// 提示框显示函数(code=0  警告 ; code=1 成功 ; code=-1 失败  )
function showWarning(code,words){

    switch(code){
        case '-1':
            $(".warning-bar").removeClass("success").removeClass("notice").addClass("fail");
            break;
        case '0':
            $(".warning-bar").removeClass("success").removeClass("fail").addClass("notice");
            break;
        case '1':
            $(".warning-bar").removeClass("fail").removeClass("notice").addClass("success");
            break;
        default:
            break;
    }
    $(".warn-text").text(words);
    $(".warning-bar").addClass('bar-on');
    setTimeout(function(){
        $(".warning-bar").removeClass('bar-on');
    },3000);
}

function goback(flag){

        if(flag){
            //刷新页面
            if(arrayHistoryUrls[1].indexOf('alarm_source/add') != -1){
                include_open(arrayHistoryUrls[0],'',1)
            }
        }else{
             var n = arrayHistoryUrls.length-2
            //从缓存中取页面
            // $("#open-content").html(arrayHistory[0]);
            $("#open-content").html(arrayHistory[0+n]);
        }

        arrayHistory.pop();
        arrayHistoryUrls.pop();
        if(arrayHistoryUrls.length>1){
            $(".go_back_contain").show();
        }else{
            $(".go_back_contain").hide();
        }
}

/*
* 格式化ajax结果
*/
function format_xhr_result(xhr) {
    var result = xhr.responseJSON || {
        result: null,
        success: undefined,
        message: xhr.responseText,
        code: 0,
    };
    return result;
}

/**
/* 弹窗选择插件
 * auth：v_weilli
 * 依赖组件 ：jquery artDialog bootstrap
 * 使用方式 ：$('#id').selectDialog({配置项});
 * 取值方式 ：$('#id').val();
 * 可用配置项 ：弹窗的宽：width, 弹窗的高：height, 弹窗的标题：title, 确定按钮的文字:okVal,关闭按钮的文字：cancelVal, 无选择时显示的文字:emptyText
 */
(function($){
  $.fn.selectDialog1 = function(options){
    var defaults = {
      type: "dialog",
      width : 800,
      height : 'auto',
      title : gettext('选择2'),
      okVal : gettext('保存'),
      cancelVal : gettext('取消'),
      emptyText : ''
    }
    var options = $.extend(defaults, options);
    var values = [];
    var optionText = [];
    var select = this;
    var module = '';
    if(select.attr('multiple') === 'multiple'){//多选
      module = 'multiple';
    }else{
      module = 'single';
    }
    options.selected = [];//选中的行
    options.emptyText = options.emptyText?options.emptyText: select.attr('placeholder');//无选择时显示的文字

    select.find('option').each(function(index, value){
      var v = $(value).attr('value');
      if($(value).attr('selected') === "selected"){
        options.selected.push(v);
      }
      values.push(v);
      optionText.push($(value).text());
    });
    var id = select.attr('id');
    var warpId = id + '-selectDialogWarp';
    var contentId = id + '-content';
    var dialogId = id + '-dialogId';
    var open_dialog = function(){
        var dialog = new bkDialog({
                          type: 'dialog',
          title: options.title,
          width: options.width,
          height : options.height,
          lock: true,
          content: creat_content(optionText),
          confirmFn: function(){
            creat_warp_content_new();
            // $(document).unbind('keydown');
            // creat_warp_content();
            // //点保存以后，设置select值
            // select.find('option').each(function(index, value){
            //   var option = $(value),
            //     v = option.attr('value');

            //   if($.inArray(v, options.selected) === -1){
            //     option.removeAttr('selected');
            //   }else{
            //     option.attr('selected', 'selected')
            //   }
            // });

            // select.trigger('change');
          },
          init : function(){//对话框弹出时执行的函数
            $(".aui_main").css('vertical-align', 'top');
            $(".aui_main").css('text-align', 'left');
            $(".aui_content .btn-toolbar .btn").click(function(){//绑定按钮点击事件
              btnClick(this);
            });

            $(".aui_content").find('button[data-id="check_all"]').click(function(){
              check_all();
            });
            $(".aui_content").find('button[data-id="inverse"]').click(function(){
              inverse();
            });
            $(document).keyup(function(event){
              if(event.keyCode == 27){
                dialog.close();
              }
            });
            //过滤
            $('input[data-id="keyword"]').bind('keyup',filter);
            //如果是单选，隐藏全选和反选
            if(module === 'single'){
              $('#'+dialogId).find('div[data-id="btn-group"]').hide();
            }
          },
          okVal: options.okVal,
          cancelFn: function(){
            $(".aui_main").css('vertical-align', 'middle');
            $(".aui_main").css('text-align', 'center');
            $(document).unbind('keydown');
          },
          cancelVal: options.cancelVal
        }).show();
      }
    var check_all = function(){
      $(".aui_content .btn-toolbar .btn").each(function(){
        var v = values[parseInt($(this).attr('data-index'))];
        if(v && !$(this).is(':hidden')){
          add(v);
          $(this).addClass('btn-primary');
        }
      });
    }
    var inverse = function(){
      $(".aui_content .btn-toolbar .btn").each(function(){
        if(!$(this).is(':hidden'))$(this).trigger('click');
      });
      //反选后执行一次过滤操作
      $('input[data-id="keyword"]').trigger('keyup');
    }
    var btnClick = function (btn){
      var btn =  $(btn);
      var value = values[parseInt(btn.attr('data-index'))];
      if(btn.hasClass('btn-primary')){
        btn.removeClass('btn-primary');
        remove(value);
      }else{
        //单选模式下，取消其他选中的
        if(module === 'single'){
          $('#'+ contentId + ' .btn-primary').each(function(index, v){
            $(v).trigger('click');
          });
        }
        btn.addClass('btn-primary');
        add(value);
      }
    }
    var add = function(v){
      if($.inArray(v, options.selected) === -1){
        options.selected.push(v);
      }
    }
    var remove = function(v){
      var key = $.inArray(v, options.selected);
      options.selected.splice(key,1);
    }
    var creat_warp_content = function(){
      var content = '<div class="btn-toolbar">';
      if(options.selected.length === 0 && options.emptyText){
        content += '<span style="color:#999999;">'+ options.emptyText +'</span>'
      }else{
        $.each(options.selected, function(index, v){
          var key = $.inArray(v, values);
          var value = optionText[key];
          if(value){
            content += '<div class="btn-group"><a class="btn btn-primary btn-xs">'+ value +'</a></div>';
          }
        });
      }
      content += '</div>';
      $('#'+warpId).html(content);
    };

    var creat_content = function(data){
      var toolbar = '<div class="row" style="height:44px;" id="'+ dialogId +'">'+
              '<div class="col-md-8" style="padding:0;">'+
                '<div class="btn-group btn-group-sm" data-id="btn-group" style="margin-bottom: 10px;">'+
                  '<a href="javascript: check_all()" class="btn btn-primary" data-id="check_all">' + gettext('全选') + '</a>'+
                  '<a href="javascript: inverse()" class="btn btn-success" data-id="inverse">' + gettext('反选') + '</a>'+
                '</div>'+
              '</div>'+
              '<div class="col-md-4" style="padding:0;">'+
              '<input type="text" data-id="keyword" placeholder="'+ gettext('搜索') + '..." style="float: right; margin-top: 3px;width:100%;">'+
              '</div>'+
              '</div>';
      var content = toolbar+'<div class="btn-toolbar select-bar" id='+ contentId +'>';
      $.each(data, function(index, v){
        var default_class = 'btn';
        if($.inArray(values[index], options.selected) > -1){
          default_class += ' btn-primary'
        }
        content += '<div class="btn-group btn-group-sm"><button class="'+ default_class +'" data-index="'+index+'" data-text="'+ v.toLowerCase() +'">'+ v +'</button></div>';
      });
      content += '</div>';
      return content;
    }
    var filter = function(event){
      var input = $(event.target),
        key = input.val().toLowerCase(),
        content = $('#'+contentId);
      if(key==''){
        content.find('button').show();
      }else{
        var buttons = content.find('button:not([data-text*="'+ key +'"]):not(.btn-primary)');
        content.find('button').show();//避免输入中文时的bug
        buttons.hide();
      }
    }
    this.each(function(){
      $(this).hide();
      if($('#'+warpId).length>0){//如果存在，清空内容
        $('#'+warpId).html('').off('click');
      }else{
        $(this).after('<div class="form-control" id="'+warpId+'" style="min-height:34px;height:auto;cursor: pointer;"></div>');
      }
      creat_warp_content();
      $('#'+warpId).click(function(){
        open_dialog(options);
      });
    });
    return this;
  }
})(jQuery);
