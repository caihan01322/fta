# -*- coding: utf-8 -*-
"""BK user admin."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.forms import BkUserChangeForm, BkUserCreationForm
from account.models import BkUser


class BkUserAdmin(UserAdmin):
    """
    The forms to add and change user instances.

    The fields to be used in displaying the User model.
    These override the definitions on the base UserAdmin
    """

    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info', {'fields': ('chname', 'company')}),
        ('Contact info', {'fields': ('qq', 'phone', 'email')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',)}),
    )
    form = BkUserChangeForm
    add_form = BkUserCreationForm
    list_display = ('username', 'chname', 'company', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'chname', 'company')
    ordering = ('username',)


admin.site.register(BkUser, BkUserAdmin)
