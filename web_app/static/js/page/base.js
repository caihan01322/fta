/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
var curWinHeight = $(window).innerHeight();
var curMaxAlertHeight = curWinHeight*0.8;

window.onload = function () {
    var userAgent = window.navigator.userAgent.toLowerCase();
    $.browser.msie8 = $.browser.msie && /msie 8\.0/i.test(userAgent);
    $.browser.msie7 = $.browser.msie && /msie 7\.0/i.test(userAgent);
    $.browser.msie6 = !$.browser.msie8 && !$.browser.msie7 && $.browser.msie && /msie 6\.0/i.test(userAgent);
    if($.browser.msie8 || $.browser.msie7 || $.browser.msie6){
        $.gritter.add({
            title:  gettext('您的浏览器版本稍显陈旧哦'),
            text:   gettext('尊敬的用户, 为了亲能获得最佳浏览体验, 建议使用Chrome/Firefox/Safari/Opera/IE9以上的浏览器哦~'),
            sticky: true,
        });
    }

    // 接入指引交互Start
    $(".switch-left").on("click",function(){
        var cur_index = $(".guide-tab .on").index();
        if(cur_index>0){
            cur_index--;
            $(".guide-tab .guide-tab-item").eq(cur_index).addClass("on").siblings().removeClass("on");
            $(".guide-dot span").eq(cur_index).addClass("on").siblings().removeClass("on");
            if(cur_index==0){
                $(".switch-left").hide();
            }

            if(cur_index==1){
                $(".switch-right").show();
            }
        }
    });
    $(".switch-right").on("click",function(){
        var cur_index = $(".guide-tab .on").index();
        if(cur_index<2){
            cur_index++;
            $(".guide-dot span").eq(cur_index).addClass("on").siblings().removeClass("on");
            showSwitch(cur_index);
        }
    });

    function showSwitch(cur_index){
        if(cur_index==0){
            $(".switch-left").hide();
            $(".switch-right").show();
        }
        if(cur_index==1){
            $(".switch-left,.switch-right").show();
        }
        if(cur_index==2){
            $(".switch-left").show();
            $(".switch-right").hide();
        }
        $(".guide-tab .guide-tab-item").eq(cur_index).addClass("on").siblings().removeClass("on");
    }

    $(".guide-dot").on("click","span",function(){
        $(this).addClass("on").siblings().removeClass("on");
        var cur_index = $(".guide-dot .on").index();
        showSwitch(cur_index)
    });

    $(".guide-close,.back-bg,.guide-btn-to").on("click",function(){
            $(".access-guide").fadeOut(300);
    });

    $(".guide-access").on("click",function(){
            $(".access-guide").fadeIn(300);
    });

    // 接入指引交互End

    // 左侧菜单导航交互Start
    $(".pureLink").on("click",function(event){
        event.stopPropagation();
        $(".simple-nav li").removeClass("open").find("a").removeClass("curActive");
        $(".simple-nav li ul").slideUp();
        $(this).addClass("open").find("a").addClass("curActive");
    });

    $(".side-bar .subMenu>a").on("click", function(event){
        event.stopPropagation();
        var _this = $(this).parent();
        var side_bar = $(".side-bar");
        var _thisBrother = $(this).parent().siblings();
        _this.addClass("open").siblings().removeClass("open");
        _thisBrother.find("ul").slideUp();
        if (side_bar.hasClass("side-open")) {
            _this.find("ul").slideToggle();
        }
        else {
            _this.find("ul").slideDown();
        }
    });

    $(".subnav-list a").on("click",function(event){
        event.stopPropagation();
        $(".subnav-list a").removeClass("curActive");
        $(this).addClass("curActive");
        var _thisLi = $(this).parents("li.subMenu")
        if(!_thisLi.hasClass("open")){
            _thisLi.siblings().removeClass("open");
            _thisLi.addClass("open");
        }
    });

    $(".side-switch svg").on("click",function(event){
        event.stopPropagation();
        var self = $(this);
        var side_bar = $(".side-bar");
        var cur_active_item = side_bar.find(".curActive");
        var active_item_group = cur_active_item.closest(".subnav-list");
        var active_item_tab = active_item_group.closest(".subMenu");
        cur_active_item.removeClass("curActive");
        active_item_group.slideUp(0);
        self.toggleClass("open");
        side_bar.toggleClass("side-open side-close");
        side_bar.toggleClass("lock-side");
        $(".content").toggleClass("content-close");
        if ($("#sideNav").hasClass("side-close")) {
            $('.footer-row #footer').hide();
        } else {
            setTimeout(function () {
                $('.footer-row #footer').fadeIn(100);
            }, 500)
        }
        setTimeout(function(){
            if($('.homeLink').hasClass("open")){
                var echartInstance =  echarts.init(document.getElementById('mixed_trend_container'));
                echartInstance.setOption(mixed_trend_chart_opts)
            }
            if($("#li-data_report_v2 a").hasClass("curActive")){
                update_chart();
            }
        }, 500);
    });

    $(".logo").on("click",function(){
        $(".subMenu a.curActive").removeClass("curActive");
        $(".subMenu.open").removeClass("open").find("ul").slideUp();
        $(".homeLink").addClass("open");
    })

    // 左侧菜单导航交互End

    // 自愈之旅弹窗Start
    $(".fta-trip").on("click",function(){
        $(".trip-panel").load(site_url + tip_id +'/show_trip/');
        $(".trip-panel").fadeIn();
    });

    $(".trip-panel").on("click",".back-bg,.trip-close",function(){
        $(".trip-panel").fadeOut();
    });
    // 自愈之旅弹窗End

    // 新用户判断
    $(function(){
        var is_show_guide = $("#is_show_guide").val();
        if(is_show_guide == '1'){
            $(".access-guide").fadeIn(300);
        }
    })

    // 视频弹窗
    $(".access-video").on("click",function(){
        var player = document.getElementById('accessVideo');
        if (!playerInstance) {
            if (flvjs.isSupported()) {
                var playerInstance = flvjs.createPlayer({
                    type: 'mp4',
                    url: 'https://video-1252002024.cossh.myqcloud.com/%E6%95%85%E9%9A%9C%E8%87%AA%E6%84%88-02_1.%E6%8E%A5%E5%85%A5%E7%A3%81%E7%9B%98%E5%91%8A%E8%AD%A6%E8%87%AA%E6%84%88%E6%96%B9%E6%A1%88.mp4'
                });
                playerInstance.attachMediaElement(accessVideo);
                playerInstance.load(); //加载
            }
        }

        var v_curpos = ($(window).innerHeight() - $(window).innerWidth()*0.5)/2;
        $("#accessVideo,.close-video").css("top",v_curpos+"px");
        $(".access-video-modal").fadeIn();

        player.play();
    })

    $(".access-video-modal .back-bg,.close-video").on("click",function(){
        $(".access-video-modal").fadeOut();
        document.getElementById('accessVideo').pause();
    })

    // 表格收起交互 公共部分说
    $(".table-packup table").on("click",".text-switch",function(){
        // debugger
        $(this).closest("tr").children("td").children(".limitText").toggleClass("hd")
        $(this).closest("tr").toggleClass("open-text close-text");
    })

    $(".table-packup tr").hover(function(){
        var _this = $(this);
        var curFlag = false;
        $(this).find(".limitText").each(function(){
            // debugger
            if($.trim($(this).find("span").text()).length>0){
                curFlag = true;
            }
        });
        if(curFlag){
            $(this).addClass("overLine");
        }else{
            $(this).removeClass("overLine");
        }
    }, function(){
        $(this).removeClass("overLine");
    });
}
