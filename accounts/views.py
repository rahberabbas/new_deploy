# from django.shortcuts import render
# from .serializers import *
# from .models import *
# from .renderers import *
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework import generics, status
# import jwt
# from rest_framework.permissions import (
#     IsAuthenticated,
#     IsAuthenticatedOrReadOnly,
#     AllowAny,
# )
# from rest_framework.generics import (
#     CreateAPIView,
#     DestroyAPIView,
#     ListAPIView,
#     UpdateAPIView,
#     RetrieveAPIView,
#     RetrieveUpdateAPIView,
#     RetrieveUpdateDestroyAPIView,
# )
# from rest_framework.views import APIView
# import random
# import string
# from django.contrib.auth.hashers import make_password
# from django.core.mail import EmailMessage
# from django.conf import settings
# import threading
# class EmailThread(threading.Thread):

#     def __init__(self, email):
#         self.email = email
#         threading.Thread.__init__(self)

#     def run(self):
#         self.email.send()

# # Create your views here.

# def get_tokens_for_user(user):
#   refresh = RefreshToken.for_user(user)
#   return {
#       'refresh': str(refresh),
#       'access': str(refresh.access_token),
#   }


# class SuperAdminRegistrationView(generics.GenericAPIView):

#     serializer_class = SuperAdminRegistrationSerializer
#     renderer_classes = (UserRenderer,)

#     def post(self, request):
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         user_data = serializer.data
#         user = SuperAdmin.objects.get(email=user_data['email'])
#         token = RefreshToken.for_user(user).access_token
#         tokens = get_tokens_for_user(user)
#         return Response({"user_data": user_data, "tokens": tokens }, status=status.HTTP_201_CREATED)


# class OrgRegistrationView(generics.GenericAPIView):

#     serializer_class = OrgRegistrationSerializer
#     renderer_classes = (UserRenderer,)

#     def post(self, request):
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         user_data = serializer.data
#         user = Organization.objects.get(email=user_data['email'])
#         token = RefreshToken.for_user(user).access_token
#         tokens = get_tokens_for_user(user)
#         return Response({"user_data": user_data, "tokens": tokens }, status=status.HTTP_201_CREATED)

# class OrganizationAdminCreateView(generics.GenericAPIView):

#     serializer_class = OrganizationAdminCreteSerializer
#     renderer_classes = (UserRenderer,)
#     permission_classes = [
#             IsAuthenticated,
#     ]

#     def post(self, request):
#         password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
#         print(password)
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(password=(password))
        
        
#         user_data = serializer.data
#         user = Organization.objects.get(email=user_data['email'])
#         Organization.objects.filter(email=user_data['email']).update(created_by=SuperAdmin.objects.get(user=request.user.superadmin))
#         email_body = f"Your Email is : {user_data['email']} \n Your Password is: {password}"
#         email = EmailMessage(subject='Activate your account', body=email_body, from_email=settings.EMAIL_HOST_USER, to=[user_data['email']])
#         email.content_subtype = 'html'
#         EmailThread(email).start()
#         token = RefreshToken.for_user(user).access_token
#         tokens = get_tokens_for_user(user)
#         return Response({"user_data": user_data, "tokens": tokens }, status=status.HTTP_201_CREATED)


# class LoginAPIView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validate(request.data)
#         dict=serializer.data
#         # print(dict)
#         email = dict['email']
#         print(email)
#         try:
#             user = SuperAdmin.objects.filter(email=email).values()
#             users = SuperAdmin.objects.get(email=email)
#             for i in user:
#                 verified = i['verified']
#             if verified != "True":
#                 token = RefreshToken.for_user(users).access_token
#                 tokens = get_tokens_for_user(users)
            
#             print(verified)
#         except:
#             pass
#         try:
#             user = Organization.objects.filter(email=email).values()
#             users = Organization.objects.get(email=email)
#             for i in user:
#                 verified = i['verified']
#             if verified != "True":
#                 token = RefreshToken.for_user(users).access_token
#                 tokens = get_tokens_for_user(users)
            
#             print(verified)
#         except:
#             pass
#         dict.update({'type': data["type"],'userObj':data["userObj"]})
#         return Response(dict,status=status.HTTP_200_OK)

# class UserInfi(ListAPIView):
#     permission_classes = [
#             IsAuthenticated,
#     ]
#     serializer_class = OrganizationUserInfoSerializer
#     model = serializer_class.Meta.model
#     def get_queryset(self):
#         orefid = self.kwargs['orefid']
#         queryset = self.model.objects.filter(orefid=orefid)
#         # if (self.model.objects.filter(organization_permissions__title = 'Job Related')):
#         #     print("Have it")
#         return queryset

# class OrganizationUserAdminPermissions(APIView):
#     permission_classes = [
#             IsAuthenticated,
#     ]
#     def post(self, request):
#         permission = request.POST.get('permission')
#         if permission == "ADMIN":
#             return Response({"Permission": "ADMIN"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"Permission": "Not Allowed"},status=status.HTTP_423_LOCKED)

# class OrganizationUserJobPermissions(APIView):
#     permission_classes = [
#             IsAuthenticated,
#     ]
#     def post(self, request):
#         user = Organization.objects.filter(user = request.user).values()
#         if (user.filter(organization_permissions__title = 'Job Related')):
#             print("Do some thing")
#             return Response({"Permission": "Access"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"Permission": "Not Allowed"},status=status.HTTP_423_LOCKED)


# class CandidateRegistrationView(generics.GenericAPIView):

#     serializer_class = CandidateRegestrationSerializer
#     renderer_classes = (UserRenderer,)

#     def post(self, request, *args, **kwargs):
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         user_data = serializer.data
#         user = Candidate.objects.get(email=user_data['email'])
       
#         token = RefreshToken.for_user(user).access_token
#         tokens = get_tokens_for_user(user)
        
#         return Response({"user_data": user_data, "tokens": tokens }, status=status.HTTP_201_CREATED)

# class CLoginAPIView(generics.GenericAPIView):
#     serializer_class = CLoginSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validate(request.data)
#         dict=serializer.data
#         # print(dict)
#         email = dict['email']
#         print(email)
#         dict.update({'type': data["type"],'userObj':data["userObj"]})
#         return Response(dict,status=status.HTTP_200_OK)
