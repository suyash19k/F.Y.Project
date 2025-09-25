# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome.")
            return redirect("dreams:dashboard")
    else:
        form = SignUpForm()
    # Use the unified template
    return render(request, "accounts/auth_form.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dreams:dashboard")
    else:
        form = AuthenticationForm()
    # Use the unified template
    return render(request, "accounts/auth_form.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")