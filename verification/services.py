from django.utils import timezone
from django.db.models import Count

from drugs.models import VerificationCode
from .models import ScanLog, CounterfeitFlag

# Number of scans on a single code within the window below that triggers
# an automatic suspicious-activity flag.
SUSPICIOUS_SCAN_THRESHOLD = 10
SUSPICIOUS_WINDOW_HOURS = 24


def verify_code(code_str, user=None, ip_address=None, location_hint=''):
    """
    Core verification logic. Returns a dict with the result, message,
    and related objects for the template to render.
    """
    try:
        verification_code = VerificationCode.objects.select_related(
            'batch__drug__manufacturer'
        ).get(code=code_str)
    except VerificationCode.DoesNotExist:
        _log_scan(code_str, None, ScanLog.Result.INVALID_CODE, user, ip_address, location_hint)
        return {
            'result': ScanLog.Result.INVALID_CODE,
            'message': 'This code was not found in our database. The drug may be counterfeit.',
        }

    batch = verification_code.batch
    drug = batch.drug

    if not verification_code.is_active:
        _log_scan(code_str, verification_code, ScanLog.Result.RECALLED, user, ip_address, location_hint)
        return {
            'result': ScanLog.Result.RECALLED,
            'message': 'This batch has been recalled or deactivated. Do not use this product.',
            'drug': drug,
            'batch': batch,
        }

    if batch.is_expired:
        _log_scan(code_str, verification_code, ScanLog.Result.EXPIRED, user, ip_address, location_hint)
        return {
            'result': ScanLog.Result.EXPIRED,
            'message': 'This drug has passed its expiry date. Do not use this product.',
            'drug': drug,
            'batch': batch,
        }

    scan_log = _log_scan(code_str, verification_code, ScanLog.Result.AUTHENTIC, user, ip_address, location_hint)
    flagged = _check_and_flag_suspicious_activity(verification_code)

    return {
        'result': ScanLog.Result.SUSPICIOUS if flagged else ScanLog.Result.AUTHENTIC,
        'message': (
            'Warning: this code has been scanned an unusually high number of times. '
            'It may have been duplicated. Please report your point of purchase.'
            if flagged else
            'This product is authentic and verified by NAFDAC.'
        ),
        'drug': drug,
        'batch': batch,
        'manufacturer': drug.manufacturer,
    }


def _log_scan(code_str, verification_code, result, user, ip_address, location_hint):
    return ScanLog.objects.create(
        code_entered=code_str,
        verification_code=verification_code,
        result=result,
        scanned_by=user if user and user.is_authenticated else None,
        ip_address=ip_address,
        location_hint=location_hint,
    )


def _check_and_flag_suspicious_activity(verification_code):
    """Auto-raises a CounterfeitFlag if scan volume in the recent window is abnormal."""
    window_start = timezone.now() - timezone.timedelta(hours=SUSPICIOUS_WINDOW_HOURS)
    recent_scan_count = ScanLog.objects.filter(
        verification_code=verification_code,
        scanned_at__gte=window_start,
    ).count()

    if recent_scan_count < SUSPICIOUS_SCAN_THRESHOLD:
        return False

    already_open = CounterfeitFlag.objects.filter(
        verification_code=verification_code, status=CounterfeitFlag.Status.OPEN
    ).exists()
    if not already_open:
        CounterfeitFlag.objects.create(
            verification_code=verification_code,
            reason=f"Auto-flagged: {recent_scan_count} scans within {SUSPICIOUS_WINDOW_HOURS}h.",
            scan_count_at_flag=recent_scan_count,
        )
    return True


def get_scan_history(limit=100):
    return ScanLog.objects.select_related('verification_code__batch__drug')[:limit]


def get_open_flags():
    return CounterfeitFlag.objects.filter(status=CounterfeitFlag.Status.OPEN).select_related(
        'verification_code__batch__drug'
    )


def resolve_flag(flag, new_status):
    flag.status = new_status
    if new_status in (CounterfeitFlag.Status.RESOLVED, CounterfeitFlag.Status.DISMISSED):
        flag.resolved_at = timezone.now()
    flag.save()
    return flag


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')



