from rest_framework import serializers
from .models import *

from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class CandidateRegestrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = Candidate
        fields=['email', 'first_name','mobile', 'last_name', 'password', 'password2']
        extra_kwargs={
            'password':{'write_only':True}
        }

    # Validating Password and Confirm Password while Registration
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email = attrs.get('email')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        if User.objects.filter(email=email).exists():
           raise serializers.ValidationError("This Email Already Used")
        return attrs

    def create(self, validate_data):
        return Candidate.objects.create_candiate_user(**validate_data)

class CLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    tokens = serializers.SerializerMethodField()
    #print(tokens)

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        check = False
        if not User.objects.filter(email=email).exists():
          raise serializers.ValidationError('User Not Exist')
        elif SuperAdmin.objects.filter(user=User.objects.get(email=email)).exists():
          raise serializers.ValidationError('This Email Already Used As SuperAdmin')
        elif Organization.objects.filter(user=User.objects.get(email=email)).exists():
          raise serializers.ValidationError('This Email Already Used As Organization')
        elif Candidate.objects.filter(email=email).exists():
          filtered_user_by_email = Candidate.objects.filter(email=email)
          user = auth.authenticate(email=email, password=password)
          try:
            userObj = Candidate.objects.get(user=user)
            type='Candidate'
            role='Candidate'
            userFObj = Candidate.objects.filter(user=user).values()
          except:
            raise serializers.ValidationError('Invalid Credential')
          

        # else:
          
        #   # #print()
        #   # check=True
        
           
        if check:
          raise AuthenticationFailed('Invalid credentials, try again')
        else:
          try:
            if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
                raise AuthenticationFailed(
                    detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

            if not userObj:
                raise AuthenticationFailed('Invalid credentials, try again')
            if not user.is_active:
                raise AuthenticationFailed('Account disabled, contact admin')
            if not userObj.verified:
                # token = RefreshToken.for_user(userObj).access_token
                # tokens = get_tokens_for_user(userObj)
                # request = self.context.get("request")
                # current_site = get_current_site(request).domain
                # relativeLink = reverse('email-verify')
                # # #print(token)
                # absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
                # # email_body = 'Hi '+user.first_name + \
                # #     ' Use the link below to verify your email \n' + absurl
                # email_body = render_to_string('verify-email.html',{
                #     'user': user.email,
                #     'absurl': absurl,
                # })
                # # #print(absurl)
                # # data = {'email_body': email_body, 'to_email': user.email,
                # #         'email_subject': 'Activate your account'}

                # emails = EmailMessage(subject='Activate your account', body=email_body, from_email=settings.EMAIL_HOST_USER, to=[email])
                # emails.content_subtype = 'html'
                # EmailThread(email).start()
                raise AuthenticationFailed('Email is not verified')
            return {
                'email': userObj.email,
                'tokens': user.tokens,
                'type':type,
                'role':role,
                'userObj':userFObj,
            }
          except:
              raise serializers.ValidationError('Account does not exists')
        





from .models import *

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields= '__all__'
        
# class CandidateAccountSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = CandidateProfile
#         fields = ['profile', 'country', 'stoken']

class BioSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateProfile
        fields = ['summary', 'current_salary', 'expected_salary', 'notice_period', 'recuriter_message']

# Candidate Profiles

class FinalCandidateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateProfile
        fields = ['first_name','last_name','mobile','summary', 'current_salary', 'expected_salary', 'notice_period', 'recuriter_message']

class ListCandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = '__all__'

class ListCandidateProfileSerializer(serializers.ModelSerializer):
    user = ListCandidateSerializer()
    class Meta:
        model = CandidateProfile
        fields = '__all__'


# Skills

class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ['title', 'experties', 'skill_set']

class ListSkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = '__all__'

# Link

class LinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = ['title']

class ListLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = '__all__'        

# Resume

class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = ['title', 'file']

class ListResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = '__all__'  

# Certificate

class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = ['title', 'company', 'yearofissue', 'yearofexp', 'creid', 'creurl',]

class ListCertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = '__all__' 

# Education

class EducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateEducation
        fields = ['title', 'college', 'yearofjoin', 'yearofend', 'edubody']

class ListEducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateEducation
        fields = '__all__'

# Experience

class ExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateExperience
        fields = ['title', 'company', 'year_of_join', 'year_of_end', 'expbody', 'type']

class ListExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateExperience
        fields = '__all__'

# class CandidateProfileDataSerializer2(serializers.ModelSerializer):
#     # user = CandidateDataSerializer()
#     class Meta:
#         model = CandidateProfile
#         fields = '__all__'

class CandidateProfileDataSerializer(serializers.ModelSerializer):
    # profile = CandidateProfileDataSerializer2()
    class Meta:
        model = Candidate
        fields = '__all__'




class CandidateProfileDataSerializer2(serializers.ModelSerializer):
    # user = CandidateDataSerializer()
    class Meta:
        model = CandidateProfile
        fields = '__all__'

class CandidateProfileDataSerializer(serializers.ModelSerializer):
    # profile = CandidateProfileDataSerializer2()
    class Meta:
        model = Candidate
        fields = '__all__'


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']

class UserProfileSerializer(serializers.Serializer):
    cprofiledata = ListCandidateProfileSerializer(many=True)
    skilldata = ListSkillSerializer(many=True)
    linkdata = ListLinkSerializer(many=True)
    cexpdata = ListExperienceSerializer(many=True)
    cedudata = ListEducationSerializer(many=True)
    cerdata = ListCertificateSerializer(many=True)
    resumedata = ListResumeSerializer(many=True)

    def to_representation(self, instance):
        cprofiledata = instance['cprofiledata']
        skilldata = instance['skilldata']
        linkdata = instance['linkdata']
        cexpdata = instance['cexpdata']
        cedudata = instance['cedudata']
        cerdata = instance['cerdata']
        resumedata = instance['resumedata']
        return {
            'CandidateProfile': ListCandidateProfileSerializer(cprofiledata, many=True).data,
            'Skill': ListSkillSerializer(skilldata, many=True).data,
            'Link': ListLinkSerializer(linkdata, many=True).data,
            'Experience': ListExperienceSerializer(cexpdata, many=True).data,
            'Education': ListEducationSerializer(cedudata, many=True).data,
            'Certification': ListCertificateSerializer(cerdata, many=True).data,
            'Resume': ListResumeSerializer(resumedata, many=True).data,
        }
        
class UserProfileSerializer1(serializers.Serializer):
    candidatedata = CandidateProfileDataSerializer(many=True)
    cprofiledata = ListCandidateProfileSerializer(many=True)
    skilldata = ListSkillSerializer(many=True)
    linkdata = ListLinkSerializer(many=True)
    cexpdata = ListExperienceSerializer(many=True)
    cedudata = ListEducationSerializer(many=True)
    cerdata = ListCertificateSerializer(many=True)
    resumedata = ListResumeSerializer(many=True)

    def to_representation(self, instance):
        # candidatedata = instance['candidatedata']
        cprofiledata = instance['cprofiledata']
        skilldata = instance['skilldata']
        linkdata = instance['linkdata']
        cexpdata = instance['cexpdata']
        cedudata = instance['cedudata']
        cerdata = instance['cerdata']
        resumedata = instance['resumedata']
        return {
            
            # 'Candidatedata': CandidateProfileDataSerializer(candidatedata, many=True).data,
            'CandidateProfile': ListCandidateProfileSerializer(cprofiledata, many=True).data,
            'Skill': ListSkillSerializer(skilldata, many=True).data,
            'Link': ListLinkSerializer(linkdata, many=True).data,
            'Experience': ListExperienceSerializer(cexpdata, many=True).data,
            'Education': ListEducationSerializer(cedudata, many=True).data,
            'Certification': ListCertificateSerializer(cerdata, many=True).data,
            'Resume': ListResumeSerializer(resumedata, many=True).data,
            
        }