/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
(function(){
  var initMask = function(options){
    var opts = options || {},
      trigger = opts.el ? $(opts.el) : $(document),
      shown = opts.shown ? opts.shown : function(){},
      closed = opts.closed ? opts.closed : function(){}
      mask = $('#bk_mask'),
      bk_mask_content = mask.children('#bk_mask_content');

    //显示侧边栏
    trigger.on('click', function(){
      mask.show();
      setTimeout(function(){
        bk_mask_content.css('right', 0);
        shown && shown(mask);
      }, 10);
    });

    //隐藏侧边栏通用函数
    function hide(){
      bk_mask_content.removeAttr('style');
      setTimeout(function(){
        mask.hide();
        closed && closed(mask);
      }, 200);
    }

    bk_mask_content.find('#close').on('click', function(){
      hide();
    });

    //遮罩绑定事件
    mask.on('click', function(event){
      var target = event.target,
        $this = $(this);

      if($(target).attr('id') == 'bk_mask'){
        hide();
      }
    });
  }
  window.initMask = initMask;
})();
