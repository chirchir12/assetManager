from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse 
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .utils import unique_slug_generator

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from .choices import EMPLOYEES_SIZE


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_employer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# employer model
class Employer(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(_('Enter your Fullname'), max_length=255)
    company = models.CharField(_('The name of your company'), max_length=255)
    role = models.CharField(_('Your position in your company'), max_length=255)
    phone = models.CharField(_('Your phone number'), max_length=20)
    no_employees = models.CharField(
        _('select number of employees'), max_length = 20, choices=EMPLOYEES_SIZE, default=0)
    email_confirmed=models.BooleanField(default = False)

    objects=models.Manager()

    def __str__(self):
        return self.company





# employee model
class Employee(models.Model):
    user=models.OneToOneField(User, on_delete = models.CASCADE)
    name=models.CharField(_('Enter your fullname'),
                            max_length = 200, blank = True, null = True)
    national_id=models.CharField(
        _('Enter your ID'), null = True, blank = True, max_length = 20)
    dob=models.DateField(_('Date of birth'), null = True, blank = True)
    phone=models.CharField(_('Enter your Phone number'),
                             max_length = 20, null = True, blank = True)
    pin=models.CharField(_('Enter your KRA Pin'),
                           max_length = 100, null = True, blank = True)
    role=models.CharField(_('Employee role'), null = True,
                            blank = True, max_length = 255)
    email_confirmed=models.BooleanField(default = False)

    objects=models.Manager()


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('update_role', kwargs={'pk': self.pk})



# assets model
class Assets(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    title=models.CharField(max_length = 100)
    slug=models.SlugField(unique=True, blank=True)

    objects=models.Manager()

    def __str__(self):
        return self.title




class Notifications(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.CharField(max_length=225)
    created_at=models.DateTimeField(auto_now=True)
    objects = models.Manager()







# signals
@receiver(post_save, sender = User)
def create_Profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_employer:
            Employer.objects.create(user = instance)
        elif instance.is_employee:
            Employee.objects.create(user = instance)


def asset_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(asset_pre_save_receiver, sender=Assets)

@receiver(post_delete, sender = Employee)
def delete_user(sender, instance, **kwargs):
    user = instance.user
    User.objects.get(email=user).delete()
    