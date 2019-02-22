# -*- coding: utf-8 -*-
"""
urls config
"""
from django.conf import settings
from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
# admin.autodiscover()
from django.views.i18n import javascript_catalog

# 公共URL配置
urlpatterns = patterns(
    '',
    # Django后台数据库管理
    url(r'^admin/', include(admin.site.urls)),
    # 添加 account 相关页面
    url(r'^accounts/', include(settings.ACCOUNT_URL)),

    url(r'^doc/', include('home_application.urls')),

    url(r'^wechat/', include('wechat.urls', namespace='wechat', app_name='wechat')),
    url(r'^fta_admin/', include('fta_admin.urls', namespace='fta_admin', app_name='fta_admin')),

    url(r'^', include('fta_solutions_app.urls')),
    url(r'healthz/', "home_application.views.healthz"),
    # 处理JS翻译
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog, name='javascript-catalog'),
)

urlpatterns += settings.URL_ENV
