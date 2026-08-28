from django.db import models
from django.conf import settings

from drugs.models import VerificationCode


class ScanLog(models.Model):
    class Result(models.TextChoices):
        AUTHENTIC = 'authentic', 'Authentic'
        INVALID_CODE = 'invalid_code', 'Invalid Code'
        EXPIRED = 'expired', 'Expired Drug'
        RECALLED = 'recalled', 'Recalled/Deactivated'
        SUSPICIOUS = 'suspicious', 'Suspicious (Excessive Scans)'

    code_entered = models.CharField(max_length=20)
    verification_code = models.ForeignKey(
        VerificationCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='scan_logs'
    )
    result = models.CharField(max_length=20, choices=Result.choices)
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location_hint = models.CharField(max_length=255, blank=True)  # optional, user-supplied city/state
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']
        indexes = [models.Index(fields=['code_entered']), models.Index(fields=['result'])]

    def __str__(self):
        return f"{self.code_entered} - {self.get_result_display()} @ {self.scanned_at:%Y-%m-%d %H:%M}"


class CounterfeitFlag(models.Model):
    """
    Raised automatically when a valid code is scanned an unusual number
    of times (a sign the physical code may have been cloned/printed on
    multiple fake packs), or manually by an officer.
    """
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        INVESTIGATING = 'investigating', 'Investigating'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'

    verification_code = models.ForeignKey(
        VerificationCode, on_delete=models.CASCADE, related_name='flags'
    )
    reason = models.TextField()
    scan_count_at_flag = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Null if raised automatically by the system"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Flag on {self.verification_code.code} ({self.get_status_display()})"




