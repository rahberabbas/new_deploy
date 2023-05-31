from django.urls import path
from .views import *

urlpatterns = [
    path('addchat/', ChatView.as_view(), name='create-chat'),
    path('updatechat/<int:pk>/', ChatView.as_view(), name='create-chat'),
    path('listchat/', ListChatView.as_view(), name='list-chat'),
    path('interview-question-generator/<str:erefid>/', InterviewQuestionGenerator.as_view(), name='chatbot-job'),
    path('chat-job-wise/<str:refid>/', ChatUserJobWiseView.as_view(), name='list-chat'),
    path('chat-organization-wise/', ChatUserOrganizationWiseView.as_view(), name='chatbot-organizatiomn'),
    
    path('notification/', NotificationView.as_view(), name='notifi'),
    path('notification/unauth/', NotificationView2.as_view(), name='notifi'),
    path('list-notification/', ListingNotificationView.as_view(), name='chatbot-organizatiomn'),
    path('list-notification-admin/', ListingNotificationViewAdmin.as_view(), name='chatbot-organizatiomn'),
    path('get-notification-count/', ListingNotificationView2.as_view(), name='chatbot-organizatiomn'),
    path('get-notification-count-admin/', ListingNotificationView22.as_view(), name='chatbot-organizatiomn'),
    path('read-notification-count/', ListingNotificationView3.as_view(), name='chatbot-organizatiomn'),
    path('read-notification-count-admin/', ListingNotificationView33.as_view(), name='chatbot-organizatiomn'),
]