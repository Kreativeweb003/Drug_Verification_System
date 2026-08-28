from django.contrib import admin
from .models import ScanLog, CounterfeitFlag


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ['code_entered', 'result', 'scanned_by', 'ip_address', 'scanned_at']
    list_filter = ['result', 'scanned_at']
    search_fields = ['code_entered', 'ip_address']
    readonly_fields = [f.name for f in ScanLog._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(CounterfeitFlag)
class CounterfeitFlagAdmin(admin.ModelAdmin):
    list_display = ['verification_code', 'status', 'scan_count_at_flag', 'raised_by', 'created_at']
    list_filter = ['status']
    search_fields = ['verification_code__code']