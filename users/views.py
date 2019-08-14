from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from .models import User, Employee, Assets, Notifications
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.detail import DetailView
import datetime

from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.core import serializers

from . import pusher 

from .forms import (
    CreateUserForm,
    EmployerProfileForm,
    LoginEmployer,
    CreateEmployeeEmailForm,
    CreateEmployeeNameForm,
    EmployeePasswordCreation,
    Create_and_Assign_AssetsForm,
    EmployeeProfile, 
    UpdateRoleForm
)
from .tokens import account_activation_token
from .decorators import employer_required, employee_required


"""
pusher init

"""
pusher = pusher.connect()



def index_view(request):
    return render(request, 'index.html', {})


@transaction.atomic
def registerEmployer(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        profileForm = EmployerProfileForm(request.POST)
        if user_form.is_valid() and profileForm.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.is_employer = True
            user.save()
            user.refresh_from_db()
            profileForm = EmployerProfileForm(
                request.POST, instance=user.employer)
            profileForm.full_clean()
            profileForm.save()

            # email user
            current_site = get_current_site(request)
            subject = "Activate Your Account"
            message = render_to_string(
                'users/account_activation.html',
                {
                    'user': user,
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
        'user_form': user_form,
        'employer_profile_form': profileForm
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
        user.save()
        if user.is_employer:
            login(request, user)
            return redirect('employerdashboard')
        elif user.is_employee:
            return redirect('createpassword')
    else:
        return render(request, 'account_activation_invalid.html')



@transaction.atomic
@login_required(login_url='login')
@employer_required()
def createEmployee_view(request):
    if request.method == "POST":
        user_email = CreateEmployeeEmailForm(request.POST)
        user_name  = CreateEmployeeNameForm(request.POST)
        if user_email.is_valid() and user_name.is_valid():
            user = user_email.save(commit=False)
            user.is_active = False
            user.is_employee = True
            user.save()
            user.refresh_from_db()
            user_name = CreateEmployeeNameForm(request.POST, instance=user.employee)
            user_name.full_clean()
            user_name.save()
            

            current_site = get_current_site(request)
            name = user_name.cleaned_data['name']
            subject = f" Hello {name} Please Activate your Account"
            message = render_to_string(
                'users/account_activation.html',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
            )
            user.email_user(subject, message)
            messages.success(request, 'Employee has been added Successfully!!')
            return redirect('createEmployee')
    else:
        user_email = CreateEmployeeEmailForm()
        user_name  = CreateEmployeeNameForm()
    return render(request, 'users/createEmployee.html', {
        'email_form': user_email,
        'name_form':user_name
    })


def Employee_Update_pass_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        instance  = User.objects.get(email=email)
        form = EmployeePasswordCreation(request.POST, instance=instance)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('update_profile')
    else:
        form = EmployeePasswordCreation()
    return render(request, 'users/createPassword.html', {'form':form})

    

def employer_login_view(request):
    user = request.user
    if user.is_authenticated:
        if user.is_employer:
            return redirect('employerdashboard')
        elif user.is_employee:
            return redirect('employeedashboard')

    if request.method == 'POST':
        login_form = LoginEmployer(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            print(user)
            
            if user is not None:
                login(request, user)
                if user.is_employer:
                    return redirect('employerdashboard')
                elif user.is_employee:
                    # 
                    message = f'{request.user.employee.name} logged in'
                    data = {'message':message}
                    
                    # trigger event 
                    pusher.trigger('my-channel', 'an-event', data)
                    notify = Notifications.objects.create(message=message, user =request.user)
                    notify.save()
                    return redirect('employeedashboard')

    else:
        login_form = LoginEmployer(request.POST)
    return render(request, 'users/employerLogin.html', {
        'form': login_form
    })


def logout_employer_view(request):
    
    if request.user.is_employee:
        message = f'{request.user.employee.name} logged out'
        data = {'message':message}
        
        # trigger event 
        pusher.trigger('my-channel', 'an-event', data)
        notify = Notifications.objects.create(message=message, user =request.user)
        notify.save()
        logout(request)
    return redirect('login')


@login_required(login_url='login')
@employer_required()
def employer_dashboard_view(request):
    return render(request, 'users/employerDashboard.html', {'title': "Employer Dashboard"})


@login_required(login_url='login')
@employee_required()
def employee_dashboard_view(request):
    return render(request, 'users/employeeDashboard.html', {'title': "Employee Dashboard"})

@login_required(login_url='login')
@employer_required()
def employees_List_view(request):
    employees = Employee.objects.all()
    context = {
        'employees':employees
    }
    return render(request, 'users/employeesList.html', context)

@login_required(login_url='login')
@employer_required()
def assets_List_view(request):
    assets = Assets.objects.all()
   
    context = {
        'assets':assets
    }
    return render(request, 'users/assetsList.html', context)

@login_required(login_url='login')
@employer_required()
def addAndAssignAssetView(request):
    if request.method == 'POST':
        form = Create_and_Assign_AssetsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset assigned Successfully!!')
            return redirect('addAsset')
    else:
        form = Create_and_Assign_AssetsForm()
    return render(request, 'users/createAsset.html', {'form':form})


@login_required(login_url='login')
@employee_required()
def assigned_assets(request):
    user = Employee.objects.get(user=request.user)
    print(user)
    myAssets = Assets.objects.filter(employee=user)
    print(myAssets)

    return render(request, 'users/assets_assigned_to_employee.html', {'assets':myAssets})

    
@login_required(login_url='login')
@employee_required()
def update_profile_view(request):
    instance = Employee.objects.get(user=request.user)
    if request.method == "POST":
        form = EmployeeProfile(request.POST, instance=instance)
        if form.is_valid():
            user =form.save()
            if user is not None:
                message = f'{request.user.employee.name} updated Profile'
                data = {'message':message}
                
                # trigger event 
                pusher.trigger('my-channel', 'an-event', data)
                notify = Notifications.objects.create(message=message, user =request.user)
                notify.save()
                messages.success(request, 'Profile Updated Successfully')
                return redirect('check_profile')
            else:
                form = EmployeeProfile(instance=instance)


    else:
        form = EmployeeProfile(instance=instance)
    return render(request, 'users/update_profile.html', {'form':form})

class UserProfileDetailView(DetailView):
    model = Employee
    template_name = 'users/checkProfile.html'
    def get_object(self):
        user = self.request.user
        return get_object_or_404(Employee, user=user)
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class UpdateRole(UpdateView):
    '''
    Role Update view
    '''
    model = Employee
    form_class = UpdateRoleForm
    template_name = 'users/update_role.html'
	

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):        
        form.save()  
        return super().form_valid(form)
    def get_success_url(self):
        messages.success(self.request, 'Role Updated Successfully')
        return reverse('employeeList')


class DeleteEmployee(DeleteView):
    model = Employee
    template_name = 'users/delete.html'


    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Employee Deleted Successfully')
        return reverse_lazy('employeeList')
    
def notifications(request):
    try:
        notif = Notifications.objects.order_by('-created_at')[:8]
        newMessage = Notifications.objects.order_by('-created_at')[:1]
    except:
        raise Http404("Zero activity")
    context = {
        "notify":notif,
        'new':newMessage
    }
    return render(request, 'users/notification.html', context)