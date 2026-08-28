from .models import Drug, DrugBatch, VerificationCode
from django.db.models import Q

def create_drug(manufacturer, form):
    drug = form.save(commit=False)
    drug.manufacturer = manufacturer
    drug.save()
    return drug


def create_batch_with_codes(drug, form):
    """Creates a batch and generates one verification code per unit produced."""
    batch = form.save(commit=False)
    batch.drug = drug
    batch.save()

    codes = [VerificationCode(batch=batch) for _ in range(batch.quantity_produced)]
    VerificationCode.objects.bulk_create(codes, batch_size=1000)
    return batch


def get_drugs_for_manufacturer(manufacturer):
    return Drug.objects.filter(manufacturer=manufacturer)


def get_batch_codes(batch):
    return batch.verification_codes.all()


def deactivate_batch_codes(batch, reason=''):
    """Used for recalls - invalidates every code tied to a batch."""
    return batch.verification_codes.update(is_active=False)


def search_drugs(query):
    return Drug.objects.filter(is_active=True).filter(
        models.Q(name__icontains=query) |
        models.Q(generic_name__icontains=query) |
        models.Q(nafdac_reg_number__icontains=query)
    ) if query else Drug.objects.none()





