from django.contrib import admin

from relative.models import RelativeList, RelativeRequest


class RelativeListAdmin(admin.ModelAdmin):
    list_filter = ['users']
    list_display = ['users']
    search_fields = ['users']
    readonly_fields = ['users']

    class Meta:
        model = RelativeList


admin.site.register(RelativeList, RelativeListAdmin)


class RelativeRequestAdmin(admin.ModelAdmin):
    list_filter = ['senders', 'receivers']
    list_display = ['senders', 'receivers',]
    search_fields = ['senders__username', 'receivers__username']

    class Meta:
        model = RelativeRequest


admin.site.register(RelativeRequest, RelativeRequestAdmin)
