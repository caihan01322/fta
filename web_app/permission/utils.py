# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import itertools

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponse
from guardian.shortcuts import (
    assign_perm, remove_perm,
    get_users_with_perms, get_groups_with_perms,
    get_group_perms, get_user_perms
)

from fta_utils.component import bk
from permission import exceptions
from permission import roles
from permission.models import Business, BusinessGroupMembership
from project.conf.user import BkUser as User

CACHE_PREFIX = __name__.replace('.', '_')


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
        userinfo = _get_user_info(request)
        owner = userinfo.get('company_code')
        result = bk.cc.get_app_by_user_role({
            'user_role': ','.join(roles.ALL_ROLES),
        })
        if result['result']:
            data = result['data']
            if data:
                # 按照开发商过滤
                for key, val in data.iteritems():
                    if val:
                        temp_list = []
                        for item in val:
                            if item['Owner'] == owner:
                                temp_list.append(item)
                        data.update({key: temp_list})
                cache.set(cache_key, data, 60 * 5)
        elif result.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result.get('code') in ('20103', 20103, '20201', 20201, '20202', 20202):
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
        userinfo = bk.auth.get_user_info({})
        if userinfo['result']:
            data = userinfo['data']
            if data:
                cache.set(cache_key, data, 60 * 5)
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
        result = bk.cc.get_app_by_id({
            'app_id': app_id,
            'uin_to_openid_column': ','.join(roles.ALL_ROLES),
        })
        if result['result']:
            data = result['data'][0]
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103, '20201', 20201, '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(result['message'])

        cache.set(cache_key, data, 60 * 5)

    return data


def update_relationships(obj, extras, created=False, use_cache=True):
    """
    Update business-group(role) relationships & group-user memberships
    """
    cache_key = "%s_update_relationships_%s" % (CACHE_PREFIX, obj.cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        groups = {}
        # first, create related groups if not exist
        for role in roles.ALL_ROLES:
            group_name = "%s\x00%s" % (obj.cc_id, role)
            group, created = Group.objects.get_or_create(name=group_name)
            groups[group_name] = (group, created)

            if created:
                # assign view business perm for all roles
                assign_perm('view_business', group, obj)

                # assign manage business perm only for admin roles
                if role in roles.ADMIN_ROLES:
                    assign_perm('manage_business', group, obj)

        with transaction.atomic():
            try:
                Business.objects.select_for_update().get(pk=obj.pk)
            except Business.DoesNotExist:
                return None

            data = cache.get(cache_key)

            if not (use_cache and data):
                # If not created, clear business to group memberships
                if not created:
                    obj.groups.clear()

                for group_name in groups:
                    group, created = groups[group_name]
                    # If not created, clear group to user memberships
                    if not created:
                        group.user_set.clear()

                    BusinessGroupMembership.objects.get_or_create(
                        business=obj,
                        group=group
                    )

                    role = group_name.split('\x00')[1]
                    role_users = extras.get('{}Openid'.format(role)) or ''
                    for username in role_users.split(';'):
                        user, _ = User.objects.get_or_create(username=username)
                        user.groups.add(group)

                cache.set(cache_key, True, 60 * 5)


@transaction.atomic
def assign_tmpl_perms(request, perms, groups, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business

    # if user.has_perm('manage_business', biz):
    #     # assign perms first
    #     for perm, group in itertools.product(perms, groups):
    #         assign_perm(perm, group, tmpl_inst)
    #
    #     # then expired clear perms
    #     for group in groups:
    #         for perm in get_perms(group, tmpl_inst):
    #             if perm not in perms:
    #                 remove_perm(perm, group, tmpl_inst)
    # else:
    #     return HttpResponseForbidden()

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

    # if user.has_perm('manage_business', biz):
    #     # assign perms first
    #     for perm, name in itertools.product(perms, users):
    #         assign_perm(perm, name, tmpl_inst)
    #
    #     # then expired clear perms
    #     for name in users:
    #         for perm in get_perms(name, tmpl_inst):
    #             if perm not in perms:
    #                 remove_perm(perm, name, tmpl_inst)
    #     return True
    # else:
    #     return HttpResponseForbidden()

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

        cache.set(cache_key, (obj, False, info), 60 * 5)

    return data


def _update_user_info(info):
    User.objects.update_or_create(
        username=info['openid'],
        defaults={
            'first_name': info['uin'],
            'last_name': info['userName'],
        }
    )


def update_user_info(request, cc_id, use_cache=True):
    cache_key = "%s_update_user_info_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        result = bk.auth.get_owner_info({})
        if result['result']:
            for k, v in result['data'][0].iteritems():
                if isinstance(v, dict):
                    _update_user_info(v)
                elif isinstance(v, list):
                    for info in v:
                        _update_user_info(info)
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(result['message'])

        cache.set(cache_key, True, 60 * 5)


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
        for _, l in _get_user_business_list(request, use_cache).iteritems():
            for info in l:
                if info["ApplicationName"] == u"资源池":
                    continue
                obj, _ = Business.objects.update_or_create(
                    cc_id=info['ApplicationID'],
                    defaults={
                        'cc_name': info['ApplicationName'],
                        'cc_owner': info['Owner'],
                        'cc_company': info['DeptName'],
                    }
                )
                if obj not in data:
                    data.append(obj)

        cache.set(cache_key, data, 5)

    return data


# def get_biz_maintainer(request, cc_biz_id):
#     role_data = _get_business_info(request, cc_biz_id)
#     maintainers = role_data['MaintainersOpenid']
#     # maintainer = maintainers.split(';')[0] if maintainers else ''
#     return maintainers


def get_biz_maintainer_info(cc_biz_id):
    '''
    获取当前业务下登录过的运维人员信息，包括 operator和auth_token
    @param cc_biz_id:
    @return: operator   业务运维
    @:return: auth_token  业务运维的认证信息
    '''

    role = "Maintainers"
    group_name = "%s\x00%s" % (cc_biz_id, role)
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


def _show_tutorial(request, identifier_code):
    group_name = 'tutorial\x00%s' % identifier_code
    return not request.user.groups.filter(name=group_name).exists()


def _is_user_maintainer(request, cc_biz_id):
    '''
    判断当前用户是否为业务运维
    @param request:
    @param cc_biz_id:
    @return:
    '''
    try:
        business = prepare_business(request, cc_id=cc_biz_id)
    except exceptions.Unauthorized:
        # permission denied for target business (irregular request)
        return HttpResponse(status=406)
    except exceptions.Forbidden:
        # target business does not exist (irregular request)
        return HttpResponseForbidden()
    user = request.user
    return user.has_perm("manage_business", business)
    # is_maintainer = False
    # role = roles.MAINTAINERS
    # group_name = "%s\x00%s" % (cc_biz_id, role)
    # group = Group.objects.get(name=group_name)
    #
    # if user in group.user_set.all():
    #     is_maintainer = True
    # return is_maintainer
