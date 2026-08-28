from django.utils import timezone
from .models import Manufacturer, LicenseReviewLog


def create_manufacturer_profile(user, form):
    """Creates a Manufacturer profile tied to a manufacturer-role user."""
    manufacturer = form.save(commit=False)
    manufacturer.user = user
    manufacturer.license_status = Manufacturer.LicenseStatus.PENDING
    manufacturer.save()
    return manufacturer


def update_manufacturer_profile(manufacturer, form):
    manufacturer = form.save(commit=False)
    # Editing details after approval re-opens review, since core details changed
    if manufacturer.license_status == Manufacturer.LicenseStatus.APPROVED:
        manufacturer.license_status = Manufacturer.LicenseStatus.PENDING
    manufacturer.save()
    return manufacturer


def review_license(manufacturer, reviewer, new_status, remarks=''):
    """Applies an admin/officer decision and logs it for audit purposes."""
    previous_status = manufacturer.license_status
    manufacturer.license_status = new_status
    manufacturer.save(update_fields=['license_status', 'updated_at'])

    LicenseReviewLog.objects.create(
        manufacturer=manufacturer,
        reviewed_by=reviewer,
        previous_status=previous_status,
        new_status=new_status,
        remarks=remarks,
    )
    return manufacturer


def get_expiring_licenses(days=30):
    """Manufacturers whose license expires within the given window - for alerts."""
    cutoff = timezone.now().date() + timezone.timedelta(days=days)
    return Manufacturer.objects.filter(
        license_status=Manufacturer.LicenseStatus.APPROVED,
        license_expiry_date__lte=cutoff,
        license_expiry_date__gte=timezone.now().date(),
    )


def get_pending_manufacturers():
    return Manufacturer.objects.filter(license_status=Manufacturer.LicenseStatus.PENDING)




