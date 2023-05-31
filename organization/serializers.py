from candidate.models import Candidate
from job.serializers import ListJobSerializer
from rest_framework import serializers
from .models import *
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class SuperAdminRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = SuperAdmin
        fields=['email', 'name', 'company_name', 'password', 'password2',]
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        company_name = attrs.get('company_name')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        if SuperAdmin.objects.filter(company_name=company_name).exists():
            raise serializers.ValidationError("Company Name Already Acquired")
        commonEmailCheck = ['gmail', 'outlook', 'protonMail']
        url_string=attrs.get('email').lower()
        if any(ext in url_string for ext in commonEmailCheck):
            raise serializers.ValidationError("Company Email Required")
        return attrs

    def create(self, validate_data):
        return SuperAdmin.objects.create_super_organization(**validate_data)




class OrgRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = Organization
        fields=['email', 'name', 'company_name', 'password', 'password2', 'role', 'organization_permissions']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        commonEmailCheck = ['gmail', 'outlook', 'protonMail']
        url_string=attrs.get('email').lower()
        if any(ext in url_string for ext in commonEmailCheck):
            raise serializers.ValidationError("Company Email Required")
        return attrs

    def create(self, validate_data):
        return Organization.objects.create_organization(**validate_data)


import random
import array
 
def randompassgenerator():
    MAX_LEN = 12
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] 
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                        'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                        'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                        'z']
    
    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                        'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                        'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                        'Z']
    
    SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
            '*', '(', ')', '<']
    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS
    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)
    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol
    for x in range(MAX_LEN - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)
        temp_pass_list = array.array('u', temp_pass)
        random.shuffle(temp_pass_list)
    password = ""
    for x in temp_pass_list:
            password = password + x
            
    return(password)

class OrganizationAdminCreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields=['email', 'name', 'role','created_by','organization_permissions','dept',]
        extra_kwargs={
            'password':{'write_only':True}
        }
        

    def validate(self, attrs):
        password = randompassgenerator()
        password2 = password
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        commonEmailCheck = ['gmail', 'outlook', 'protonMail']
        url_string=attrs.get('email').lower()
        if any(ext in url_string for ext in commonEmailCheck):
            raise serializers.ValidationError("Company Email Required")
        return attrs

    def create(self, validate_data):
        return Organization.objects.create_organization(**validate_data)


class OrganizationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"

class OrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['role']
        

class LoginSerializer(serializers.ModelSerializer):
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
        elif Candidate.objects.filter(user=User.objects.get(email=email)).exists():
          raise serializers.ValidationError('This Email Already Used As Candidate')
        elif SuperAdmin.objects.filter(email=email).exists():
          filtered_user_by_email = SuperAdmin.objects.filter(email=email)
          user = auth.authenticate(email=email, password=password)
          try:
            userObj = SuperAdmin.objects.get(user=user)
            type='Organization'
            role='Super Admin'
            userFObj = SuperAdmin.objects.filter(user=user).values()
            #print(user.tokens)
          except:
            raise serializers.ValidationError('Invalid Credential')
        elif Organization.objects.filter(email=email).exists():
          print("Here")
          filtered_user_by_email = Organization.objects.filter(email=email)
          print(filtered_user_by_email)
          user = auth.authenticate(email=email, password=password)
          print(user)
          try:
            userObj = Organization.objects.get(user=user)
            type='Organization'
            role=''
            userFObj = Organization.objects.filter(user=user).values()
            for i in userFObj:
                role = i["role"]
            #print(user.tokens)
          except:
            raise serializers.ValidationError('Invalid Credential')
        
        if check:
          raise AuthenticationFailed('Invalid credentials, try again')
        else:
        #   try:
            if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
                raise AuthenticationFailed(
                    detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

            if not userObj:
                raise AuthenticationFailed('Invalid credentials, try again')
            if not user.is_active:
                raise AuthenticationFailed('Account disabled, contact admin')
            print(userObj)
            if not userObj.verified:
                raise AuthenticationFailed('Email is not verified')
            return {
                'email': userObj.email,
                'tokens': user.tokens,
                'type':type,
                'role':role,
                'userObj':userFObj,
            }
        #   except Exception as e:
        #       print(e)
        #       print("---------")
        #       raise serializers.ValidationError('User Does not exists')

class OrganizationPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationPermission
        fields = ['title']

class OrganizationUserInfoSerializer(serializers.ModelSerializer):
    organization_permissions = OrganizationPermissionSerializer(many=True)
    class Meta:
        model = Organization
        fields = "__all__"

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
        elif Candidate.objects.filter(email=email).exists():
          filtered_user_by_email = Candidate.objects.filter(email=email)
          user = auth.authenticate(email=email, password=password)
          try:
            userObj = Candidate.objects.get(user=user)
            type='Candidate'
            userFObj = Candidate.objects.filter(user=user).values()
            #print(user.tokens)
          except:
            raise serializers.ValidationError('Invalid Credential')
          

        # else:
          
        #   # #print()
        #   # check=True
        
           
        if check:
          raise AuthenticationFailed('Invalid credentials, try again')
        else:
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
              'userObj':userFObj,
          }
        

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']



# Organization Profile

class OrganizationProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationProfile
        fields = ['about_org','about_founder','org_Url','contact_Number','company_Size','workplace_Type','headquarter_Location','branch_Office','organization_Benefits','funding_Details','logo','banner','offer']

class ListOrganizationProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationProfile
        fields = '__all__'      
class ListOrganizationAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'      

class OrganizationGallerySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrganizationGallery
        fields = ['image']

class ListOrganizationGallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationGallery
        fields = '__all__'    
        

class OrganizationFounderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrganizationFounder
        fields = ['image','name','designation']

class ListOrganizationFounderSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationFounder
        fields = '__all__'    
        
# Individual Profile

class IndividualProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndividualProfile
        fields = ['profile','organization_Name','full_Name','contact_Number','email','title','department']

class ListIndividualProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndividualProfile
        fields = '__all__'      


# Individual Link

class IndividualLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndividualLink
        fields = ['title']

class ListIndividualLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndividualLink
        fields = '__all__'      

class OrgProfileCarrierSerializer(serializers.Serializer):
    oprofiledata = ListOrganizationProfileSerializer(many=True)
    gallerydata = ListOrganizationGallerySerializer(many=True)
    founderdata = ListOrganizationFounderSerializer(many=True)
    jobdata = ListJobSerializer(many=True)

    def to_representation(self, instance):
        oprofiledata = instance['oprofiledata']
        gallerydata = instance['gallerydata']
        founderdata = instance['founderdata']
        jobdata = instance['jobdata']
        return {
            'OrgProfile': ListOrganizationProfileSerializer(oprofiledata, many=True).data,
            'Gallery': ListOrganizationGallerySerializer(gallerydata, many=True).data,
            'Founder': ListOrganizationFounderSerializer(founderdata, many=True).data,
            'Job': ListJobSerializer(jobdata, many=True).data,
        }

class OrgProfileCarrierSerializer1(serializers.Serializer):
    oprofiledata = ListOrganizationProfileSerializer(many=True)

    def to_representation(self, instance):
        oprofiledata = instance['oprofiledata']
        return {
            'OrgProfile': ListOrganizationProfileSerializer(oprofiledata, many=True).data,
        }
        
class ListOrganizationAccountAndIndividualProfileSerializer(serializers.Serializer):
    organizationAccount = ListOrganizationAccountSerializer(many=True)
    individualProfile = ListIndividualProfileSerializer(many=True)

    def to_representation(self, instance):
        organizationAccount = instance['organizationAccounts']
        individualProfile = instance['individualProfiles']
        
        return {
            'OrganizationAccounts': ListOrganizationAccountSerializer(organizationAccount, many=True).data,
            'IndividualProfiles': ListIndividualProfileSerializer(individualProfile, many=True).data,
        }

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['aname']
        
class ListActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'