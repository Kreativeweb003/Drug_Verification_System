from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ManufacturerProfileForm, LicenseReviewForm
from .models import Manufacturer
from . import services


@login_required
def create_profile_view(request):
    if not request.user.is_manufacturer:
        return redirect('accounts:login')
    if hasattr(request.user, 'manufacturer_profile'):
        return redirect('manufacturers:profile_detail')

    if request.method == 'POST':
        form = ManufacturerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            services.create_manufacturer_profile(request.user, form)
            messages.success(request, "Profile submitted. Awaiting NAFDAC review.")
            return redirect('manufacturers:profile_detail')
    else:
        form = ManufacturerProfileForm()
    return render(request, 'manufacturers/create_profile.html', {'form': form})


@login_required
def profile_detail_view(request):
    if not request.user.is_manufacturer:
        return redirect('accounts:login')
    manufacturer = get_object_or_404(Manufacturer, user=request.user)
    return render(request, 'manufacturers/profile_detail.html', {'manufacturer': manufacturer})


@login_required
def edit_profile_view(request):
    if not request.user.is_manufacturer:
        return redirect('accounts:login')
    manufacturer = get_object_or_404(Manufacturer, user=request.user)

    if request.method == 'POST':
        form = ManufacturerProfileForm(request.POST, request.FILES, instance=manufacturer)
        if form.is_valid():
            services.update_manufacturer_profile(manufacturer, form)
            messages.success(request, "Profile updated. Re-submitted for review.")
            return redirect('manufacturers:profile_detail')
    else:
        form = ManufacturerProfileForm(instance=manufacturer)
    return render(request, 'manufacturers/edit_profile.html', {'form': form})


@login_required
def manufacturer_list_view(request):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    manufacturers = Manufacturer.objects.all()
    return render(request, 'manufacturers/manufacturer_list.html', {'manufacturers': manufacturers})


@login_required
def manufacturer_review_view(request, pk):
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    manufacturer = get_object_or_404(Manufacturer, pk=pk)

    if request.method == 'POST':
        form = LicenseReviewForm(request.POST)
        if form.is_valid():
            services.review_license(
                manufacturer,
                reviewer=request.user,
                new_status=form.cleaned_data['status'],
                remarks=form.cleaned_data['remarks'],
            )
            messages.success(request, f"{manufacturer.company_name} status updated.")
            return redirect('manufacturers:manufacturer_list')
    else:
        form = LicenseReviewForm()
    return render(request, 'manufacturers/manufacturer_review.html', {
        'manufacturer': manufacturer,
        'form': form,
    })




