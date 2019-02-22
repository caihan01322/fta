# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import itertools

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
from guardian.shortcuts import (
    assign_perm, get_group_perms,
    get_groups_with_perms, get_user_perms,
    get_users_with_perms, remove_perm)

from account.accounts import Account
from fta_utils.component import bk
from permission import exceptions
from permission import roles
from permission.models import Business, BusinessGroupMembership, Loignlog
from project.conf.user import BkUser as User

CACHE_PREFIX = __name__.replace('.', '_')
CACHE_TIME = settings.CACHE_TIME


def _redirect_to_login(request):
    """
    重新登录
    """
    account = Account()
    response = account.redirect_login(request)
    return response


def _get_user_business_list(request, use_cache=True):
    """Get authorized business list for a exact username.

    :param object request: django request object.
    :param bool use_cache: (Optional)
    """
    user = request.user
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        # 获取用户所属开发商信息
        result = bk.cc.get_app_by_user_role({
            'user_role': ','.join(roles.ALL_ROLES),
            # 'user_role': roles.MAINTAINERS,
        })
        if result['result']:
            data = result['data']
            if data:
                cache.set(cache_key, data, CACHE_TIME)
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103, '20201', 20201, '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(result['message'])

    return data


def _get_user_info(request, use_cache=True):
    '''
    获取用户基本信息
    @param request:
    @param use_cache:
    @return:
    '''
    user = request.user
    cache_key = "%s_get_user_info_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)
    if not (use_cache and data):
        userinfo = bk.bk_login.get_user({})
        if userinfo['result']:
            data = userinfo['data']
            if data:
                cache.set(cache_key, data, CACHE_TIME)
        elif userinfo['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(userinfo['message'])
        elif userinfo['code'] in ('20103', 20103, '20201', 20201, '20202', 20202):
            raise exceptions.Forbidden(userinfo['message'])
        else:
            raise exceptions.APIError(userinfo['message'])
    return data


def _get_business_info(request, app_id, use_cache=True):
    """Get detail infomations for a exact app_id.

    :param object request: django request object.
    :param int app_id: cc_id of core.business model.
    """
    username = request.user.username
    cache_key = "%s_get_business_info_%s_%s" % (CACHE_PREFIX, app_id, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        result = get_app_by_id(request, app_id)
        if result['result']:
            data = result['data'][0]
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103, '20201', 20201, '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(result['message'])

        cache.set(cache_key, data, CACHE_TIME)

    return data


@transaction.atomic
def update_relationships(obj, extras, created=False, use_cache=True):
    cache_key = "%s_update_relationships_%s" % (CACHE_PREFIX, obj.cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        # If not created, clear business to group memberships
        if not created:
            obj.groups.clear()

        # Update business-group(role) relationships & group-user memberships
        for role in roles.ALL_ROLES:
            group_name = "%s\x00%s" % (obj.cc_id, role)
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                # assign view business perm for all roles
                assign_perm('view_business', group, obj)

                # assign manage business perm only for admin roles
                if role in roles.ADMIN_ROLES:
                    assign_perm('manage_business', group, obj)
            else:
                group.user_set.clear()

            BusinessGroupMembership.objects.get_or_create(
                business=obj,
                group=group
            )

            role_users = extras.get(role) or ''
            for username in role_users.split(';'):
                user, _ = User.objects.get_or_create(username=username)
                user.groups.add(group)

        cache.set(cache_key, True, CACHE_TIME)


@transaction.atomic
def assign_tmpl_perms(request, perms, groups, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business
    if user.has_perm('manage_business', biz):
        # 先删除所有有当前要授权权限的分组的权限
        perm_groups = get_groups_with_perms(tmpl_inst)
        for group in perm_groups:
            perm_list = get_group_perms(group, tmpl_inst)
            for perm in perm_list:
                if perm in perms:
                    remove_perm(perm, group, tmpl_inst)
        # 给当前有权限的分组授权
        for perm, group in itertools.product(perms, groups):
            assign_perm(perm, group, tmpl_inst)
    else:
        return HttpResponseForbidden()


@transaction.atomic
def assign_tmpl_perms_user(request, perms, users, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business
    if user.has_perm('manage_business', biz):
        # 删除有当前要授权权限的所有拥有用户的授权信息
        perm_users = get_users_with_perms(tmpl_inst)
        for name in perm_users:
            perm_list = get_user_perms(name, tmpl_inst)
            for perm in perm_list:
                if perm in perms:
                    remove_perm(perm, name, tmpl_inst)
        # then assign perms
        for perm, name in itertools.product(perms, users):
            assign_perm(perm, name, tmpl_inst)
    else:
        return HttpResponseForbidden()


def get_business_obj(request, cc_id, use_cache=True):
    cache_key = "%s_get_business_obj_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        info = _get_business_info(request, cc_id, use_cache)

        obj, created = Business.objects.update_or_create(
            cc_id=info['ApplicationID'],
            defaults={
                'cc_name': info['ApplicationName'],
                'cc_owner': info['Owner'],
                'cc_company': info['DeptName'],
            }
        )

        data = (obj, created, info)

        cache.set(cache_key, data, CACHE_TIME)

    return data


def _update_user_info(info):
    username = info['username']
    user_info = {
        'chname': info.get('chname'),
        'qq': info.get('qq'),
        'phone': info.get('phone'),
        'email': info.get('email'),
    }
    User.objects.update_or_create(
        username=username,
        defaults=user_info
    )


def _clean_user_info_list(user_info_list):
    d = {}
    for user_info in user_info_list:
        # if 'is_superuser' not in user_info:
        #     try:
        #         is_superuser = bool(int(user_info['role']))
        #         del user_info['role']
        #     except Exception:
        #         is_superuser = False
        #     user_info['is_superuser'] = is_superuser

        # do not change local is_superuser
        if 'role' in user_info:
            del user_info['role']

        d[user_info['username']] = user_info

    return d


def _diff_user_info(current, latest):
    result = []
    for username in latest:
        if username in current:
            if current[username] != latest[username]:
                result.append(latest[username])
        else:
            result.append(latest[username])
    return result


def update_user_info(request, cc_id, use_cache=True):
    cache_key = "%s_update_user_info_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        result = bk.bk_login.get_all_user({})
        if result['result']:
            # do not change local is_superuser
            current_info = _clean_user_info_list(User.objects.values('username', 'qq', 'phone', 'email', 'chname'))
            latest_info = _clean_user_info_list(result['data'])
            for info in _diff_user_info(current_info, latest_info):
                _update_user_info(info)
            # 获取当前用户的时区 和 语言
            cur_user_name = request.user.username
            _data = result['data']
            for _d in _data:
                if _d.get('username') == cur_user_name:
                    request.session['blueking_timezone'] = _d.get('time_zone', 'Asia/Shanghai')
                    request.session['blueking_language'] = _d.get('language', 'zh-cn')
                    break
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(result['message'])

        cache.set(cache_key, True, CACHE_TIME)


def prepare_business(request, cc_id, use_cache=True):
    # first, get the business object
    obj, created, extras = get_business_obj(request, cc_id, use_cache)

    # then, update business object relationships
    update_relationships(obj, extras)

    # update user info (uin and nick name)
    update_user_info(request, cc_id)

    return obj


def prepare_user_business(request, use_cache=True):
    user = request.user
    cache_key = "%s_prepare_user_business_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        data = []
        # for _, l in _get_user_business_list(request, use_cache).iteritems():
        for k, l in _get_user_business_list(request, use_cache).iteritems():
            for info in l:
                if info["ApplicationName"] in [u"资源池", "resource pool"]:
                    continue
                obj, res = Business.objects.update_or_create(
                    cc_id=info['ApplicationID'],
                    defaults={
                        'cc_name': info['ApplicationName'],
                        'cc_owner': info['Owner'],
                        'cc_company': info['DeptName'],
                    }
                )
                if obj not in data:
                    data.append(obj)

        cache.set(cache_key, data, CACHE_TIME)

    return data


def convert_readable_username(username):
    """将用户名转换成昵称"""
    return username


def get_biz_maintainer_info(biz_cc_id):
    '''
    获取当前业务下登录过的运维人员信息，包括 operator和auth_token
    @param biz_cc_id:
    @return: operator   业务运维
    @:return: auth_token  业务运维的认证信息
    '''

    role = "Maintainers"
    group_name = "%s\x00%s" % (biz_cc_id, role)
    group = Group.objects.get(name=group_name)
    user_list = group.user_set.order_by('last_login')
    operator = ''
    auth_token = ''
    for item in user_list:
        if item.auth_token:
            operator = item.username
            auth_token = item.auth_token
            break

    return operator, auth_token


def get_app_by_id(request, app_id):
    result = bk.cc.get_app_list({
        'app_id': app_id,
    })
    if not result['result']:
        return result
    app_list = result['data']
    app_info = {}
    for item in app_list:
        if int(item['ApplicationID']) == int(app_id):
            app_info = item
            break
    if request.user.username in app_info.get(roles.MAINTAINERS, '').split(';'):
        result.update({'data': [app_info]})
    else:
        result.update({
            'result': False,
            'code': 20201,
            'message': _(u"非运维身份不能执行此操作。")
        })

    return result


def _get_all_user_info(username):
    """
    获取所有用户的信息
    """
    cc_result = bk.bk_login.get_all_user({})
    if not cc_result.get('result', False):
        raise exceptions.APIError(cc_result.get('message', 'call component sdk error'))

    user_dict = {}
    for _data in cc_result['data']:
        user_dict[_data['username']] = _data['chname']
    return user_dict


def record_login_log(request):
    """
    记录用户登录日志
    @note: 为防止用户恶意登录导致登录日志过大，每 5 分钟记录一次登录日志
    """
    username = request.user.username
    cache_key = "%s_record_login_log_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)
    if not data:
        host = request.get_host()
        login_browser = request.META.get('HTTP_USER_AGENT', 'unknown')
        # 获取用户ip
        login_ip = request.META.get('HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR')
        Loignlog.objects.record_login(request.user, login_browser, login_ip, host)

        cache.set(cache_key, True, CACHE_TIME)
