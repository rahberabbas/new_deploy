from rest_framework import serializers
from job.serializers import ListApplicantSerializer, InterViewSeerializer

from organization.serializers import *
from .models import *
from candidate.models import *


# Chat

class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ['message', 'response',]

class ListChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = '__all__' 

class InterviewQuestionGeneratorSerailizer(serializers.ModelSerializer):
    
    class Meta:
        model = Resume
        fields = ['full_text']
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'notification_type', 'read', 'adminRead']

class UserSerializer(serializers.ModelSerializer):       
    class Meta:
        model = User
        fields = '__all__'  

class ListNotificationSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()
    to_user = UserSerializer()
    Org = ListOrganizationProfileSerializer()
    job = ListJobSerializer()
    applicant = ListApplicantSerializer()
    interview = InterViewSeerializer()
    class Meta:
        model = Notification
        fields = '__all__'