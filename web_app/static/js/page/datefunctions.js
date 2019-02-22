/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
function getStartDate(sDate){
    // 日期往前推算30天
    var curData = sDate.split("-");
    var curY = curData[0];
    var curM = curData[1];
    var curD = parseInt(curData[2]);
    // 上月起始号数
    var preDate ;

    var resDays = Math.abs(curD-30);

    if(curD-30>=0){
        // 不跨月份情况
        preM<10?preM="0"+preM:0;
        preDate = curY + "-" + curM + "-" + getStrNum(resDays+1);
    }else{
        // 跨月份情况（1.跨年份 ； 2.不跨年份）
        if(parseInt(curM) == 1){
            var preY = parseInt(curY)-1;
            var preDays = getDaysInOneMonth(preY,12);
            preDate = preY + "-12-" + (preDays-resDays+1)
        }else{
            var preM = parseInt(curM)-1;
            preM<10?preM="0"+preM:0;
            var preDays = getDaysInOneMonth(curY,preM);
            preDate = curY + "-" + preM + "-" + (preDays-resDays+1);
        }
    }

    return preDate;
}

// 获取某年某月天数
function getDaysInOneMonth(year, month){
    month = parseInt(month, 10);
    var d= new Date(year, month, 0);
    return d.getDate();
}

// 1-9的整数 转换成 01-09字符串
function getStrNum(num){
    var resStr = num;
    if(num<10){
        resStr = "0" + num;
    }
    return resStr ;
}

function getCurTime(){

    var arrayDate = [];

    if($("#selectTrendDate").val()){
        startDate = $("#selectTrendDate").val().split(' - ')[0];
        endDate = $("#selectTrendDate").val().split(' - ')[1];
    }else{
        startDate = lastMonthDate;
        endDate = todayDate;
    }

    arrayDate = [startDate,endDate];
    return arrayDate

}

function dateType(flag){
    if(flag == 0){
        // 查询当天数据
        lastMonthDate = todayDate;
    }else{
        // 查询一个月数据
        lastMonthDate = getStartDate(todayDate);
    }
}

var curDate = new Date();
var tYear = curDate.getFullYear();
var tMonth = curDate.getMonth() + 1;
var tDay = curDate.getDate();
tMonth = getStrNum(tMonth);
tDay = getStrNum(tDay);

var todayDate = tYear+"-"+tMonth+"-"+tDay;
var lastMonthDate ;

var startDate;
var endDate;
