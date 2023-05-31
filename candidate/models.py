from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models import signals
from accounts.models import *
from random import *
from organization.models import *
from django.core.files.base import ContentFile
from job.models import Job
import cuid

# Create your models here.
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class Candidate(User):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        parent_link=True,
        related_name='candidate',
    )
    erefid = models.SlugField(blank=True,null=True)
    organizations = models.ManyToManyField(OrganizationProfile, blank=True)
    complete = models.PositiveIntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    mobile = models.CharField(max_length=256, null=True, blank=True)
    verified = models.BooleanField(default=False)
    
    

    class Meta:
        verbose_name = _('Candidate Account')
        verbose_name_plural = _('Candidates Account')

@receiver(signals.pre_save, sender=Candidate)
def populate_erefid(sender, instance, **kwargs):

    # cuid_str = cuid.cuid()
    
    slug = cuid.cuid()

    if not instance.erefid:
        instance.erefid = slug        


class CandidateProfile(models.Model):
    user = models.ForeignKey(Candidate,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    mobile = models.CharField(max_length=256, null=True, blank=True)
    profile = models.FileField(upload_to='candidate/logo/name/', default="default_image.jpeg")
    summary = models.CharField(max_length=256, null=True, blank=True)
    current_salary = models.CharField(max_length=256, null=True, blank=True)
    expected_salary = models.CharField(max_length=256, null=True, blank=True)
    notice_period = models.CharField(max_length=256, null=True, blank=True)
    recuriter_message = models.CharField(max_length=256, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

# @receiver(post_save, sender=Candidate)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         CandidateProfile.objects.create(user=instance)

# @receiver(post_save, sender=Candidate)
# def save_user_profile(sender, instance, **kwargs):
#     instance.candidateprofile.save()

class Link(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Candidate Social Link'
        verbose_name_plural = 'Candidate Social Links'

    def __str__(self):
        return self.user.email + self.title

class Skill(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True)
    experties = models.CharField(max_length=256, null=True, blank=True)
    skill_set = models.CharField(max_length=256, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Candidate Skill'
        verbose_name_plural = 'Candidate Skills'

    def __str__(self):
        return self.user.email + self.title

class CandidateEducation(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True)
    college = models.CharField(max_length=256, null=True, blank=True)
    yearofjoin = models.DateField(null=True, blank=True)
    yearofend = models.DateField(null=True, blank=True)
    edubody = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Candidate Education'
        verbose_name_plural = 'Candidate Educations'

    def __str__(self):
        return self.user.email + self.title

class CandidateExperience(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
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
        verbose_name = 'Candidate Experience'
        verbose_name_plural = 'Candidate Experiences'
    
    def __str__(self):
        return self.user.email + self.title

class Certificate(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
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
        verbose_name = 'Candidate Certificate'
        verbose_name_plural = 'Candidate Certificate'

    def __str__(self):
        return self.user.email + self.title

class Resume(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    title = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='candidate/resume/', null=True, blank=True)
    file_img = models.FileField(upload_to='candidate/resume/png/', null=True, blank=True)
    full_text = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name = 'Candidate Resume'
        verbose_name_plural = 'Candidate Resumes'
    
    def save(self, *args, **kwargs):
        super(Resume, self).save(*args, **kwargs)
        