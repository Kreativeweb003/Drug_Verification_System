from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False, max_length=15)
    role = forms.ChoiceField(choices=CustomUser.Role.choices)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'role', 'password1', 'password2']

    def clean_role(self):
        role = self.cleaned_data['role']
        # Public self-registration should never grant admin
        if role == CustomUser.Role.ADMIN:
            raise forms.ValidationError("You cannot self-register as an administrator.")
        return role


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']




