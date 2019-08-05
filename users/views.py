from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.db import transaction
from django.shortcuts import render, redirect
from .models import User

from .forms import CreateUserForm, EmployerProfileForm, LoginEmployer
from .tokens import account_activation_token
from .decorators import employer_required

@transaction.atomic
def registerEmployer(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        profileForm = EmployerProfileForm(request.POST)
        if user_form.is_valid() and profileForm.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()
            user.refresh_from_db()
            profileForm = EmployerProfileForm(request.POST, instance=user.employer)
            profileForm.full_clean()
            profileForm.save()

            # email user 
            current_site = get_current_site(request)
            subject = "Activate Your Account"
            message = render_to_string(
                'users/account_activation.html',
                {
                    'user':user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
            )
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        user_form = CreateUserForm()
        profileForm = EmployerProfileForm()
    return render(request, 'users/employerSignup.html', {
        'user_form':user_form,
        'employer_profile_form':profileForm
    })

def account_activation_sent(request):
    return render(request, 'users/account_activation_sent.html', {})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.employer.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'account_activation_invalid.html')

@employer_required()
def employer_dashboard_view(request):
    return render(request, 'users/employerDashboard.html', {'title':"Employer Dashboard"})


def employer_login_view(request):
    if request.method=='POST':
        login_form = LoginEmployer(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password=login_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        login_form = LoginEmployer(request.POST)
    return render(request, 'users/employerLogin.html', {
        'form':login_form
    })

def logout_employer_view(request):
    logout(request)
    return redirect('employerLogin')