from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        OFFICER = 'officer', 'NAFDAC Officer'
        MANUFACTURER = 'manufacturer', 'Manufacturer'
        CONSUMER = 'consumer', 'Public/Consumer'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONSUMER,
    )
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Superusers are always treated as admins in this system,
        # regardless of how the account was created (createsuperuser,
        # admin panel, shell, etc.)
        if self.is_superuser:
            self.role = self.Role.ADMIN
            self.is_verified = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_officer(self):
        return self.role == self.Role.OFFICER

    @property
    def is_manufacturer(self):
        return self.role == self.Role.MANUFACTURER

    @property
    def is_consumer(self):
        return self.role == self.Role.CONSUMER





