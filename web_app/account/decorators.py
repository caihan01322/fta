# -*- coding: utf-8 -*-
"""登录装饰器."""
import json
from functools import wraps

from django.http import HttpResponse
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext as _


def login_exempt(view_func):
    """登录豁免,被此装饰器修饰的action可以不校验登录."""

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.login_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


def is_superuser(view_func):
    """
    检查超级管理员权限
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse(json.dumps({
                'result': False,
                'message': _(u"请使用管理员身份管理告警源<br>注: 对告警源操作会应用所有业务")
            }))

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def is_superuser_cls(view_func):
    """
    检查超级管理员权限
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse(json.dumps({
                'result': False,
                'message': _(u"请使用管理员身份管理告警源<br>注: 对告警源操作会应用所有业务")
            }))

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view
