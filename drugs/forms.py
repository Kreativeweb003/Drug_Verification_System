from django import forms
from .models import Drug, DrugBatch


class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = [
            'name', 'generic_name', 'nafdac_reg_number', 'dosage_form',
            'strength', 'description', 'active_ingredients',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'active_ingredients': forms.Textarea(attrs={'rows': 2}),
        }


class DrugBatchForm(forms.ModelForm):
    class Meta:
        model = DrugBatch
        fields = ['batch_number', 'quantity_produced', 'manufacture_date', 'expiry_date']
        widgets = {
            'manufacture_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        manufacture_date = cleaned_data.get('manufacture_date')
        expiry_date = cleaned_data.get('expiry_date')
        if manufacture_date and expiry_date and expiry_date <= manufacture_date:
            raise forms.ValidationError("Expiry date must be after the manufacture date.")
        quantity = cleaned_data.get('quantity_produced')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity produced must be greater than zero.")
        return cleaned_data






