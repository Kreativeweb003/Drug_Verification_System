from django.db import models
from django.conf import settings


class GeneratedReport(models.Model):
    """
    Audit record of reports produced by the system (e.g. monthly counterfeit
    summary, manufacturer compliance report). The actual PDF is generated
    on demand by services.py; this model just tracks who requested what.
    """
    class ReportType(models.TextChoices):
        COUNTERFEIT_SUMMARY = 'counterfeit_summary', 'Counterfeit Summary'
        MANUFACTURER_COMPLIANCE = 'manufacturer_compliance', 'Manufacturer Compliance'
        SCAN_ACTIVITY = 'scan_activity', 'Scan Activity'
        EXPIRING_LICENSES = 'expiring_licenses', 'Expiring Licenses'

    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='generated_reports/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.generated_at:%Y-%m-%d}"



