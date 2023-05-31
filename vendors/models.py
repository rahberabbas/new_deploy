from django.db import models
# from job.models import Job
from organization.models import SuperAdmin, OrganizationProfile
import cuid
from django.dispatch import receiver
from django.db.models import signals
from accounts.models import *
from django.utils.translation import gettext_lazy as _


# Create your models here.

class NewVendor(models.Model):
    vrefid = models.SlugField(blank=True,null=True)
    user = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(max_length=256, null=True, blank=True)
    contact_number = models.CharField(max_length=256, null=True, blank=True)
    agent_name = models.CharField(max_length=256, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    agreement = models.FileField(upload_to='vendor/agreement/', null=True, blank=True)
    agreement_valid_start_date = models.DateField(null=True, blank=True)
    agreement_valid_end_date = models.DateField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    onboard = models.BooleanField(default=False)
    activate = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.email} -> {self.company_name}"
    
@receiver(signals.pre_save, sender=NewVendor)
def populate_vrefid(sender, instance, **kwargs):

    # cuid_str = cuid.cuid()
    
    slug = cuid.cuid()

    if not instance.vrefid:
        instance.vrefid = slug 
        
class VendorRegistration(User):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        parent_link=True,
        related_name='vendors',
    )
    vendor_logo = models.FileField(upload_to='vendor/logos/', null=True, blank=True)
    vendor = models.ForeignKey(NewVendor, on_delete=models.CASCADE, null=True, blank=True)
    contact_2 = models.CharField(max_length=256, null=True, blank=True)
    license_number = models.CharField(max_length=256, null=True, blank=True)
    headquater_address = models.TextField(null=True, blank=True)
    signature = models.FileField(upload_to='vendor/agreement/signature/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.vendor.email} -> {self.vendor.user.email}"
    
