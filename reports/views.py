from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse

from .models import GeneratedReport
from . import services


@login_required
def dashboard_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    stats = services.get_dashboard_stats()
    top_flagged = services.get_top_flagged_drugs()
    scan_trend = services.get_scan_trend()
    return render(request, 'reports/dashboard.html', {
        'stats': stats,
        'top_flagged': top_flagged,
        'scan_trend': scan_trend,
    })


@login_required
def report_list_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    reports = GeneratedReport.objects.all()
    return render(request, 'reports/report_list.html', {'reports': reports})


@login_required
def generate_counterfeit_report_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    date_from = request.GET.get('date_from') or None
    date_to = request.GET.get('date_to') or None
    report = services.generate_counterfeit_summary_pdf(request.user, date_from, date_to)
    return redirect('reports:report_list')


@login_required
def generate_compliance_report_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    services.generate_manufacturer_compliance_pdf(request.user)
    return redirect('reports:report_list')


@login_required
def download_report_view(request, pk):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    report = get_object_or_404(GeneratedReport, pk=pk)
    return FileResponse(report.file.open('rb'), as_attachment=True, filename=report.file.name.split('/')[-1])






