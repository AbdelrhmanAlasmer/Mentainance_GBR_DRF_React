from django.contrib import admin
from .models import Reception, ReceptionPhoto, Call, RepairNote
from django.utils.html import format_html
from django.urls import reverse

class ReceptionPhotoInline(admin.TabularInline):
    model = ReceptionPhoto
    extra = 1
    readonly_fields = ['photo_preview']
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="100" />', obj.photo.url)
        return "-"
    photo_preview.short_description = 'Preview'

class CallInline(admin.TabularInline):
    model = Call
    extra = 0
    readonly_fields = ['datetime', 'caller']
    fields = ['datetime', 'call_type', 'caller', 'summary', 'follow_up_required']
    
    def has_add_permission(self, request, obj=None):
        return True

class RepairNoteInline(admin.TabularInline):
    model = RepairNote
    extra = 0
    readonly_fields = ['created_at', 'author']
    
    def has_add_permission(self, request, obj=None):
        return True

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = [
        'case_number', 
        'customer_link', 
        'tv_link', 
        'status', 
        'current_place',
        'priority',
        'initial_cost',
        'final_cost',
        'days_in_system'
    ]
    list_filter = [
        'status',
        'current_place',
        'priority',
        'in_guarantee',
        'have_guarantee',
        'receptionist',
        'check_tv_eng',
        'maintenance_eng'
    ]
    search_fields = [
        'case_number',
        'customer__name',
        'tv__serial_number',
        'initial_damage'
    ]
    readonly_fields = [
        'case_number',
        'status',
        'days_in_system',
        'receptionist',
        'check_tv_eng',
        'check_feedback_eng',
        'maintenance_eng',
        'given_to_customer_receptionist',
        'the_date',  # Added as readonly since it's auto_now_add
        'reception_photos_preview'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'case_number',
                ('customer', 'tv'),
                ('status', 'current_place', 'priority'),
                'initial_damage',
                'reception_photos_preview'
            )
        }),
        ('Financial Information', {
            'fields': (
                ('initial_tax', 'initial_cost', 'final_cost'),
                ('in_guarantee', 'have_guarantee', 'warranty_expiry_date')
            )
        }),
        ('Timeline', {
            'fields': (
                'the_date',  # Now properly included as readonly
                ('check_tv_date', 'check_feedback_date'),
                ('maintenance_date', 'expected_completion_date'),
                'given_to_customer_date'
            )
        }),
        ('Personnel', {
            'fields': (
                ('receptionist', 'who_receive_it'),
                ('check_tv_eng', 'check_feedback_eng'),
                ('maintenance_eng', 'given_to_customer_receptionist')
            )
        }),
        ('Technical Details', {
            'fields': (
                'check_feedback_description',
                'damage_full_description',
                'refused_reason'
            )
        }),
        ('Delivery Information', {
            'fields': (
                'how_actually_take_it',
                'notes'
            )
        })
    )
    inlines = [ReceptionPhotoInline, CallInline, RepairNoteInline]
    date_hierarchy = 'the_date'
    ordering = ['-the_date']
    actions = ['mark_as_completed', 'mark_as_refused']

    def customer_link(self, obj):
        url = reverse("admin:customers_customer_change", args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer__name'

    def tv_link(self, obj):
        url = reverse("admin:tvs_tv_change", args=[obj.tv.id])
        return format_html('<a href="{}">{}</a>', url, obj.tv.serial_number)
    tv_link.short_description = 'TV'
    tv_link.admin_order_field = 'tv__serial_number'

    def reception_photos_preview(self, obj):
        photos = obj.reception_photos.all()
        if photos:
            return format_html(
                ''.join(f'<img src="{photo.photo.url}" height="100" style="margin-right: 10px;" />' for photo in photos)
            )
        return "-"
    reception_photos_preview.short_description = 'Photos Preview'

    def days_in_system(self, obj):
        from django.utils import timezone
        if obj.given_to_customer_date:
            delta = obj.given_to_customer_date - obj.the_date
        else:
            delta = timezone.now() - obj.the_date
        return delta.days
    days_in_system.short_description = 'Days in System'

    def mark_as_completed(self, request, queryset):
        queryset.update(status='given_to_customer', current_place='customer')
    mark_as_completed.short_description = "Mark selected as completed"

    def mark_as_refused(self, request, queryset):
        queryset.update(status='refused_or_not_accept', current_place='reception')
    mark_as_refused.short_description = "Mark selected as refused"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Technicians').exists():
            return qs.filter(maintenance_eng=request.user)
        if request.user.groups.filter(name='Receptionists').exists():
            return qs.filter(receptionist=request.user)
        return qs

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ['reception_link', 'call_type', 'caller', 'datetime', 'follow_up_required']
    list_filter = ['call_type', 'follow_up_required', 'caller', 'datetime']
    search_fields = ['reception__case_number', 'summary']
    readonly_fields = ['caller', 'datetime']

    def reception_link(self, obj):
        url = reverse("admin:receptions_reception_change", args=[obj.reception.id])
        return format_html('<a href="{}">{}</a>', url, obj.reception.case_number)
    reception_link.short_description = 'Reception'
    reception_link.admin_order_field = 'reception__case_number'

@admin.register(RepairNote)
class RepairNoteAdmin(admin.ModelAdmin):
    list_display = ['reception_link', 'author', 'created_at', 'short_note']
    list_filter = ['author', 'created_at']
    search_fields = ['reception__case_number', 'note']
    readonly_fields = ['author', 'created_at']

    def reception_link(self, obj):
        url = reverse("admin:receptions_reception_change", args=[obj.reception.id])
        return format_html('<a href="{}">{}</a>', url, obj.reception.case_number)
    reception_link.short_description = 'Reception'
    reception_link.admin_order_field = 'reception__case_number'

    def short_note(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    short_note.short_description = 'Note'

@admin.register(ReceptionPhoto)
class ReceptionPhotoAdmin(admin.ModelAdmin):
    list_display = ['reception_link', 'photo_preview', 'description']
    readonly_fields = ['photo_preview']

    def reception_link(self, obj):
        url = reverse("admin:receptions_reception_change", args=[obj.reception.id])
        return format_html('<a href="{}">{}</a>', url, obj.reception.case_number)
    reception_link.short_description = 'Reception'
    reception_link.admin_order_field = 'reception__case_number'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="100" />', obj.photo.url)
        return "-"
    photo_preview.short_description = 'Preview'