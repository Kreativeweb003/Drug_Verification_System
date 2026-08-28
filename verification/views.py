from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CodeVerificationForm
from .models import CounterfeitFlag
from . import services


def verify_view(request):
    """Public-facing verification page - no login required."""
    result = None
    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            ip_address = services.get_client_ip(request)
            result = services.verify_code(code, user=request.user, ip_address=ip_address)
    else:
        form = CodeVerificationForm()

    return render(request, 'verification/verify.html', {'form': form, 'result': result})


@login_required
def scan_history_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    logs = services.get_scan_history()
    return render(request, 'verification/scan_history.html', {'logs': logs})


@login_required
def flag_list_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    flags = services.get_open_flags()
    return render(request, 'verification/flag_list.html', {'flags': flags})


@login_required
def flag_resolve_view(request, pk):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    flag = get_object_or_404(CounterfeitFlag, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(CounterfeitFlag.Status.choices):
        services.resolve_flag(flag, new_status)
        messages.success(request, f"Flag marked as {flag.get_status_display()}.")
    return redirect('verification:flag_list')




