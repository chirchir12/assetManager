from django import forms
from .admin import UserCreationForm
from .models import User, Employer


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',)


class EmployerProfileForm(forms.ModelForm):
    name = forms.CharField(help_text='Enter your Full name', max_length=255)
    company= forms.CharField(help_text='The name of your company', max_length=255)
    role = forms.CharField(help_text='Your position in your company', max_length=255)
    phone =forms.CharField(help_text='Your phone number', max_length=20)
    no_employees= forms.CharField(help_text='select number of employees', max_length=20)

    class Meta:
        model = Employer
        fields = ('name', 'company', 'role', 'phone', 'no_employees')
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('name is required')
        return name

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            raise forms.ValidationError('Company is required')
        return company
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError('role is required')
        return role
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError('phone is required')
        return phone
    
class LoginEmployer(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(), required=True)
    password =forms.CharField(widget=forms.PasswordInput(), required=True)
    class Meta:
        model= User
        fields=('email', 'password', )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('email is required')
        return email

