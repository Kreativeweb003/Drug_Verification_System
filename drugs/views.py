from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import DrugForm, DrugBatchForm
from .models import Drug, DrugBatch
from . import services


@login_required
def drug_list_view(request):
    if request.user.is_manufacturer:
        if not hasattr(request.user, 'manufacturer_profile'):
            messages.info(request, "Complete your company profile before managing drugs.")
            return redirect('manufacturers:create_profile')
        manufacturer = request.user.manufacturer_profile
        drugs = services.get_drugs_for_manufacturer(manufacturer)
    else:
        drugs = Drug.objects.filter(is_active=True)
    return render(request, 'drugs/drug_list.html', {'drugs': drugs})

@login_required
def drug_create_view(request):
    if not request.user.is_manufacturer:
        return redirect('accounts:login')
    if not hasattr(request.user, 'manufacturer_profile'):
        messages.info(request, "Complete your company profile before registering drugs.")
        return redirect('manufacturers:create_profile')
    manufacturer = request.user.manufacturer_profile
    if not manufacturer.is_license_active:
        messages.error(request, "Your NAFDAC license must be approved and active before registering drugs.")
        return redirect('manufacturers:profile_detail')
    ...

@login_required
def drug_detail_view(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    batches = drug.batches.all()
    return render(request, 'drugs/drug_detail.html', {'drug': drug, 'batches': batches})


@login_required
def batch_create_view(request, drug_pk):
    drug = get_object_or_404(Drug, pk=drug_pk)
    if not (request.user.is_manufacturer and drug.manufacturer.user == request.user):
        return redirect('accounts:login')

    if request.method == 'POST':
        form = DrugBatchForm(request.POST)
        if form.is_valid():
            batch = services.create_batch_with_codes(drug, form)
            messages.success(
                request,
                f"Batch {batch.batch_number} created with {batch.quantity_produced} verification codes."
            )
            return redirect('drugs:batch_detail', pk=batch.pk)
    else:
        form = DrugBatchForm()
    return render(request, 'drugs/batch_form.html', {'form': form, 'drug': drug})


@login_required
def batch_detail_view(request, pk):
    batch = get_object_or_404(DrugBatch, pk=pk)
    if not (
        request.user.is_admin or request.user.is_officer
        or (request.user.is_manufacturer and batch.drug.manufacturer.user == request.user)
    ):
        return redirect('accounts:login')
    codes = services.get_batch_codes(batch)
    return render(request, 'drugs/batch_detail.html', {'batch': batch, 'codes': codes})


@login_required
def batch_recall_view(request, pk):
    batch = get_object_or_404(DrugBatch, pk=pk)
    if not (request.user.is_admin or request.user.is_officer):
        return redirect('accounts:login')
    services.deactivate_batch_codes(batch)
    messages.warning(request, f"All codes for batch {batch.batch_number} have been deactivated.")
    return redirect('drugs:batch_detail', pk=batch.pk)


def public_drug_search_view(request):
    query = request.GET.get('q', '')
    drugs = services.search_drugs(query)
    return render(request, 'drugs/public_search.html', {'drugs': drugs, 'query': query})




