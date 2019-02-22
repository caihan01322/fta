/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
var curWinHeight = $(window).innerHeight();
var charHeight = curWinHeight - 400;

$('#mixed_trend_container, #failure_container').height(charHeight)

var failure_options = {
    title: {
        x: 'center',
        y: 'top',
        textAlign: 'center',
        text: gettext('自愈失败原因分布图') + '('+ cc_biz_name + ')',
        textStyle: {
            fontWeight: 'normal'
        }
    },
	tooltip : {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#6a7985'
            }
        },
        backgroundColor: 'rgba(250, 250, 250, .85)',
        borderColor: 'rgb(255,192,0)',
        borderWidth: 1,
        textStyle: {
            color: '#797979',
            fontSize: 12
        },
        formatter: function (params, s, c){
            var colors = ['#7cb5ec','#434348', '#90ed7d', '#f7a35c', '#8085e9','#f15c80',  '#e4d354', '#2b908f','#f45b5b', '#546570', '#c4ccd3']
            var colorSpan = color => '<span style="display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:' + color + '"></span>'
            var formatTemp = '<p>' + params[0].name + '</p>'
            params.forEach(function (item, index) {
                formatTemp += '<p>' + colorSpan(colors[index]) + item.seriesName + ' : ' + item.value + '</p>'
            })
            return formatTemp
        }
    },
    color: ['#7cb5ec','#434348', '#90ed7d', '#f7a35c', '#8085e9','#f15c80',  '#e4d354', '#2b908f','#f45b5b', '#546570', '#c4ccd3'],
	legend: {
        show: true,
        orient: 'horizontal',
        x: 'center',
        y: 'bottom',
        padding: [0, 15],
        data: []
    },
	toolbox: {
        feature: {
            saveAsImage: {}
        }
    },
	grid: {
        borderWidth: 0
    },
    xAxis: [{
		type : 'category',
		boundaryGap : false,
		data : [],
        axisLabel: {
		    rotate: 45
        },
        splitLine: {
		    show: false
        }
	}],
    yAxis : [
        {
            type : 'value',
            name: gettext('次数'),
            nameLocation: 'top',
            nameTextStyle: {
                color: '#707070',
                verticalAlign: 'middle'
            },
            axisLine: {
                show: true,
                lineStyle: {
                    color: '#FFF'
                }
            }
        }
    ],
	series: []
}

var mixed_trend_chart_opts = {
    legend: {
        orient: 'horizontal',
        x: 'center',
        y: 'bottom',
        padding: [0, 15],
        data: [gettext('自愈失败'), gettext('自愈成功'), gettext('自愈指数')]
    },
    title: {
        x: 'center',
        y: 'top',
        textAlign: 'center',
        text: gettext('自愈指数趋势') + '('+ cc_biz_name + ')',
        textStyle: {
            fontWeight: 'normal'
        }
    },
    grid: {
        borderWidth: 0
    },
    toolbox: {
        feature: {
            magicType: {
                type: [
                    'line',
                    'bar',
                    'stack',
                    'tiled'
                ],
                show: true
            },
            restore: {
                show: true
            },
            dataView: {
                readOnly: false,
                show: true
            },
            saveAsImage: {
                show: true
            }
        },
        show: false
    },
    xAxis: {
        type: 'category',
        data: [],
        splitLine: {
            show: false
        },
        calculable: true,
        axisLabel: {
            rotate: 45
        },
        axisTick: {
            lineStyle: {
                color: '#DDD'
            }
        },
        axisLine: {
            lineStyle: {
                width: 1,
                color: '#DDD'
            }
        }
    },
    yAxis: [{
        type: 'value',
        name: gettext('告警（个）/ 日'),
        splitLine: {
            show: true,
            lineStyle: {
                color: '#DDD',
                width: 1,
                type: 'solid'
            }
        },
        boundaryGap: true,
        axisLabel: {
            show: true,
            formatter: '{value}',
            textStyle: {
                align: 'center'
            }
        },
        axisLine: {
            lineStyle: {
                color: '#FFF'
            }
        },
        nameTextStyle: {
            color: '#707070',
            verticalAlign: 'middle'
        },
        axisTick: {
            alignWithLabel: true
        },
        min: 0
    }, {
        type: 'value',
        name: gettext('自愈指数趋势'),
        axisLabel: {
            formatter: '{value}%',
            textStyle: {
                color: 'rgb(255,192,0)'
            }
        },
        axisTick: {
            lineStyle: {
                color: 'rgb(255,192,0)'
            }
        },
        splitLine: {
            show: false
        },
        nameTextStyle: {
            color: 'rgb(255,192,0)',
            verticalAlign: 'middle'
        },
        axisLine: {
            lineStyle: {
                color: '#FFF'
            }
        },
        min: 0,
        max: 100
    }],
    tooltip: {
        axisPointer: {
            type: 'shadow'
        },
        trigger: 'axis',
        backgroundColor: 'rgba(250, 250, 250, .85)',
        borderColor: 'rgb(255,192,0)',
        borderWidth: 1,
        textStyle: {
            color: '#797979',
            fontSize: 12
        }
    },
    series: []
}

function bar_tooltip_formatter(params){
    var colorSpan = color => '<span style="display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:' + color + '"></span>'
    var formatTemp = '<p>' + params[0].name + '</p>'
    params.forEach(function (item, index) {
        var hasPercent = index === 2 ? '%' : '';
        formatTemp += '<p>' + colorSpan(item.series.itemStyle.normal.color) + item.seriesName + ' : ' + item.value + hasPercent + '</p>'
    })
    return formatTemp
}

function show_trend_by_today(){

    $.ajax({
        url: site_url + tip_id + '/data/alarms_by_time/',
        data: {
            'start_time': analysis_end_time,
            'end_time': analysis_end_time,
        },
        type: 'GET',
        dataType: 'json',
        success: function(result){
            $("#trend_today").html(result.message.success_list[0] + '<em>/' + result.message.count +'</em>');
        }
    })
}

function show_mixed_trend(){

    $.ajax({
        url: site_url + tip_id + '/data/alarms_by_time/',
        data: {
            'start_time':getCurTime()[0],
            'end_time':getCurTime()[1],
        },
        type: 'GET',
        dataType: 'json',
        success: function(result){
            $.getJSON(site_url + tip_id + '/out_of_scope_trend/', {}, function(data) {
                mixed_trend_chart_opts.title.text = gettext('自愈趋势')+' ('+ cc_biz_name + ')';
                mixed_trend_chart_opts.xAxis.data = result.message.key;
                mixed_trend_chart_opts.tooltip.formatter = bar_tooltip_formatter;

                var success_list = new Array();
                var fail_list = new Array();
                var na_list = new Array();
                var trend_list = new Array();
                for(var i=0; i<result.message.key.length; i++) {
                    var d0 = result.message.success_list[i];
                    var d1 = result.message.value[i] - result.message.success_list[i];
                    var d2 = data.data_column1[i+1]
                    var d3 = 100 * d0 / (d0 + d1 + d2)
                    if(isNaN(d3)) {
                        d3 = 100
                    }
                    success_list.push(d0);
                    fail_list.push(d1)
                    na_list.push(d2);
                    trend_list.push(parseFloat(d3.toFixed(2)));
                }

                mixed_trend_chart_opts.series[0] = {
                    type: 'bar',
                    name: gettext('自愈成功'),
                    data: success_list,
                    smooth: true,
                    itemStyle: {
                        normal: {
                            color: '#5b9bd5',
                            areaStyle: {
                                type: 'default'
                            }
                        }
                    },
                    stack: 'normal'
                }
                mixed_trend_chart_opts.series[1] = {
                    type: 'bar',
                    name: gettext('自愈失败'),
                    color: '#ed7d31',
                    data: fail_list,
                    smooth: true,
                    itemStyle: {
                        normal: {
                            color: '#ed7d31',
                            areaStyle: {
                                type: 'default'
                            }
                        }
                    },
                    stack: 'normal'
                }
                mixed_trend_chart_opts.series[2] = {
                    type: 'line',
                    name: gettext('自愈指数'),
                    yAxisIndex: 1,
                    data: trend_list,
                    smooth: false,
                    symbol: 'circle',
                    symbolSize: 1,
                    itemStyle:{
                        normal:{
                            color: 'rgb(255,192,0)',
                            lineStyle: {
                                width: 2,
                                type: 'dotted'
                            }
                        }
                    }
                }

                // 获取自愈次数最大值
                var totalList = mixed_trend_chart_opts.series[0].data.map(function(item, index) {
                    return item + mixed_trend_chart_opts.series[1].data[index]
                })
                var maxNum = Math.max.apply(null, totalList)

                mixed_trend_chart_opts.yAxis[0].max = Math.ceil(maxNum/100)*100
                mixed_trend_chart_opts.yAxis[0].axisLabel = {
                    margin: 5,
                    textStyle: {
                        align: 'right'
                    }
                }
                var echartInstance =  echarts.init(document.getElementById('mixed_trend_container'));

                echartInstance.setOption(mixed_trend_chart_opts)
            });
        }
    })
}

function show_failure(){
    $.ajax({
        url: site_url + tip_id + '/data/failure_by_time/',
        data: {
            'start_time':getCurTime()[0],
            'end_time':getCurTime()[1],
        },
        type: 'GET',
        dataType: 'json',
        success: function(result){
            failure_options.legend.data = result.message.series_list.map(item => item.name);
            failure_options.xAxis[0].data = result.message.day_list;
            failure_options.xAxis[0].interval = Math.max(1, Math.floor(
                    result.message.day_list.length/15));
            failure_options.series = result.message.series_list.map(item => {
                item['type'] = 'line'
                return item
            });

            var echartInstance =  echarts.init(document.getElementById('failure_container'));
            echartInstance.setOption(failure_options)
        }
    })
}

function update_data() {
    // 自愈指数趋势图更新
    show_mixed_trend();
    // 失败分析图更新
    show_failure();
}
