from django.urls import path
from .views import *

urlpatterns = [
    path('plan-list/', PlansListApiView.as_view(), name='register'),
    path('subscription/', SubscriptionUserApiView.as_view(), name='register'),
    path('cancle-subscription/', SubscriptionDeleteApiView.as_view(), name='register'),
]