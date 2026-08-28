import random
import string

from django.db import models
from django.conf import settings

from manufacturers.models import Manufacturer


class Drug(models.Model):
    class DosageForm(models.TextChoices):
        TABLET = 'tablet', 'Tablet'
        CAPSULE = 'capsule', 'Capsule'
        SYRUP = 'syrup', 'Syrup'
        INJECTION = 'injection', 'Injection'
        CREAM = 'cream', 'Cream/Ointment'
        OTHER = 'other', 'Other'

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='drugs')
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True)
    nafdac_reg_number = models.CharField(max_length=100, unique=True)
    dosage_form = models.CharField(max_length=20, choices=DosageForm.choices, default=DosageForm.TABLET)
    strength = models.CharField(max_length=100, help_text="e.g. 500mg")
    description = models.TextField(blank=True)
    active_ingredients = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)  # false if delisted/banned
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.nafdac_reg_number})"


class DrugBatch(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100)
    quantity_produced = models.PositiveIntegerField()
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-manufacture_date']
        unique_together = ['drug', 'batch_number']

    def __str__(self):
        return f"{self.drug.name} - Batch {self.batch_number}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()


def generate_verification_code():
    """Generates a unique 12-character alphanumeric code, grouped for readability."""
    chars = string.ascii_uppercase + string.digits
    raw = ''.join(random.choices(chars, k=12))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"


class VerificationCode(models.Model):
    """
    One unique code per physical unit/pack within a batch.
    Consumers verify authenticity by entering this code.
    """
    batch = models.ForeignKey(DrugBatch, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=20, unique=True, default=generate_verification_code)
    is_active = models.BooleanField(default=True)  # can be deactivated if compromised/recalled
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['code'])]

    def __str__(self):
        return self.code





