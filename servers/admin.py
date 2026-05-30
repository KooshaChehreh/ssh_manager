from django.contrib import admin
from .models import Server


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'host_key', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'host')
