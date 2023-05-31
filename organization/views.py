import base64
from django.shortcuts import render
import pytz
from candidate.models import *
from job.models import *
from job.serializers import InterViewSeerializer
from .serializers import *
from .models import *
from accounts.renderers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
import jwt
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django.forms.models import model_to_dict
from rest_framework.views import APIView
import random
import string
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.conf import settings
import threading
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.template.loader import render_to_string, get_template
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from organization.models import OrganizationCalendarIntegration
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from notifications.signals import notify
from notifications.models import Notification


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class SuperAdminRegistrationView(generics.GenericAPIView):
    serializer_class = SuperAdminRegistrationSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = SuperAdmin.objects.get(email=user_data["email"])
        org_unique_id = OrganizationProfile.objects.get(user=user).unique_id
        token = RefreshToken.for_user(user).access_token
        tokens = get_tokens_for_user(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse("email-verify")
        # print(token)
        absurl = "http://" + current_site + relativeLink + "?token=" + str(token)
        # email_body = 'Hi '+user.name + \
        #     ' Use the link below to verify your email \n' + absurl
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Verify your email'}

        email_body = render_to_string(
            "verify-email.html",
            {
                "user": user.email,
                "absurl": absurl,
            },
        )
        # #print(absurl)
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Activate your account'}

        email = EmailMessage(
            subject="Activate your account",
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.content_subtype = "html"
        EmailThread(email).start()
        user_data["org_unique_id"] = org_unique_id
        return Response(
            {"user_data": user_data, "tokens": tokens}, status=status.HTTP_201_CREATED
        )


class ListOrganizationUserView(generics.ListAPIView):
    serializer_class = OrganizationListSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        # if SuperAdmin.objects.filter(user=self.request.user).exists():
        # user = self.request.user
        queryset = self.model.objects.filter(created_by=user)
        return queryset


class OrgRegistrationView(generics.GenericAPIView):
    serializer_class = OrgRegistrationSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = Organization.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user).access_token
        tokens = get_tokens_for_user(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse("email-verify")
        # print(token)
        absurl = "http://" + current_site + relativeLink + "?token=" + str(token)
        # email_body = 'Hi '+user.name + \
        #     ' Use the link below to verify your email \n' + absurl
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Verify your email'}

        email_body = render_to_string(
            "verify-email.html",
            {
                "user": user.email,
                "absurl": absurl,
            },
        )
        # #print(absurl)
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Activate your account'}

        email = EmailMessage(
            subject="Activate your account",
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.content_subtype = "html"
        EmailThread(email).start()
        return Response(
            {"user_data": user_data, "tokens": tokens}, status=status.HTTP_201_CREATED
        )


class OrganizationAdminCreateView(generics.GenericAPIView):
    serializer_class = OrganizationAdminCreteSerializer
    renderer_classes = (UserRenderer,)
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        password = "".join(
            random.choice(string.ascii_letters + string.digits) for i in range(8)
        )
        print(password)
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save(password=(password))

        user_data = serializer.data
        user = Organization.objects.get(email=user_data["email"])
        Organization.objects.filter(email=user_data["email"]).update(
            created_by=SuperAdmin.objects.get(user=request.user.superadmin)
        )
        email_body = (
            f"Your Email is : {user_data['email']} \n Your Password is: {password}"
        )
        email = EmailMessage(
            subject="Activate your account",
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_data["email"]],
        )
        email.content_subtype = "html"
        EmailThread(email).start()
        token = RefreshToken.for_user(user).access_token
        tokens = get_tokens_for_user(user)
        return Response(
            {"user_data": user_data, "tokens": tokens}, status=status.HTTP_201_CREATED
        )

    def put(self, request, pk, format=None):
        link = Organization.objects.get(pk=pk)
        print(link)
        serializer = OrganizationUpdateSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validate(request.data)
        dict = serializer.data
        # print(dict)
        email = dict["email"]
        print(email)
        try:
            user = SuperAdmin.objects.filter(email=email).values()
            users = SuperAdmin.objects.get(email=email)
            for i in user:
                verified = i["verified"]
            if verified != "True":
                token = RefreshToken.for_user(users).access_token
                tokens = get_tokens_for_user(users)

            print(verified)
        except:
            pass
        try:
            user = Organization.objects.filter(email=email).values()
            users = Organization.objects.get(email=email)
            for i in user:
                verified = i["verified"]
            if verified != "True":
                token = RefreshToken.for_user(users).access_token
                tokens = get_tokens_for_user(users)

            print(verified)
        except:
            pass
        dict.update(
            {"type": data["type"], "role": data["role"], "userObj": data["userObj"]}
        )
        return Response(dict, status=status.HTTP_200_OK)


class UserInfi(ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = OrganizationUserInfoSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        orefid = self.kwargs["orefid"]
        queryset = self.model.objects.filter(orefid=orefid)
        # if (self.model.objects.filter(organization_permissions__title = 'Job Related')):
        #     print("Have it")
        return queryset


class OrganizationUserAdminPermissions(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        permission = request.POST.get("permission")
        if permission == "ADMIN":
            return Response({"Permission": "ADMIN"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"Permission": "Not Allowed"}, status=status.HTTP_423_LOCKED
            )


class OrganizationUserJobPermissions(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        user = Organization.objects.filter(user=request.user).values()
        if user.filter(organization_permissions__title="Job Related"):
            print("Do some thing")
            return Response({"Permission": "Access"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"Permission": "Not Allowed"}, status=status.HTTP_423_LOCKED
            )


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        # print(token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # print('payload ', payload)
        try:
            # print("hello")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # print("Paylod:", payload)
            # if Candidate.objects.filter(id=payload['user_id']).exists():
            #     user = Candidate.objects.get(id=payload['user_id'])
            #     #print(user.first_name)
            #     if not user.verified:
            #         user.verified = True
            #         user.save()

            #         email_body = render_to_string('cand-login-welcome.html',{
            #             'fname': user.first_name,
            #             'lname': user.last_name,
            #         })
            #         # #print(absurl)
            #         # data = {'email_body': email_body, 'to_email': user.email,
            #         #         'email_subject': 'Activate your account'}

            #         email = EmailMessage(subject='Welcome to Somhako', body=email_body, from_email=settings.EMAIL_HOST_USER, to=[user.email])
            #         email.content_subtype = 'html'
            #         EmailThread(email).start()

            #     return HttpResponseRedirect(redirect_to='https://somhako.com/marketplace/auth/signin/')
            if SuperAdmin.objects.filter(id=payload["user_id"]).exists():
                user = SuperAdmin.objects.get(id=payload["user_id"])
                # print(user)
                if not user.verified:
                    user.verified = True
                    user.save()
                    # print(user)
                    email_body = render_to_string(
                        "recruiter-login.html",
                        {
                            "cname": user.company_name,
                            "email": user.email,
                        },
                    )
                    # #print(absurl)
                    # data = {'email_body': email_body, 'to_email': user.email,
                    #         'email_subject': 'Activate your account'}

                    email = EmailMessage(
                        subject="Welcome to Somhako",
                        body=email_body,
                        from_email=settings.EMAIL_HOST_USER,
                        to=[user.email],
                    )
                    email.content_subtype = "html"
                    EmailThread(email).start()

                return HttpResponseRedirect(
                    redirect_to="https://somhako.com/marketplace/auth/signin/"
                )
            else:
                return Response({"email": "Not Activated"}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


# Org Profile


class OrganizationProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrganizationProfileSerializer

    def put(self, request, format=None):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        print("---------")
        print(user)
        link = OrganizationProfile.objects.get(user=user)
        print(link)
        serializer = OrganizationProfileSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListOrganizationProfileView(generics.ListAPIView):
    serializer_class = ListOrganizationProfileSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        queryset = self.model.objects.filter(user=user)
        return queryset


class ListOrganizationAccountView(generics.ListAPIView):
    serializer_class = ListOrganizationAccountSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        user = self.request.user
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            queryset = self.model.objects.filter(user=user)
        queryset = self.model.objects.filter(created_by=user)
        print(queryset)
        print(user)
        return queryset


# Individual Profile


class IndividualProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IndividualProfileSerializer

    def put(self, request, format=None):
        user = self.request.user
        link = IndividualProfile.objects.get(user=user)
        serializer = IndividualProfileSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListIndividualProfileView(generics.ListAPIView):
    serializer_class = ListIndividualProfileSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(user=user)
        return queryset


# Individual Links


class IndividualLinkView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IndividualLinkSerializer

    def post(self, request, uniqueid, format=None):
        link = IndividualLink.objects.create(
            individualProfile=IndividualProfile.objects.get(unique_id=uniqueid)
        )
        serializer = IndividualLinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, uniqueid, pk, format=None):
        link = IndividualLink.objects.get(
            individualProfile=IndividualProfile.objects.get(unique_id=uniqueid), pk=pk
        )
        serializer = IndividualLinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uniqueid, pk, *args, **kwargs):
        link = IndividualLink.objects.get(
            individualProfile=IndividualProfile.objects.get(unique_id=uniqueid), pk=pk
        )
        link.delete()
        return Response({"msg": "Deleted"}, status=204)


class ListIndividualLinkView(generics.ListAPIView):
    serializer_class = ListIndividualLinkSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        uniqueid = self.kwargs["uniqueid"]
        queryset = self.model.objects.filter(
            individualProfile=IndividualProfile.objects.get(unique_id=uniqueid)
        )
        return queryset


class OrganizationGalleryAPIView(APIView):
    serializer_class = OrganizationGallerySerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def post(self, request, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        gal = OrganizationGallery.objects.create(
            organizationProfile=OrganizationProfile.objects.get(user=user)
        )

        serializer = OrganizationGallerySerializer(gal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        gal = OrganizationGallery.objects.get(
            organizationProfile=OrganizationProfile.objects.get(user=user), pk=pk
        )
        gal.delete()
        return Response({"msg": "Deleted"}, status=204)


class ListOrganizationGalleryView(generics.ListAPIView):
    serializer_class = ListOrganizationGallerySerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        queryset = self.model.objects.filter(
            organizationProfile=OrganizationProfile.objects.get(user=user)
        )
        return queryset


class OrganizationFounderAPIView(APIView):
    serializer_class = OrganizationFounderSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def post(self, request, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        gal = OrganizationFounder.objects.create(
            organizationProfile=OrganizationProfile.objects.get(user=user)
        )

        serializer = OrganizationFounderSerializer(gal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        gal = OrganizationFounder.objects.get(
            organizationProfile=OrganizationProfile.objects.get(user=user), pk=pk
        )

        serializer = OrganizationFounderSerializer(gal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        gal = OrganizationFounder.objects.get(
            organizationProfile=OrganizationProfile.objects.get(user=user), pk=pk
        )
        gal.delete()
        return Response({"msg": "Deleted"}, status=204)


class ListOrganizationFounderView(generics.ListAPIView):
    serializer_class = ListOrganizationFounderSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        queryset = self.model.objects.filter(
            organizationProfile=OrganizationProfile.objects.get(user=user)
        )
        return queryset


class CarrierOrgView1(APIView):
    def get(self, request, cname, format=None):
        user = SuperAdmin.objects.get(company_name=cname)
        queryset1 = OrganizationProfile.objects.filter(user=user)
        data = {
            "oprofiledata": queryset1,
        }
        serializer = OrgProfileCarrierSerializer1(data)
        return Response(serializer.data)


class CarrierOrgView(APIView):
    def get(self, request, unique_id, format=None):
        queryset1 = OrganizationProfile.objects.filter(unique_id=unique_id)
        queryset2 = OrganizationGallery.objects.filter(
            organizationProfile=OrganizationProfile.objects.get(unique_id=unique_id)
        )
        queryset3 = OrganizationFounder.objects.filter(
            organizationProfile=OrganizationProfile.objects.get(unique_id=unique_id)
        )
        data = OrganizationProfile.objects.filter(unique_id=unique_id).values()
        for i in data:
            user_id = i["user_id"]
        queryset4 = Job.objects.filter(
            user=SuperAdmin.objects.get(pk=user_id), jobStatus="Active"
        ).order_by("-publish_date")

        data = {
            "oprofiledata": queryset1,
            "gallerydata": queryset2,
            "founderdata": queryset3,
            "jobdata": queryset4,
        }
        serializer = OrgProfileCarrierSerializer(data)
        return Response(serializer.data)


class CarrierOrgView3(APIView):
    def get(self, request, pk, format=None):
        user = SuperAdmin.objects.get(pk=pk)
        queryset1 = OrganizationProfile.objects.filter(user=user)
        queryset2 = OrganizationGallery.objects.filter(
            organizationProfile=OrganizationProfile.objects.get(user=user)
        )
        queryset3 = OrganizationFounder.objects.filter(
            organizationProfile=OrganizationProfile.objects.get(user=user)
        )
        data = OrganizationProfile.objects.filter(user=user).values()
        for i in data:
            user_id = i["user_id"]
        queryset4 = Job.objects.filter(
            user=SuperAdmin.objects.get(pk=user_id), jobStatus="Active"
        ).order_by("-publish_date")

        data = {
            "oprofiledata": queryset1,
            "gallerydata": queryset2,
            "founderdata": queryset3,
            "jobdata": queryset4,
        }
        serializer = OrgProfileCarrierSerializer(data)
        return Response(serializer.data)


class ListOrganizationAccountAndProfilesView(APIView):
    def get(self, request):
        user = request.user

        organizationAccounts = Organization.objects.filter(created_by=user)

        individualProfiles = IndividualProfile.objects.none()

        for organization in organizationAccounts:
            individualProfile = IndividualProfile.objects.filter(user=organization.user)

            individualProfiles = individualProfiles | individualProfile

        data = {
            "organizationAccounts": organizationAccounts,
            "individualProfiles": individualProfiles,
        }

        serializer = ListOrganizationAccountAndIndividualProfileSerializer(data)
        return Response(serializer.data)


@require_POST
@csrf_exempt
def create_calendar_integration(request, unique_id: str):
    newIntegrationData = json.loads(request.body)

    try:
        prevIntegration = OrganizationCalendarIntegration.objects.get(
            organization_id=unique_id, provider=newIntegrationData["provider"]
        )
        if prevIntegration:
            prevIntegration.delete()
    except OrganizationCalendarIntegration.DoesNotExist:
        """"""

    newIntegration = OrganizationCalendarIntegration.objects.create(
        organization_id=unique_id,
        expires_in=newIntegrationData["expires_in"],
        access_token=newIntegrationData["access_token"],
        refresh_token=newIntegrationData["refresh_token"],
        scope=newIntegrationData["scope"],
        provider=newIntegrationData["provider"],
        calendar_id=newIntegrationData["calendar_id"],
    )

    newIntegration.save()

    return HttpResponse(
        json.dumps({"success": True, "newIntegration": model_to_dict(newIntegration)}),
        content_type="application/json",
    )


@csrf_exempt
def delete_calendar_integration(request, integration_id: int):
    OrganizationCalendarIntegration.objects.get(id=integration_id).delete()

    return JsonResponse({"success": True})


def get_calendar_integration(request, unique_id: str):
    for integration in OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ).values()

    return JsonResponse({"integrations": list(integrations)})


@csrf_exempt
def create_mail_integration(request, unique_id: str):
    newIntegrationData = json.loads(request.body)

    try:
        prevIntegration = OrganizationMailIntegration.objects.get(
            organization_id=unique_id, provider=newIntegrationData["provider"]
        )
        if prevIntegration:
            prevIntegration.delete()
    except OrganizationMailIntegration.DoesNotExist:
        """"""

    newIntegration = OrganizationMailIntegration.objects.create(
        organization_id=unique_id,
        expires_in=newIntegrationData["expires_in"],
        access_token=newIntegrationData["access_token"],
        refresh_token=newIntegrationData["refresh_token"],
        scope=newIntegrationData["scope"],
        provider=newIntegrationData["provider"],
        label_id=newIntegrationData["label_id"],
    )

    newIntegration.save()

    return HttpResponse(
        json.dumps({"success": True, "newIntegration": model_to_dict(newIntegration)}),
        content_type="application/json",
    )


@csrf_exempt
def delete_mail_integration(request, integration_id: int):
    OrganizationMailIntegration.objects.get(id=integration_id).delete()

    return JsonResponse({"success": True})


def get_mail_integration(request, unique_id: str):
    for integration in OrganizationMailIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationMailIntegration.objects.filter(
        organization_id=unique_id
    ).values()

    return JsonResponse({"integrations": list(integrations)})


from datetime import datetime, timedelta
import pickle
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from uuid import uuid4
from rest_framework.decorators import api_view

from googleapiclient.errors import HttpError


@api_view(["PUT"])
def calander_automation(request, unique_id: str, arefid: str):
    app = Applicant.objects.filter(arefid=arefid).values()
    for i in app:
        pk = i["user_id"]
        jobpk = i["job_id"]
    cand = Candidate.objects.filter(pk=pk).values()
    job = Job.objects.filter(pk=jobpk).values()
    for i in cand:
        email = i["email"]
        fname = i["first_name"]
        lname = i["last_name"]
    print(fname)
    for i in job:
        title = i["job_title"]
    if not OrganizationCalendarIntegration.objects.filter(organization_id=unique_id):
        return JsonResponse({"message": "Not Integrated"})
    for integration in OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ).values()
    calendar = integrations[0]

    access_token = calendar["access_token"]
    refresh_token = calendar["refresh_token"]
    is_expired = calendar["is_expired"]
    provider = calendar["provider"]
    scope = calendar["scope"]
    calendar_id = calendar["calendar_id"]
    if is_expired:
        return JsonResponse({"Message": "Sorry Experied"})
    else:
        creds = Credentials.from_authorized_user_info(
            info={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "client_id": "249513300153-tas5kilecjdnnucio144mce492je1hg6.apps.googleusercontent.com",
                "client_secret": "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",
            }
        )
        service = build("calendar", "v3", credentials=creds)

        if request.POST.get("stime") and request.POST.get("etime"):
            start_time = request.POST.get("stime")
            end_time = request.POST.get("etime")
        else:
            start_time = (
                datetime.now(tz=pytz.timezone("Asia/Kolkata")) + timedelta(hours=2)
            ).isoformat()
            end_time = (
                datetime.now(tz=pytz.timezone("Asia/Kolkata")) + timedelta(hours=3)
            ).isoformat()
        print(start_time, end_time)
        if request.POST.get("summary"):
            summary = request.POST.get("summary")
        else:
            summary = "Automating calendar"
        if request.POST.get("desc"):
            desc = request.POST.get("desc")
        else:
            desc = f"This is a Automation mail for meet in {title} for {fname} {lname} Candidate"
        org = OrganizationProfile.objects.filter(unique_id=unique_id).values()
        for i in org:
            user_id = i["user_id"]
        user_emails = User.objects.filter(id=user_id).values()
        for i in user_emails:
            user_email = i["email"]
        if user_email and len(user_email) > 0:
            attendees = [email, user_email]
        else:
            attendees = [email]
        event = {
            "summary": summary,
            "description": desc,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
            "attendees": [{"email": attendee} for attendee in attendees],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"{uuid4}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {
                "useDefault": True,
            },
        }
        print(start_time)
        print("-------------------------")
        print(end_time)
        print("-------------------------------")
        print(Job.objects.get(pk=jobpk))
        print(request.user)

        event = (
            service.events()
            .insert(
                calendarId=calendar_id,
                conferenceDataVersion=1,
                body=event,
                sendUpdates="all",
                sendNotifications=True,
            )
            .execute()
        )
        CandidateInterview.objects.create(
            applicant=Applicant.objects.get(arefid=arefid),
            job=Job.objects.get(pk=jobpk),
            date_time_from=start_time,
            date_time_to=end_time,
            link=event["hangoutLink"],
            org=OrganizationProfile.objects.get(unique_id=unique_id),
            interview_name=summary,
            description=desc,
            user=request.user,
        )
        return JsonResponse(
            {"data": {"event_id": event["id"], "calendar_id": calendar_id}}
        )


@csrf_exempt
def update_calander_automation(
    request, unique_id: str, event_id: str, calendar_id: str
):
    for integration in OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ).values()
    calendar = integrations[0]

    access_token = calendar["access_token"]
    refresh_token = calendar["refresh_token"]
    is_expired = calendar["is_expired"]
    provider = calendar["provider"]
    scope = calendar["scope"]
    calendar_id = calendar["calendar_id"]
    if is_expired:
        return JsonResponse({"Message": "Sorry Experied"})
    else:
        creds = Credentials.from_authorized_user_info(
            info={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "client_id": "249513300153-tas5kilecjdnnucio144mce492je1hg6.apps.googleusercontent.com",
                "client_secret": "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",
            }
        )
        service = build("calendar", "v3", credentials=creds)
        summary = request.POST.get("summary")
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event["summary"] = summary
        updated_event = (
            service.events()
            .update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates="all",
                sendNotifications=True,
            )
            .execute()
        )

        return JsonResponse(
            {"data": {"event_id": event["id"], "calendar_id": calendar_id}}
        )


def calendar_choose_slots(request, unique_id: str):
    if not OrganizationCalendarIntegration.objects.filter(organization_id=unique_id):
        return JsonResponse({"message": "Not Integrated"})
    for integration in OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationCalendarIntegration.objects.filter(
        organization_id=unique_id
    ).values()
    calendar = integrations[0]

    access_token = calendar["access_token"]
    refresh_token = calendar["refresh_token"]
    is_expired = calendar["is_expired"]
    provider = calendar["provider"]
    scope = calendar["scope"]
    calendar_id = calendar["calendar_id"]
    if is_expired:
        return JsonResponse({"Message": "Sorry Experied"})
    else:
        creds = Credentials.from_authorized_user_info(
            info={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "client_id": "249513300153-tas5kilecjdnnucio144mce492je1hg6.apps.googleusercontent.com",
                "client_secret": "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",
            }
        )
        service = build("calendar", "v3", credentials=creds)
        d = datetime.now().date()
        start_utc_time = datetime(
            d.year, d.month, d.day, 10, 0, 0, tzinfo=pytz.timezone("UTC")
        ) + timedelta(days=1)
        start_time = start_utc_time.astimezone(pytz.timezone("Asia/Kolkata"))
        end_time = start_time + timedelta(hours=1)

        if start_time:
            while True:
                print("Start")
                # Use the Google Calendar API to get a list of events during the time slot we want
                events_result = (
                    service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=start_time.isoformat(),
                        timeMax=end_time.isoformat(),
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = events_result.get("items", [])
                print(events)

                # If there are no collisions, create the event and return
                if events == []:
                    stime = start_time.isoformat()
                    etime = end_time.isoformat()
                    start_date_time = start_time.strftime("%m/%d/%Y, %I:%M:%S %p")
                    end_date_time = end_time.strftime("%m/%d/%Y, %I:%M:%S %p")
                    # CandidateInterview.objects.create(applicant=Applicant.objects.filter(arefid=arefid), job=Job.objects.filter(pk=jobpk), date_time=f"{start_time} to {end_time}")
                    return JsonResponse(
                        {
                            "Start Time": stime,
                            "End Time": etime,
                            "Simple Start Date": start_date_time,
                            "Simple End Date": end_date_time,
                        }
                    )

                start_time = end_time
                end_time = start_time + timedelta(hours=1)

        return JsonResponse({"n": 1})


from bs4 import BeautifulSoup


@csrf_exempt
def email_inbox(request, unique_id: str):
    emails = request.POST.get("email")
    if not OrganizationMailIntegration.objects.filter(organization_id=unique_id):
        return JsonResponse({"message": "Not Integrated"})
    for integration in OrganizationMailIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationMailIntegration.objects.filter(
        organization_id=unique_id
    ).values()
    calendar = integrations[0]

    access_token = calendar["access_token"]
    refresh_token = calendar["refresh_token"]
    is_expired = calendar["is_expired"]
    provider = calendar["provider"]
    scope = calendar["scope"]
    if is_expired:
        return JsonResponse({"Message": "Sorry Experied"})
    else:
        creds = Credentials.from_authorized_user_info(
            info={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "client_id": "249513300153-tas5kilecjdnnucio144mce492je1hg6.apps.googleusercontent.com",
                "client_secret": "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",
            }
        )
        service = build("gmail", "v1", credentials=creds)
        query = f"from:{emails}"

        user_id = "me"
        messages = []
        page_token = None
        while True:
            response = (
                service.users()
                .messages()
                .list(userId=user_id, q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        for message in messages:
            message_id = message["id"]
            message_details = (
                service.users().messages().get(userId=user_id, id=message_id).execute()
            )
            print(f"From: {message_details['payload']['headers'][1]['value']}")
            print(f"To: {message_details['payload']['headers'][2]['value']}")
            print(f"Subject: {message_details['payload']['headers'][3]['value']}")
            print(f"Body: {message_details['snippet']}")
            print("=" * 50)

        return JsonResponse({"data": 1})


from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


@csrf_exempt
def email_inbox_send(request, unique_id: str):
    emails = request.POST.get("email")
    sub = request.POST.get("subject")
    body = request.POST.get("body")
    if not OrganizationMailIntegration.objects.filter(organization_id=unique_id):
        return JsonResponse({"message": "Not Integrated"})
    for integration in OrganizationMailIntegration.objects.filter(
        organization_id=unique_id
    ):
        if integration.expired:
            integration.is_expired = True
            integration.save()

    integrations = OrganizationMailIntegration.objects.filter(
        organization_id=unique_id
    ).values()
    calendar = integrations[0]

    access_token = calendar["access_token"]
    refresh_token = calendar["refresh_token"]
    is_expired = calendar["is_expired"]
    provider = calendar["provider"]
    scope = calendar["scope"]
    if is_expired:
        return JsonResponse({"Message": "Sorry Experied"})
    else:
        creds = Credentials.from_authorized_user_info(
            info={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "client_id": "249513300153-tas5kilecjdnnucio144mce492je1hg6.apps.googleusercontent.com",
                "client_secret": "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",
            }
        )
        service = build("gmail", "v1", credentials=creds)
        message = MIMEMultipart()
        message["to"] = emails
        message["subject"] = sub
        message.attach(MIMEText(body))

        try:
            create_message = {"raw": urlsafe_b64encode(message.as_bytes()).decode()}
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(
                f'The email was sent to {message["to"]}. Message Id: {send_message["id"]}'
            )
        except HttpError as error:
            print(f"An error occurred: {error}")

        return JsonResponse({"data": 1})


from django.utils import timezone


class DashboardCandidatesApiView(APIView):
    serializer_class = ListOrganizationFounderSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def get(self, request, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)

        # dashboard applicant

        job = Job.objects.filter(user=user)
        app = Applicant.objects.filter(job__in=job)
        vend_app = VendorApplicant.objects.filter(job__in=job)

        totalApplicants = app.count() + vend_app.count()

        app = Applicant.objects.filter(job__in=job).filter(status="Sourced").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job).filter(status="Sourced").count()
        )
        sourced = app + vend_app

        app = Applicant.objects.filter(job__in=job).filter(status="Applied").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job).filter(status="Applied").count()
        )
        applied = app + vend_app

        app = (
            Applicant.objects.filter(job__in=job).filter(status="Phone Screen").count()
        )
        vend_app = (
            VendorApplicant.objects.filter(job__in=job)
            .filter(status="Phone Screen")
            .count()
        )
        phoneScreen = app + vend_app

        app = Applicant.objects.filter(job__in=job).filter(status="Assessment").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job)
            .filter(status="Assessment")
            .count()
        )
        assessment = app + vend_app

        app = Applicant.objects.filter(job__in=job).filter(status="Interview").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job)
            .filter(status="Interview")
            .count()
        )
        interview = app + vend_app

        app = Applicant.objects.filter(job__in=job).filter(status="Offer").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job).filter(status="Offer").count()
        )
        offer = app + vend_app

        app = Applicant.objects.filter(job__in=job).filter(status="Hired").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job).filter(status="Hired").count()
        )
        hired = app + vend_app

        app = Applicant.objects.filter(job__in=job).filter(status="Rejected").count()
        vend_app = (
            VendorApplicant.objects.filter(job__in=job)
            .filter(status="Rejected")
            .count()
        )
        rejected = app + vend_app

        applicants = {}
        applicants["totalApplicants"] = totalApplicants
        applicants["sourced"] = sourced
        applicants["applied"] = applied
        applicants["phoneScreen"] = phoneScreen
        applicants["assessment"] = assessment
        applicants["interview"] = interview
        applicants["offer"] = offer
        applicants["hired"] = hired
        applicants["rejected"] = rejected

        # dashboard --->
        # #dashboard recent job

        recentJob = Job.objects.filter(user=user, jobStatus="Active").order_by(
            "-timestamp"
        )

        recentJobSerializer = ListJobSerializer(recentJob, many=True)
        # #dashboard recent job --->

        appli = Applicant.objects.filter(job__in=job)

        date_now = timezone.now()

        inter = CandidateInterview.objects.filter(applicant__in=appli).filter(
            date_time_from__gt=date_now
        )

        jobs = Job.objects.filter(user=user)

        all_jobs = {}
        all_jobs["total"] = jobs.count()
        all_jobs["Active"] = jobs.filter(jobStatus="Active").count()
        all_jobs["Archive"] = jobs.filter(jobStatus="Archive").count()
        all_jobs["Draft"] = jobs.filter(jobStatus="Draft").count()
        all_jobs["Close"] = jobs.filter(jobStatus="Close").count()

        serializer = InterViewSeerializer(inter, many=True)

        return Response(
            {
                "Applicants": applicants,
                "Interview": serializer.data,
                "Jobs": all_jobs,
                "recentJob": recentJobSerializer.data,
            }
        )


class ActivityLogView(APIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if SuperAdmin.objects.filter(user=request.user).exists():
            org_user = request.user
        elif Organization.objects.filter(user=request.user).exists():
            sadmin = Organization.objects.filter(user=request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]
            org_user = SuperAdmin.objects.get(pk=sadmin_key)
        activity = ActivityLog.objects.create(
            user=user, org=OrganizationProfile.objects.get(user=org_user)
        )
        serializer = ActivityLogSerializer(activity, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"Msg": "Activity Log Added"}, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)


class ActivityLogView2(APIView):
    serializer_class = ActivityLogSerializer

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        user = User.objects.get(email=email)
        if SuperAdmin.objects.filter(user=user).exists():
            org_user = user
        elif Organization.objects.filter(user=user).exists():
            sadmin = Organization.objects.filter(user=user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]
            org_user = SuperAdmin.objects.get(pk=sadmin_key)
        activity = ActivityLog.objects.create(
            user=user, org=OrganizationProfile.objects.get(user=org_user)
        )
        serializer = ActivityLogSerializer(activity, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"Msg": "Activity Log Added"}, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)


class ListingActivityLogView(generics.ListAPIView):
    serializer_class = ListActivityLogSerializer
    model = serializer_class.Meta.model

    # paginate_by = 100
    def get_queryset(self):
        user = self.request.user
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            self.model.objects.filter(
                org=OrganizationProfile.objects.get(user=user)
            ).order_by("-timestamp")
        elif Organization.objects.filter(user=self.request.user).exists():
            queryset = self.model.objects.filter(user=user).order_by("-timestamp")

        # if SuperAdmin.objects.filter(user=self.request.user).exists():
        #     user = self.request.user
        # elif Organization.objects.filter(user=self.request.user).exists():
        #     sadmin = Organization.objects.filter(user=self.request.user).values()
        #     for i in sadmin:
        #         sadmin_key = i['created_by_id']

        #     user = SuperAdmin.objects.get(pk=sadmin_key)
        # queryset = self.model.objects.filter(org=OrganizationProfile.objects.get(user=user)).order_by("-timestamp")
        return queryset
