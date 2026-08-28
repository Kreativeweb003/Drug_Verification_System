from django import forms
from .models import Manufacturer


class ManufacturerProfileForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = [
            'company_name', 'registration_number', 'address', 'country',
            'contact_email', 'contact_phone', 'nafdac_license_number',
            'license_document', 'license_issue_date', 'license_expiry_date',
        ]
        widgets = {
            'license_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'license_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue = cleaned_data.get('license_issue_date')
        expiry = cleaned_data.get('license_expiry_date')
        if issue and expiry and expiry <= issue:
            raise forms.ValidationError("License expiry date must be after the issue date.")
        return cleaned_data


class LicenseReviewForm(forms.Form):
    STATUS_CHOICES = [
        ('approved', 'Approve'),
        ('suspended', 'Suspend'),
        ('revoked', 'Revoke'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)





