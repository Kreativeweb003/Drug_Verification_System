from django.db import models
from django.conf import settings


class Manufacturer(models.Model):
    class LicenseStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        SUSPENDED = 'suspended', 'Suspended'
        REVOKED = 'revoked', 'Revoked'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='manufacturer_profile',
        limit_choices_to={'role': 'manufacturer'},
    )
    company_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)  # CAC number
    address = models.TextField()
    country = models.CharField(max_length=100, default='Nigeria')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)

    nafdac_license_number = models.CharField(max_length=100, unique=True)
    license_document = models.FileField(upload_to='manufacturer_licenses/')
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()
    license_status = models.CharField(
        max_length=20,
        choices=LicenseStatus.choices,
        default=LicenseStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company_name']

    def __str__(self):
        return f"{self.company_name} ({self.nafdac_license_number})"

    @property
    def is_license_active(self):
        from django.utils import timezone
        return (
            self.license_status == self.LicenseStatus.APPROVED
            and self.license_expiry_date >= timezone.now().date()
        )


class LicenseReviewLog(models.Model):
    """Audit trail of admin/officer decisions on a manufacturer's license."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='review_logs')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reviewed_at']

    def __str__(self):
        return f"{self.manufacturer.company_name}: {self.previous_status} → {self.new_status}"






