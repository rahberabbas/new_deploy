from rest_framework import serializers
from .models import *

from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class SuperAdminRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = SuperAdmin
        fields=['email', 'name', 'company_name','company_type', 'password', 'password2',]
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
        return SuperAdmin.objects.create_super_organization(**validate_data)




class OrgRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = Organization
        fields=['email', 'name', 'company_name','company_type', 'password', 'password2', 'role', 'organization_permissions']
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
        fields=['email', 'name', 'role','created_by','organization_permissions',]
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
        elif SuperAdmin.objects.filter(email=email).exists():
          filtered_user_by_email = SuperAdmin.objects.filter(email=email)
          user = auth.authenticate(email=email, password=password)
          try:
            userObj = SuperAdmin.objects.get(user=user)
            type='SuperAdmin'
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
            userFObj = Organization.objects.filter(user=user).values()
            #print(user.tokens)
          except:
            raise serializers.ValidationError('Invalid Credential')
        
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
              raise AuthenticationFailed('Email is not verified')
          return {
              'email': userObj.email,
              'tokens': user.tokens,
              'type':type,
              'userObj':userFObj,
          }

class OrganizationPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationPermission
        fields = ['title']

class OrganizationUserInfoSerializer(serializers.ModelSerializer):
    organization_permissions = OrganizationPermissionSerializer(many=True)
    class Meta:
        model = Organization
        fields = "__all__"


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