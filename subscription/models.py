from datetime import datetime
from django.db import models
from organization.models import SuperAdmin
import django.utils
from djstripe.models import Customer, Subscription

# class SubscriptionPlan(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     stripe_plan_id = models.CharField(max_length=100, unique=True)

class SubscriptionPlans(models.Model):
    organisation = models.OneToOneField(SuperAdmin, on_delete=models.CASCADE, unique=True, null=True, blank=True)
    plan = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    