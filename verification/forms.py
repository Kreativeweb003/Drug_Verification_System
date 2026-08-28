from django import forms


class CodeVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. AB12-CD34-EF56',
            'autofocus': True,
        }),
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        return code