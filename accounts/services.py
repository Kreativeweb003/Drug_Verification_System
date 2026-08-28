from django.contrib.auth import authenticate, login, logout
from .models import CustomUser


def register_user(form):
    """
    Creates a user from a validated RegistrationForm.
    Officer and Manufacturer accounts start unverified and require
    admin approval before they can access role-specific features.
    """
    user = form.save(commit=False)
    if user.role in (CustomUser.Role.OFFICER, CustomUser.Role.MANUFACTURER):
        user.is_verified = False
        user.is_active = True  # can log in, but restricted until verified
    else:
        user.is_verified = True
    user.save()
    return user


def authenticate_user(request, username, password):
    return authenticate(request, username=username, password=password)


def login_user(request, user):
    login(request, user)


def logout_user(request):
    logout(request)


def get_dashboard_redirect_url(user):
    """Central place to decide where a user lands after login."""
    if user.is_admin:
        return 'accounts:admin_dashboard'
    if user.is_officer:
        return 'accounts:officer_dashboard'
    if user.is_manufacturer:
        return 'accounts:manufacturer_dashboard'
    return 'accounts:consumer_dashboard'


def approve_user(user):
    user.is_verified = True
    user.save(update_fields=['is_verified'])
    return user





