from django import forms
from .admin import UserCreationForm, UserChangeForm
from .models import User, Employer, Employee, Assets
from .choices import EMPLOYEES_SIZE


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='enter your active email', 
                            widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(label='Password', 
                            widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(
        label='Password confirmation', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        }) 


class EmployerProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=255,
                        widget=forms.TextInput(attrs={'placeholder': 'Enter Full Name'}))
    company= forms.CharField(max_length=255,
                        widget=forms.TextInput(attrs={'placeholder': 'Company Name'}))
    role = forms.CharField(help_text='Your position in your company', max_length=255, 
                        widget=forms.TextInput(attrs={'placeholder': 'Your Role e.g Manager'}))
    phone =forms.CharField(max_length=20, 
                        widget=forms.TextInput(attrs={'placeholder': 'Phone No'}))
    no_employees= forms.ChoiceField(choices=EMPLOYEES_SIZE, help_text='Select size of your employees')

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
    def __init__(self, *args, **kwargs):
        super(EmployerProfileForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        })   
    
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
    
    def __init__(self, *args, **kwargs):
        super(LoginEmployer, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        })  

class EmployeeProfile(forms.ModelForm):
    dob = forms.DateField(input_formats=['%Y-%m-%d','%m/%d/%Y','%m/%d/%y'], 
                        label='Date of Birth',
                        help_text = 'date format is MM/DD/YY, eg 05/27/95' )
    national_id = forms.CharField(max_length=50, label="National ID", required=True)
    phone = forms.CharField(label='Phone No.', max_length=50, required=True)
    pin = forms.CharField(label='KRA Pin', max_length=20, required=True)
    class Meta:
        model = Employee
        fields = ('national_id', 'dob', 'phone', 'pin',)
      

# class EmployeeProfileForm(forms.ModelForm):
#     class Meta:
#         model =Employee
#         fields = ('name', 'national_id', 'dob', 'phone', 'pin')
        
class CreateEmployeeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', )
class CreateEmployeeNameForm(forms.ModelForm):
    name = forms.CharField(max_length=200, required=True)
    class Meta:
        model = Employee
        fields = ('name', )


class EmployeePasswordCreation(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class Create_and_Assign_AssetsForm(forms.ModelForm):
    title = forms.CharField(label="Name", max_length=100, required=True)
    slug = forms.CharField(label="Serial No.", max_length=100, help_text="optional", required=False)

    # def clean_employee(self):
    #     employee = self.cleaned_data.get('employee')
    #     if employee is None:
    #         return forms.ValidationError('Assign assets to somebody')
    #     return employee

    class Meta:

        model = Assets
        fields = ('employee', 'title', 'slug')

class UpdateRoleForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('role', )