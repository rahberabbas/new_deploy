from rest_framework import serializers
from .models import *
from candidate.serializers import *
from accounts.models import User

class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['refid','job_title', 'job_function', 'department', 'industry', 'group_or_division', 'vacancy', 'description', 'responsibility','looking_for', 'jobSkill', 'employment_type', 'experience', 'education', 'location', 'currency', 'relocation', 'visa', 'worktype', 'deadline', 'timestamp', 'publish_date', 'refid','jobStatus']
    


from organization.models import Organization
class TeamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"

class ListJobSerializer(serializers.ModelSerializer):
    team = TeamListSerializer(many=True)
    class Meta:
        model = Job
        fields = '__all__'

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = '__all__'

class DashboardAllApplicantSerializer(serializers.ModelSerializer):
    user = CandidateProfileDataSerializer()
    # cand = CandidateProfileDataSerializer2()
    job = ListJobSerializer()

    class Meta:
        model = Applicant
        fields = '__all__'


class SingleApplicantSerializer(serializers.ModelSerializer):
    user = CandidateProfileDataSerializer()
    # cand = CandidateProfileDataSerializer2()
    job = ListJobSerializer()
    class Meta:
        model = Applicant
        fields = '__all__'


# Applicant

class ApplicantSerializer(serializers.ModelSerializer):
    # user = CandidateProfileDataSerializer()
    # job = ListJobSerializer()
    class Meta:
        model = Applicant
        fields = ['status']

class ListApplicantSerializer(serializers.ModelSerializer):
    user = CandidateProfileDataSerializer()
    job = ListJobSerializer()
    class Meta:
        model = Applicant
        fields = '__all__'

class UserSerializer2(serializers.ModelSerializer):       
    class Meta:
        model = User
        fields = '__all__'  

class ListFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer2()
    applicant = ListApplicantSerializer()
    class Meta:
        model = Feedback
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['status','feedback']

class CurrentUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'  
        
class OfferManagementCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferManagement
        fields = [
            'designation',
            'department',
            'section',
            'divsion',
            'grade',
            'location',
            'currency',
            'salary_type',
            'salary_from',
            'salary_to',
            'candidate_type',
            'visa_sponsorship',
            'paid_relocation',
            'offerLetter',
            'status',
            'candidate_status'
        ]
    
class OfferManagementSerializer(serializers.ModelSerializer):
    applicant = ListApplicantSerializer()
    class Meta:
        model = OfferManagement
        fields = '__all__'
        
class OfferFeedbackCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferFeedback
        fields = [
            'feedback',
            'status',
        ]
    
class UserOfferManagementFSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class OfferFeedbackSerializer(serializers.ModelSerializer):
    organization = UserOfferManagementFSerializer()
    class Meta:
        model = OfferFeedback
        fields = '__all__'
        
class InterViewSeerializer(serializers.ModelSerializer):
    applicant = ListApplicantSerializer()
    job=ListJobSerializer()
    class Meta:
        model = CandidateInterview
        fields = '__all__'
        
class InterviewCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateInterview
        fields = ['date_time_from','date_time_to', 'interview_name', 'platform', 'description', 'link']
        
class ListInterViewSerializer(serializers.ModelSerializer):
    applicant = ListApplicantSerializer()
    add_interviewer = TeamListSerializer(many=True)
    job = ListJobSerializer()
    user = UserSerializer2()
    class Meta:
        model = CandidateInterview
        fields = '__all__'