import io
from django.utils import timezone
from django.db.models import Count, Q
from django.core.files.base import ContentFile

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from verification.models import ScanLog, CounterfeitFlag
from manufacturers.models import Manufacturer
from drugs.models import Drug, DrugBatch
from .models import GeneratedReport


# ---------- Dashboard analytics (no PDF, just numbers for templates) ----------

def get_dashboard_stats():
    total_scans = ScanLog.objects.count()
    result_breakdown = ScanLog.objects.values('result').annotate(count=Count('id'))
    open_flags = CounterfeitFlag.objects.filter(status=CounterfeitFlag.Status.OPEN).count()
    total_manufacturers = Manufacturer.objects.count()
    approved_manufacturers = Manufacturer.objects.filter(
        license_status=Manufacturer.LicenseStatus.APPROVED
    ).count()
    total_drugs = Drug.objects.filter(is_active=True).count()
    total_batches = DrugBatch.objects.count()

    return {
        'total_scans': total_scans,
        'result_breakdown': list(result_breakdown),
        'open_flags': open_flags,
        'total_manufacturers': total_manufacturers,
        'approved_manufacturers': approved_manufacturers,
        'total_drugs': total_drugs,
        'total_batches': total_batches,
    }


def get_top_flagged_drugs(limit=10):
    return (
        CounterfeitFlag.objects
        .values('verification_code__batch__drug__name')
        .annotate(flag_count=Count('id'))
        .order_by('-flag_count')[:limit]
    )


def get_scan_trend(days=30):
    """Daily scan counts for the last N days - useful for a line chart."""
    cutoff = timezone.now() - timezone.timedelta(days=days)
    logs = ScanLog.objects.filter(scanned_at__gte=cutoff)
    trend = (
        logs.extra(select={'day': "date(scanned_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    return list(trend)


def get_manufacturer_compliance_data():
    return Manufacturer.objects.annotate(
        drug_count=Count('drugs', distinct=True),
        flagged_count=Count(
            'drugs__batches__verification_codes__flags',
            filter=Q(drugs__batches__verification_codes__flags__status=CounterfeitFlag.Status.OPEN),
            distinct=True,
        ),
    )


# ---------- PDF generation ----------

def generate_counterfeit_summary_pdf(user, date_from=None, date_to=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("NAFDAC Counterfeit Drug Summary Report", styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    period = f"{date_from or 'All time'} to {date_to or timezone.now().date()}"
    elements.append(Paragraph(f"Reporting period: {period}", styles['Normal']))
    elements.append(Spacer(1, 1*cm))

    flags_qs = CounterfeitFlag.objects.select_related('verification_code__batch__drug__manufacturer')
    if date_from:
        flags_qs = flags_qs.filter(created_at__date__gte=date_from)
    if date_to:
        flags_qs = flags_qs.filter(created_at__date__lte=date_to)

    data = [['Drug', 'Manufacturer', 'Batch', 'Code', 'Status', 'Date Raised']]
    for flag in flags_qs:
        vc = flag.verification_code
        data.append([
            vc.batch.drug.name,
            vc.batch.drug.manufacturer.company_name,
            vc.batch.batch_number,
            vc.code,
            flag.get_status_display(),
            flag.created_at.strftime('%Y-%m-%d'),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5632')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Total flags in period: {flags_qs.count()}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    report = GeneratedReport.objects.create(
        report_type=GeneratedReport.ReportType.COUNTERFEIT_SUMMARY,
        generated_by=user,
        date_from=date_from,
        date_to=date_to,
    )
    report.file.save(f"counterfeit_summary_{report.id}.pdf", ContentFile(buffer.read()))
    return report


def generate_manufacturer_compliance_pdf(user):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Manufacturer Compliance Report", styles['Title']), Spacer(1, 1*cm)]

    data = [['Company', 'NAFDAC License', 'Status', 'Drugs Registered', 'Open Flags']]
    for m in get_manufacturer_compliance_data():
        data.append([
            m.company_name,
            m.nafdac_license_number,
            m.get_license_status_display(),
            str(m.drug_count),
            str(m.flagged_count),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5632')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    report = GeneratedReport.objects.create(
        report_type=GeneratedReport.ReportType.MANUFACTURER_COMPLIANCE,
        generated_by=user,
    )
    report.file.save(f"manufacturer_compliance_{report.id}.pdf", ContentFile(buffer.read()))
    return report




