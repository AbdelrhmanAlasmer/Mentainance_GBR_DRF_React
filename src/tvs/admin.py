from django.contrib import admin
from .models import TVType, TVModel, TV

@admin.register(TVType)
class TVTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(TVModel)
class TVModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type')
    search_fields = ('name', 'type__name')
    list_filter = ('type',)
    ordering = ('type', 'name')

@admin.register(TV)
class TVAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'type', 'model', 'status', 'get_status_display')
    search_fields = ('serial_number', 'type__name', 'model__name')
    list_filter = ('status', 'type', 'model')
    ordering = ('type', 'model', 'serial_number')
    list_select_related = ('type', 'model')

    # This will show the human-readable status in the list display
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Status'