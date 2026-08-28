from django.contrib import admin
from .models import Manufacturer, LicenseReviewLog


class LicenseReviewLogInline(admin.TabularInline):
    model = LicenseReviewLog
    extra = 0
    readonly_fields = ['reviewed_by', 'previous_status', 'new_status', 'remarks', 'reviewed_at']
    can_delete = False


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'nafdac_license_number', 'license_status', 'license_expiry_date']
    list_filter = ['license_status', 'country']
    search_fields = ['company_name', 'nafdac_license_number', 'registration_number']
    inlines = [LicenseReviewLogInline]


@admin.register(LicenseReviewLog)
class LicenseReviewLogAdmin(admin.ModelAdmin):
    list_display = ['manufacturer', 'previous_status', 'new_status', 'reviewed_by', 'reviewed_at']
    list_filter = ['new_status']




