from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models import signals
from rest_framework_simplejwt.tokens import RefreshToken

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("User must have an Email")
        user = self.model(
            email=self.normalize_email(email)
        )
        if password:
            user.set_password(password)
            user.save(using=self._db)
        else:
            user.set_unusable_password()
            user.save()
        return user
    
    def create_candiate_user(self, email,first_name, last_name,mobile, password=None, password2=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            mobile = mobile
        )

        if password:
            user.set_password(password)
            user.save(using=self._db)
        else:
            user.set_unusable_password()
            user.save()
        return user

    def create_vendor_user(self, email, contact_2,headquater_address, license_number, signature,vendor=None, password=None, password2=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            contact_2 = contact_2,
            headquater_address = headquater_address,
            license_number = license_number,
            signature = signature,
        )

        if password:
            user.set_password(password)
            user.save(using=self._db)
        else:
            user.set_unusable_password()
            user.save()
        return user


    def create_super_organization(self, email, company_name,name,password=None, password2=None):
        if not email:
            raise ValueError("user must have an Email")
        
        user = self.model(
            email=self.normalize_email(email),
            name = name,
            company_name = company_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_organization(self, email, role,name,dept,created_by=None,organization_permissions=None,password=None, password2=None):
        if not email:
            raise ValueError("user must have an Email")
        
        user = self.model(
            email=self.normalize_email(email),
            name = name,
            role = role,
            dept = dept,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


ORGANISATION_ROLE = {
    ('ADMIN', 'ADMIN'),
    ('COLLABRATORS', 'COLLABRATORS'),
    ('HIRING_MANAGER', 'HIRING_MANAGER'),
}

AUTH_PROVIDERS = {'email': 'email'}

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255, unique=True
    )
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    
    objects = UserManager() 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()