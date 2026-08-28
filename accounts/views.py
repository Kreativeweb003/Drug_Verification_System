from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import RegistrationForm, LoginForm, ProfileUpdateForm
from .models import CustomUser
from . import services


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = services.register_user(form)
            messages.success(request, "Registration successful. You may now log in.")
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            services.login_user(request, user)
            redirect_url = services.get_dashboard_redirect_url(user)
            return redirect(redirect_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    services.logout_user(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('accounts:login')
    pending_users = CustomUser.objects.filter(
        role__in=[CustomUser.Role.OFFICER, CustomUser.Role.MANUFACTURER],
        is_verified=False,
    )
    return render(request, 'accounts/admin_dashboard.html', {'pending_users': pending_users})


@login_required
def officer_dashboard(request):
    if not request.user.is_officer:
        return redirect('accounts:login')
    return render(request, 'accounts/officer_dashboard.html')


@login_required
def manufacturer_dashboard(request):
    if not request.user.is_manufacturer:
        return redirect('accounts:login')
    return render(request, 'accounts/manufacturer_dashboard.html')


@login_required
def consumer_dashboard(request):
    return render(request, 'accounts/consumer_dashboard.html')


@login_required
def approve_user_view(request, user_id):
    if not request.user.is_admin:
        return redirect('accounts:login')
    user = get_object_or_404(CustomUser, id=user_id)
    services.approve_user(user)
    messages.success(request, f"{user.username} has been verified.")
    return redirect('accounts:admin_dashboard')





