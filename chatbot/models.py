from django.db import models
from accounts.models import User
from organization.models import *
from job.models import *
from vendors.models import *

# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(null=True,blank=True)
    response = models.TextField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.timestamp}"
    
class Notification(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="From_Account")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="To_Account")
    Org = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField( null=True, blank=True)
    notification_type = models.CharField(max_length=256, null=True, blank=True)
    read = models.BooleanField(default='False')
    adminRead = models.BooleanField(default='False')
    # Job
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    
    # Applicant
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True)
    # Interview
    interview = models.ForeignKey(CandidateInterview, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title