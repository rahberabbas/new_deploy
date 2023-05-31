from django.db import models
from random import randint
from organization.models import *
from django.utils.translation import gettext_lazy as _
import cuid
from vendors.models import NewVendor

# Create your models here.
class Job(models.Model):
    refid = models.SlugField(blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True, blank=True)
    job_title = models.CharField(max_length=300, null=True, blank=True)
    job_function = models.CharField(max_length=300, null=True, blank=True)
    department = models.CharField(max_length=300, null=True, blank=True)
    industry = models.CharField(max_length=300, null=True, blank=True)
    group_or_division = models.CharField(max_length=300, null=True, blank=True)
    vacancy = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    responsibility = models.TextField(null=True, blank=True)
    looking_for = models.TextField(null=True, blank=True)
    jobSkill = models.TextField(null=True, blank=True)
    employment_type = models.CharField(max_length=300, null=True, blank=True)
    experience = models.CharField(max_length=300, null=True, blank=True)
    education = models.CharField(max_length=300, null=True, blank=True)
    location = models.CharField(max_length=300, null=True, blank=True)
    currency = models.CharField(max_length=300, null=True, blank=True)
    relocation = models.CharField(max_length=300, null=True, blank=True)
    visa = models.CharField(max_length=300, null=True, blank=True)
    worktype = models.CharField(max_length=300, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True,null=True)
    jobStatus = models.CharField(max_length=300, null=True, blank=True)
    team = models.ManyToManyField(Organization,blank=True,related_name="Team")
    vendor = models.ManyToManyField(NewVendor,blank=True,related_name="Vendor")

    class Meta:
        verbose_name = _('Organization Job')
        verbose_name_plural = _('Organization Jobs')

    def __str__(self):
        return self.job_title

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@receiver(signals.pre_save, sender=Job)
def populate_refid(sender, instance, **kwargs):
    
    slug = cuid.cuid()

    if not instance.refid:
        instance.refid = slug  


from candidate.models import *
class Applicant(models.Model):

    arefid = models.SlugField(blank=True)
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    # cand = models.ForeignKey(CandidateProfile,on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=300, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = _('Candidate Application')
        verbose_name_plural = _('Candidate Applications')

    def __str__(self):
        return self.user.email

@receiver(signals.pre_save, sender=Applicant)
def populate_arefid(sender, instance, **kwargs):

    
    slug = cuid.cuid()

    if not instance.arefid:
        instance.arefid = slug 

class Feedback(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    status = models.CharField(max_length=300, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Candidate Application Feedback')
        verbose_name_plural = _('Candidate Application Feedbacks')

    def __str__(self):
        return self.user.email


class VendorCandidateProfile(models.Model):
    vcrefid = models.SlugField(blank=True,null=True)
    vendor = models.ForeignKey(NewVendor, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    email = models.EmailField(max_length=256, null=True, blank=True)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    mobile = models.CharField(max_length=256, null=True, blank=True)
    resume = models.FileField(upload_to='vendor/candidate/resume/', null=True, blank=True)
    summary = models.CharField(max_length=256, null=True, blank=True)
    current_salary = models.CharField(max_length=256, null=True, blank=True)
    expected_salary = models.CharField(max_length=256, null=True, blank=True)
    notice_period = models.CharField(max_length=256, null=True, blank=True)
    recuriter_message = models.CharField(max_length=256, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    
@receiver(signals.pre_save, sender=VendorCandidateProfile)
def populate_vcrefid(sender, instance, **kwargs):

    # cuid_str = cuid.cuid()
    
    slug = cuid.cuid()

    if not instance.vcrefid:
        instance.vcrefid = slug 
        
class VendorCandidateSocialLink(models.Model):
    user = models.ForeignKey(VendorCandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Vendor Candidate Social Link'
        verbose_name_plural = 'Vendor Candidate Social Links'

    def __str__(self):
        return self.user.email + self.title
    
    
class VendorCandidateEducation(models.Model):
    user = models.ForeignKey(VendorCandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True)
    college = models.CharField(max_length=256, null=True, blank=True)
    yearofjoin = models.DateField(null=True, blank=True)
    yearofend = models.DateField(null=True, blank=True)
    edubody = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Vendor Candidate Education'
        verbose_name_plural = 'Vendor Candidate Educations'

    # def __str__(self):
    #     return self.title
    
class VendorCandidateExperience(models.Model):
    user = models.ForeignKey(VendorCandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True)
    company = models.CharField(max_length=256, null=True, blank=True)
    year_of_join = models.DateField(null=True, blank=True)
    year_of_end = models.DateField(null=True, blank=True)
    expbody = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=256, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Vendor Candidate Experience'
        verbose_name_plural = 'Vendor Candidate Experiences'
    
    # def __str__(self):
    #     return self.user.email + self.title

class VendorCandidateCertificate(models.Model):
    user = models.ForeignKey(VendorCandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True)
    company = models.CharField(max_length=256, null=True, blank=True)
    yearofissue = models.DateField(null=True, blank=True)
    yearofexp = models.DateField(null=True, blank=True)
    creid = models.CharField(max_length=256, null=True, blank=True)
    creurl = models.CharField(max_length=256, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Vendor Candidate Certificate'
        verbose_name_plural = 'Vendor Candidate Certificate'

    # def __str__(self):
    #     return self.user.email + self.title
    
class VendorApplicant(models.Model):

    arefid = models.SlugField(blank=True)
    vendor = models.ForeignKey(NewVendor, on_delete=models.CASCADE)
    applicant = models.ForeignKey(VendorCandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=300, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Vendors Application')
        verbose_name_plural = _('Vendors Applications')

    def __str__(self):
        return f"{self.vendor.email} -> {self.applicant.email}"
    
class CandidateInterview(models.Model):
    irefid = models.SlugField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    org = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, null=True, blank=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    date_time_from = models.DateTimeField( null=True, blank=True)
    date_time_to = models.DateTimeField( null=True, blank=True)
    interview_name = models.CharField(max_length=256, null=True, blank=True)
    platform = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    add_interviewer = models.ManyToManyField(Organization,blank=True,related_name="Interviewer")
    link = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    # def __str__(self):
    #     return f"{self.applicant.user.email} -> {self.job.job_title} -> {self.timestamp}"
    
    
@receiver(signals.pre_save, sender=CandidateInterview)
def populate_irefid(sender, instance, **kwargs):

    
    slug = cuid.cuid()

    if not instance.irefid:
        instance.irefid = slug 
    
class OfferManagement(models.Model):
    omrefid = models.SlugField(blank=True, null=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
    designation = models.CharField(max_length=1000, null=True, blank=True)
    department = models.CharField(max_length=1000, null=True, blank=True)
    section = models.CharField(max_length=1000, null=True, blank=True)
    divsion = models.CharField(max_length=1000, null=True, blank=True)
    grade = models.CharField(max_length=1000, null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    currency = models.CharField(max_length=1000, null=True, blank=True)
    salary_type = models.CharField(max_length=1000, null=True, blank=True)
    salary_from = models.CharField(max_length=1000, null=True, blank=True)
    salary_to = models.CharField(max_length=1000, null=True, blank=True)
    candidate_type = models.CharField(max_length=1000, null=True, blank=True)
    visa_sponsorship = models.CharField(max_length=1000, null=True, blank=True)
    paid_relocation = models.CharField(max_length=1000, null=True, blank=True)
    approval_authorities = models.ManyToManyField(Organization,blank=True,related_name="Authority")
    offerLetter = models.FileField(upload_to='org/candidate/offer/', null=True, blank=True)
    status = models.CharField(max_length=300, null=True, blank=True)
    candidate_status = models.CharField(max_length=300, default="Pending")
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.applicant.user.first_name
    
@receiver(signals.pre_save, sender=OfferManagement)
def populate_omrefid(sender, instance, **kwargs):

    # cuid_str = cuid.cuid()
    
    slug = cuid.cuid()

    if not instance.omrefid:
        instance.omrefid = slug
    
class OfferFeedback(models.Model):
    ofrefid = models.SlugField(blank=True, null=True)
    offer = models.ForeignKey(OfferManagement, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1000, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.offer.omrefid
    
@receiver(signals.pre_save, sender=OfferFeedback)
def populate_omrefid(sender, instance, **kwargs):

    # cuid_str = cuid.cuid()
    
    slug = cuid.cuid()

    if not instance.ofrefid:
        instance.ofrefid = slug