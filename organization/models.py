from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models import signals
from accounts.models import *
from random import *
from datetime import datetime
import django.utils
import cuid


ORGANISATION_ROLE = {
    ('Recruiter', 'Recruiter'),
    ('Collaborator', 'Collaborator'),
    ('Hiring Manager', 'Hiring Manager'),
}

# Create your models here.
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class OrganizationPermission(models.Model):
    title = models.CharField(max_length=265, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SuperAdmin(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True, related_name='superadmin')
    srefid = models.SlugField(blank=True, null=True)
    company_name = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    paddress = models.CharField(max_length=256, null=True, blank=True)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('SuperAdmin Account')
        verbose_name_plural = _('SuperAdmins Account')


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@receiver(signals.pre_save, sender=SuperAdmin)
def populate_orefid(sender, instance, **kwargs):

    
    slug = cuid.cuid()

    if not instance.srefid:
        instance.srefid = slug 


class Organization(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True, related_name='organization')
    orefid = models.SlugField(blank=True, null=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    verified = models.BooleanField(default=False)
    role = models.CharField(choices=ORGANISATION_ROLE, max_length=255, null=True, blank=True)
    organization_permissions = models.ManyToManyField(OrganizationPermission, blank=True)
    created_by = models.ForeignKey(SuperAdmin,on_delete=models.CASCADE,null=True, blank=True)
    dept = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _('Organization Account')
        verbose_name_plural = _('Organizations Account')


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@receiver(signals.pre_save, sender=Organization)
def populate_orefid(sender, instance, **kwargs):
    
    slug = cuid.cuid()

    if not instance.orefid:
        instance.orefid = slug 


from django.db import models
from django.dispatch import receiver 
from django.db.models.signals import post_save


    
class OrganizationProfile(models.Model):
    user = models.OneToOneField(SuperAdmin,on_delete=models.CASCADE)
    unique_id = models.SlugField(blank=True, null=True, unique=True)
    about_org = models.TextField(null=True, blank=True)
    about_founder = models.TextField(null=True, blank=True)
    org_Url = models.CharField(max_length=256, null=True, blank=True)
    contact_Number = models.CharField(max_length=256, null=True, blank=True)
    company_Size = models.CharField(max_length=256, null=True, blank=True)
    workplace_Type = models.CharField(max_length=256, null=True, blank=True)
    headquarter_Location = models.TextField(null=True, blank=True)
    branch_Office = models.TextField(null=True, blank=True)
    organization_Benefits = models.TextField(null=True, blank=True)
    funding_Details = models.TextField(null=True, blank=True)
    logo = models.FileField(upload_to='org/profile/logo/', default="default_image.jpeg")
    banner = models.FileField(upload_to='org/profile/banner/', default="default_image.jpeg")
    offer = models.FileField(upload_to='org/profile/offer/', null=True, blank=True)

    class Meta:
        verbose_name = 'Organization Profile'
        verbose_name_plural = 'Organization Profiles '
    
    def __str__(self):
        return self.user.email

class OrganizationIntegration(models.Model):
    "Base integration class"
    
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, to_field='unique_id')
    created_at = models.DateTimeField(auto_now_add=True)
    access_token = models.CharField(max_length=1000, blank=True)
    refresh_token = models.CharField(max_length=1000, blank=True)
    expires_in = models.IntegerField()
    is_expired = models.BooleanField(default=False)
    provider = models.CharField(max_length=255, blank=True)
    scope = models.CharField(max_length=256)
    
    @property
    def expired(self):
        return (datetime.now().replace(tzinfo=None) - self.created_at.replace(tzinfo=None)).seconds > self.expires_in 
    
    def __str__(self):
        return self.organization.__str__() + '_' + self.provider + "_integration"
    
    class Meta:
        abstract = True
        
class OrganizationCalendarIntegration(OrganizationIntegration):
    "Calendar integration class"
    calendar_id = models.CharField(max_length=1000, blank=True)
    class Meta:
        "Calendar integration names"
        verbose_name = 'Organization Calendar Integration'
        verbose_name_plural = 'Organization Calendar Integrations'

class OrganizationMailIntegration(OrganizationIntegration):
    "Mail integration class"
    
    label_id = models.CharField(max_length=120)
    class Meta:
        "Mail integration names"
        verbose_name = 'Organization Mail Integration'
        verbose_name_plural = 'Organization Mail Integrations'

@receiver(post_save, sender=SuperAdmin)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        OrganizationProfile.objects.create(user=instance)


@receiver(post_save, sender=SuperAdmin)
def save_user_profile(sender, instance, **kwargs):
    instance.organizationprofile.save()

@receiver(signals.pre_save, sender=OrganizationProfile)
def populate_unique_id(sender, instance, **kwargs):
    
    slug = cuid.cuid()

    if not instance.unique_id:
        instance.unique_id = slug 



class OrganizationGallery(models.Model):
    organizationProfile = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE)
    image = models.FileField(upload_to='org/gallery', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Organization Gallery'
        verbose_name_plural = 'Organization Galleries '
    
    def __str__(self):
        return self.organizationProfile.unique_id


class OrganizationFounder(models.Model):
    organizationProfile = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE)
    image = models.FileField(upload_to='org/founder', null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    designation = models.CharField(max_length=256, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Organization Founder'
        verbose_name_plural = 'Organization Founders '
    
    def __str__(self):
        return self.organizationProfile.unique_id + " " + self.name


class IndividualProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    unique_id = models.SlugField(blank=True, null=True)
    profile = models.FileField(upload_to='org/profile/', default="default_image.jpeg")
    organization_Name = models.CharField(max_length=256, null=True, blank=True)
    full_Name = models.CharField(max_length=256, null=True, blank=True)
    contact_Number = models.CharField(max_length=256, null=True, blank=True)
    email = models.CharField(max_length=256, null=True, blank=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    department = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = 'Individual Profile'
        verbose_name_plural = 'Individual Profiles '
    
    def __str__(self):
        return self.user.email
    

@receiver(post_save, sender=SuperAdmin)
@receiver(post_save, sender=Organization)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        IndividualProfile.objects.create(user=instance)


@receiver(post_save, sender=SuperAdmin)
@receiver(post_save, sender=Organization)
def save_user_profile(sender, instance, **kwargs):
    instance.individualprofile.save()


@receiver(signals.pre_save, sender=IndividualProfile)
def populate_unique_id(sender, instance, **kwargs):

    
    slug = cuid.cuid()

    if not instance.unique_id:
        instance.unique_id = slug 


class IndividualLink(models.Model):
    individualProfile = models.ForeignKey(IndividualProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Individual Social Link'
        verbose_name_plural = 'Individual Social Links'

    def __str__(self):
        return self.title
    
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    org = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, null=True, blank=True)
    aname = models.TextField( null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} -> {self.aname}"
    
    
