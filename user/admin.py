from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *


class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'fio',
        'phone',
        'date_joined',

    )
    ordering = ('id',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                "fio",
                "email",
                       'password1',
                       'password2',
                       ), }),)
    search_fields = ('id','login', 'fio', 'phone',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info',
         {'fields': (


                "fio",
                "phone",


         )}
         ),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups',)}),)


admin.site.register(User,UserAdmin)





