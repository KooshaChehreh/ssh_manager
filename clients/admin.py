from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'is_active', 'traffic_used_display',
                    'traffic_limit_display', 'expire_date', 'sub_link', 'token')
    list_filter = ('is_active',)
    search_fields = ('name', 'username')
    filter_horizontal = ('servers',)
    readonly_fields = ('traffic_used', 'created_at', 'sub_link_display')

    def traffic_used_display(self, obj):
        return f"{obj.traffic_used_mb} MB"
    traffic_used_display.short_description = "مصرف"

    def traffic_limit_display(self, obj):
        return obj.traffic_limit_mb
    traffic_limit_display.short_description = "حد ترافیک"

    def sub_link(self, obj):
        return f"/sub/{obj.token}/"
    sub_link.short_description = "لینک ساب"

    def sub_link_display(self, obj):
        from django.utils.html import format_html
        link = f"/sub/{obj.token}/"
        return format_html('<a href="{}" target="_blank">{}</a>', link, link)
    
    sub_link_display.short_description = "لینک اشتراک"
