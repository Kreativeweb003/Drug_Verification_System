from django.contrib import admin
from .models import Drug, DrugBatch, VerificationCode


class DrugBatchInline(admin.TabularInline):
    model = DrugBatch
    extra = 0


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'nafdac_reg_number', 'manufacturer', 'dosage_form', 'is_active']
    list_filter = ['dosage_form', 'is_active']
    search_fields = ['name', 'generic_name', 'nafdac_reg_number']
    inlines = [DrugBatchInline]


@admin.register(DrugBatch)
class DrugBatchAdmin(admin.ModelAdmin):
    list_display = ['drug', 'batch_number', 'quantity_produced', 'manufacture_date', 'expiry_date']
    list_filter = ['manufacture_date', 'expiry_date']
    search_fields = ['batch_number', 'drug__name']


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'batch', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code']




