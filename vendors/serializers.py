from rest_framework import serializers
from .models import *
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from job.serializers import *
from job.models import *

class NewVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewVendor
        fields= ["company_name", "email", "contact_number", "agent_name", "message", "agreement", "agreement_valid_start_date", "agreement_valid_end_date"]
        
class VendorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewVendor
        fields = '__all__'
        
class OnboardVendorSerailizer(serializers.ModelSerializer):
    vendor = VendorDataSerializer()
    class Meta:
        model = VendorRegistration
        fields = '__all__'
        
class VendorRegestrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = VendorRegistration
        fields=['email', 'vendor','contact_2', 'headquater_address', 'license_number', 'signature', 'password', 'password2']
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
        return VendorRegistration.objects.create_vendor_user(**validate_data)
    
class VendorLoginSerializer(serializers.ModelSerializer):
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
        elif VendorRegistration.objects.filter(email=email).exists():
          filtered_user_by_email = VendorRegistration.objects.filter(email=email)
          user = auth.authenticate(email=email, password=password)
          try:
            userObj = VendorRegistration.objects.get(user=user)
            type='Vendor'
            role='Vendor'
            userFObj = VendorRegistration.objects.filter(user=user).values()
            #print(user.tokens)
          except:
            raise serializers.ValidationError('Invalid Credential')
        elif SuperAdmin.objects.filter(user=User.objects.get(email=email)).exists() or Organization.objects.filter(user=User.objects.get(email=email)).exists():
          raise serializers.ValidationError('This Email Already Used As Organization')
          

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
            if not VendorRegistration.objects.filter(email=email).exists():
                raise AuthenticationFailed('Fill Up Sign Up Form First')
            # if not userObj.verified:
            #     # token = RefreshToken.for_user(userObj).access_token
            #     # tokens = get_tokens_for_user(userObj)
            #     # request = self.context.get("request")
            #     # current_site = get_current_site(request).domain
            #     # relativeLink = reverse('email-verify')
            #     # # #print(token)
            #     # absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            #     # # email_body = 'Hi '+user.first_name + \
            #     # #     ' Use the link below to verify your email \n' + absurl
            #     # email_body = render_to_string('verify-email.html',{
            #     #     'user': user.email,
            #     #     'absurl': absurl,
            #     # })
            #     # # #print(absurl)
            #     # # data = {'email_body': email_body, 'to_email': user.email,
            #     # #         'email_subject': 'Activate your account'}

            #     # emails = EmailMessage(subject='Activate your account', body=email_body, from_email=settings.EMAIL_HOST_USER, to=[email])
            #     # emails.content_subtype = 'html'
            #     # EmailThread(email).start()
            #     raise AuthenticationFailed('Email is not verified')
            return {
                'email': userObj.email,
                'tokens': user.tokens,
                'type':type,
                'role':role,
                'userObj':userFObj,
            }
          except:
              raise serializers.ValidationError('Account does not exists')
          
          
# Vendor Candidate

class VendorCandidateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateProfile
        fields = ['first_name','last_name', 'email','mobile','summary', 'current_salary', 'expected_salary', 'notice_period', 'recuriter_message', 'resume', 'skills']

class VendorCandidateDataSerailizer(serializers.ModelSerializer):
    class Meta:
        model = VendorCandidateProfile
        fields = '__all__'
        

class VendorCandidateSocialLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateSocialLink
        fields = ['title']
        
class ListVendorCandidateSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCandidateSocialLink
        fields = '__all__'

class VendorCandidateCertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateCertificate
        fields = ['title', 'company', 'yearofissue', 'yearofexp', 'creid', 'creurl']

class ListVendorCandidateCertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateCertificate
        fields = '__all__'
        

class VendorCandidateEducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateEducation
        fields = ['title', 'college', 'yearofjoin', 'yearofend', 'edubody']

class ListVendorCandidateEducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateEducation
        fields = '__all__'
        
class VendorCandidateExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateExperience
        fields = ['title', 'company', 'year_of_join', 'year_of_end', 'expbody', 'type']
        
class ListVendorCandidateExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCandidateExperience
        fields = '__all__'
        
class ListVendorApplicantSerializer(serializers.ModelSerializer):
    vendor = VendorDataSerializer()
    job = ListJobSerializer()
    applicant = VendorCandidateDataSerailizer()
    class Meta:
        model = VendorApplicant
        fields = '__all__'
        
class VendorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorRegistration
        fields = ['contact_2', 'headquater_address', 'license_number','logo']


class VendorUserProfileSerializer(serializers.Serializer):
    vprofiledata = VendorCandidateDataSerailizer(many=True)
    linkdata = ListVendorCandidateSocialLinkSerializer(many=True)
    vexpdata = ListVendorCandidateExperienceSerializer(many=True)
    vedudata = ListVendorCandidateEducationSerializer(many=True)
    cerdata = ListVendorCandidateCertificateSerializer(many=True)

    def to_representation(self, instance):
        vprofiledata = instance['vprofiledata']
        linkdata = instance['linkdata']
        vexpdata = instance['vexpdata']
        vedudata = instance['vedudata']
        cerdata = instance['cerdata']
        return {
            'VendorCandidateProfile': VendorCandidateDataSerailizer(vprofiledata, many=True).data,
            'Link': ListVendorCandidateSocialLinkSerializer(linkdata, many=True).data,
            'Experience': ListVendorCandidateExperienceSerializer(vexpdata, many=True).data,
            'Education': ListVendorCandidateEducationSerializer(vedudata, many=True).data,
            'Certification': ListVendorCandidateCertificateSerializer(cerdata, many=True).data,
        }
        