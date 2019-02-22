/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
//-----------------------------------------------------------
/**
 * 调试配置，请只在这个地方进行设置，不要动其他代码
 */
var debug = true; // 是否是调试模式，注意：在上传代码的时候，要改为false
//-----------------------------------------------------------

//以下公用代码区域，使用范围非常广，请勿更改--------------------------------
// document.write(" <script lanague=\"javascript\" src=\""+static_url+"assets/artdialog/jquery.artDialog.js?skin=simple\"> <\/script>");
//csrftoken
document.write(" <script lanague=\"javascript\" src=\""+static_url+"js/csrftoken.js?v=1\"> <\/script>");
/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
$.ajaxSetup({
//	timeout: 8000,
	statusCode: {
	    401: function(xhr) {
	    	//ajax 请求 未登录
	    	window.location.reload();
	    },
	    402: function(xhr) {
	    	// 功能开关
	    	var _src = xhr.responseText;
	    	ajax_content = '<iframe name="403_iframe" frameborder="0" src="'+_src+'" style="width:570px;height:400px;"></iframe>';
			new bkDialog({
                                    type: 'dialog',
			    title: gettext("提示"),
			    lock: true,
			    content: ajax_content
			}).show();
	    	return;
	    },
	    400: function(xhr){
			var reuslt = format_xhr_result(xhr);
	    	var content = reuslt.message + '<br><a href="'+site_url+ '">' + gettext('返回首页') + '</a>';
	    	new bkDialog({
                        type: 'dialog',
                        title: gettext("提示信息"),
                        icon: 'warning',
                        lock: true,
                        content: content,
                        confirmFn: function(){
                        },
                        okVal: gettext("确定")
                    }).show();
	    	$('#include_loading').addClass('hide');
	    },
	    403: function(xhr){
			var reuslt = format_xhr_result(xhr);
	    	var content = reuslt.message + '<br><a href="'+site_url+ '">' + gettext('返回首页') + '</a>';
	    	new bkDialog({
                        type: 'dialog',
                        title: gettext("提示信息"),
                        icon: 'warning',
                        lock: true,
                        content: content,
                        confirmFn: function(){

                        },
                        okVal: gettext("确定")
                    }).show();
	    	$('#include_loading').addClass('hide');
	    },
	    406: function(xhr){
			var reuslt = format_xhr_result(xhr);
	    	var content = result.message + '<br><a href="'+site_url+ '">' + gettext('返回首页') + '</a>';
    	    	new bkDialog({
                        type: 'dialog',
                        title: gettext("提示信息"),
                        icon: 'warning',
                        lock: true,
                        content: content,
                        confirmFn: function(){
                        },
                        okVal: gettext("确定")
                    }).show();
	    	$('#include_loading').addClass('hide');
	    },
	    501: function(xhr){
	    	var content = gettext('请求内容不合法！') + '<br><a href="' +site_url+ '">' + gettext('返回首页') + '</a>';
	    	new bkDialog({
                        type: 'dialog',
                        title: gettext("提示信息"),
                        icon: 'warning',
                        lock: true,
                        content: content,
                        confirmFn: function(){
                        },
                        okVal: gettext("确定")
                    });
            $('#include_loading').addClass('hide');
	    },
	    500: function(xhr){
	    	var content = gettext('服务暂时不可用，请联系开发人员！') + '<br><a href="' +site_url+ '">' + gettext('返回首页') + '</a>';
	    	new bkDialog({
                        type: 'dialog',
                        title: gettext("提示信息"),
                        icon: 'warning',
                        lock: true,
                        content: content,
                        confirmFn: function(){
                        },
                        okVal: gettext("确定")
                    }).show();
            $('#include_loading').addClass('hide');
	    }
	}
});
