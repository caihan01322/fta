# coding=utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.conf.urls import patterns, include
from tastypie.api import Api

from fta_advice.urls import urlpatterns_advice
from fta_solutions_app import api
from fta_solutions_app import views
from fta_solutions_app import views_def

v1_api = Api(api_name='v1')
v1_api.register(api.AlarmDefResource())
v1_api.register(api.AlarmTypeResource())
v1_api.register(api.AlarmInstanceResource())
v1_api.register(api.IncidentDefResource())
v1_api.register(api.IncidentResource())
v1_api.register(api.IncidentAlarmResource())
v1_api.register(api.BizConfResource())
v1_api.register(api.WorldResource())
v1_api.register(api.SolutionResource())
v1_api.register(api.AdviceResource())

urlpatterns = patterns(
    'fta_solutions_app.views',

    # tastypie
    (r'^(?P<cc_biz_id>\d+)/api/', include(v1_api.urls)),

    # 首页
    (r'^$', 'base'),
    (r'^(?P<cc_biz_id>\d+)/$', 'base'),
    # 自愈之旅页面
    (r'^(?P<cc_biz_id>\d+)/show_trip/$', 'show_trip'),

    # 告警定义界面
    (r'^(?P<cc_biz_id>\d+)/alarm_def_list/$', 'alarm_def_list'),
    (r'^(?P<cc_biz_id>\d+)/alarm_def/(?P<alarm_def_id>\w+)/$', 'alarm_def'),
    (r'^(?P<cc_biz_id>\d+)/alarm_def_copy/$', 'alarm_def_copy'),

    # 健康度报告界面
    (r'^(?P<cc_biz_id>\d+)/advice_list/$', 'advice_list'),
    (r'^(?P<cc_biz_id>\d+)/advice/handle/(?P<advice_id>\d+)/$', 'handle_advice'),
    (r'^(?P<cc_biz_id>\d+)/advice/show/(?P<advice_id>\d+)/$', 'show_offline_advice'),
    (r'^(?P<cc_biz_id>\d+)/health/$', 'health'),
    (r'^(?P<cc_biz_id>\d+)/health_detail/$', 'health_detail'),

    # 处理套餐界面
    (r'^(?P<cc_biz_id>\d+)/solution_list/$', 'solution_list'),
    (r'^(?P<cc_biz_id>\d+)/solution/(?P<solution_id>\w+)/$', 'solution'),
    (r'^(?P<cc_biz_id>\d+)/solution_form/(?P<solution_type_or_id>\w+)/$', 'solution_form'),
    (r'^(?P<cc_biz_id>\d+)/check_solution_title/(?P<solution_id>\w+)/$', 'check_solution_title'),

    (r'^(?P<cc_biz_id>\d+)/solution_copy/$', 'solution_copy'),
    (r'^(?P<cc_biz_id>\d+)/graph_copy/$', 'graph_copy'),

    # 收敛界面
    (r'^(?P<cc_biz_id>\d+)/incident/$', 'incident_def_list'),
    (r'^(?P<cc_biz_id>\d+)/block_incident/$', 'block_incident_def'),
    (r'^(?P<cc_biz_id>\d+)/add_incident/$', 'add_incident_def'),
    (r'^(?P<cc_biz_id>\d+)/del_incident/$', 'del_incident_def'),

    # 告警详情界面
    (r'^(?P<cc_biz_id>\d+)/alarm_instance_list/$', views.AlarmInstanceListView.as_view(),),
    # TODEL 兼容外部调用接口
    # (r'^alarm_instance_list/$', 'alarm_instance_list'),
    (r'^(?P<cc_biz_id>\d+)/alarm_instance/(?P<alarm_instance_id>\d+)/$', 'alarm_instance_page'),
    (r'^(?P<cc_biz_id>\d+)/alarm_instance/page/(?P<alarm_instance_id>\d+)/$', 'alarm_instance_page'),

    # (r'^preference/$', 'preference'),
    # (r'^intro/$', 'intro'),

    # 重试流程
    (r'^(?P<cc_biz_id>\d+)/retry/flow/$', 'retry_flow'),
    # 终止流程
    (r'^(?P<cc_biz_id>\d+)/stop/flow/$', 'stop_flow'),
    # 审批流程
    (r'^(?P<cc_biz_id>\d+)/approve/flow/$', 'approve_flow'),

)

# 告警定义的界面
# <legacy>基础定义的接口, 目前只有alarm_def用到
urlpatterns += patterns(
    'fta_solutions_app.views_def',

    (r'^check_perm/(?P<cc_biz_id>\d+)/$', 'check_perm'),
    # 添加自愈告警
    (r'^(?P<cc_biz_id>\d+)/add_alarm_def/$', 'add_alarm_def'),
    # 修改自愈告警
    (r'^(?P<cc_biz_id>\d+)/edit_alarm_def/$', 'edit_alarm_def'),
    # 删除自愈告警
    (r'^(?P<cc_biz_id>\d+)/del_def/(?P<func_type>\w+)/$', 'del_def'),
    # 开启/关闭全业务alarm_def
    (r'^(?P<cc_biz_id>\d+)/block_alarm_def/$', 'block_alarm_def'),
)

# 告警类型相关
urlpatterns += patterns(
    'fta_solutions_app.views_def',

    (r'^(?P<cc_biz_id>\d+)/alarm_type/del/$', 'del_alarm_type'),
    # 获取蓝鲸监控告警类型列表
    (r'^(?P<cc_biz_id>\d+)/alarm_type/alert/list/$', 'get_alert_alarm_types'),
    # 刷新蓝鲸监控的告警列表
    (r'^(?P<cc_biz_id>\d+)/alarm_type/alert/refresh/$', 'refresh_alert_alarm_types'),
)

# 告警源相关
urlpatterns += patterns(
    'fta_solutions_app.views_def',

    (r'^(?P<cc_biz_id>\d+)/alarm_source/list/$', 'alarm_source_list'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/add/(?P<page_type>[\w-]+)/(?P<source_id>\d+)/$', 'add_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/get/(?P<source_type>[\w-]+)/(?P<source_id>\d+)/$', 'get_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/config/(?P<source_id>\d+)/$', 'config_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/config_custom/(?P<source_id>\d+)/$', 'config_custom_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/config_email/(?P<source_id>\d+)/$', views_def.ConfigEmailAlarmSource.as_view()),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/reset/(?P<source_id>\d+)/$', 'reset_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/block/$', 'block_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/switch/$', 'switch_alarm_source'),
    (r'^(?P<cc_biz_id>\d+)/alarm_source/scripts/(?P<script_name>[\w\.]+)$', 'download_alarm_source_script', None,
     "alarm_source_scripts",),
)

# 统计报表界面
urlpatterns += patterns(
    'fta_solutions_app.views_analysis',

    (r'^(?P<cc_biz_id>\d+)/analysis/$', 'index'),
    # 操作审计
    (r'^(?P<cc_biz_id>\d+)/operational_audit_detail/$', 'operational_audit_detail',),
    # 自愈趋势
    (r'^(?P<cc_biz_id>\d+)/out_of_scope_trend/$', 'out_of_scope_trend'),
)

# 第二版统计报表  2015年1月1日
urlpatterns += patterns(
    'fta_solutions_app.views_data_v2',
    # 统计报表 收益数据dashboard
    (r'^(?P<cc_biz_id>\d+)/data_report_v2/$', 'data_report_v2'),
    # 统计报表 收益数据api
    (r'^(?P<cc_biz_id>\d+)/data_v2/counts/$', 'data_v2_counts'),

    (r'^(?P<cc_biz_id>\d+)/data/alarms_by_biz/$', 'data_alarms_by_biz'),
    (r'^(?P<cc_biz_id>\d+)/data/profit_by_time/$', 'data_profit_by_time'),
    (r'^(?P<cc_biz_id>\d+)/data/status/$', 'data_status'),

    (r'^(?P<cc_biz_id>\d+)/data/alarms_by_time/$', 'data_alarms_by_time'),
    (r'^(?P<cc_biz_id>\d+)/data/failure_by_time/$', 'data_failure_by_time'),
    (r'^(?P<cc_biz_id>\d+)/data/count_alarm_type/$', 'data_count_alarm_type'),
    (r'^(?P<cc_biz_id>\d+)/data/count_solution_type/$', 'data_count_solution_type'),

    (r'^(?P<cc_biz_id>\d+)/data/count_team/$', 'data_count_team'),
)

urlpatterns += patterns(
    'fta_solutions_app.views_component',
    (r'^(?P<cc_biz_id>\d+)/component/gcloud/(?P<task_name>\w+)/$', 'gcloud_component',),
)

urlpatterns += urlpatterns_advice
try:
    from fta_helper.urls import urlpatterns_helper

    urlpatterns += urlpatterns_helper
except Exception:
    pass

# 前端调用组件的便捷方式
urlpatterns += patterns(
    'fta_solutions_app.views_component',

    (r'^(?P<cc_biz_id>\d+)/component/(?P<module>\w+)/(?P<task_name>\w+)/$', 'component'),
)
