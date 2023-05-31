from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    GenericAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from organization.models import *
from job.models import *
from accounts.renderers import *

# Create your views here.
class NewVendorApiView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NewVendorSerializer

    def post(self, request, format=None):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
            user = SuperAdmin.objects.get(user=user)
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        organization = OrganizationProfile.objects.get(user=user)
        print(user)
        vend = NewVendor.objects.create(user=user, organization=organization)
        print(vend)
        serializer = NewVendorSerializer(vend, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # print(request.data)
            print("Valid")
            # print(request.data['email'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VendorDataView(ListAPIView):
    serializer_class = VendorDataSerializer
    model = serializer_class.Meta.model
    def get_queryset(self):
        vrefid = self.kwargs['vrefid']
        queryset = self.model.objects.filter(vrefid=vrefid)
        return queryset
    
class VendorDataView1(ListAPIView):
    serializer_class = VendorDataSerializer
    model = serializer_class.Meta.model
    def get_queryset(self):
        email = self.kwargs['email']
        queryset = self.model.objects.filter(email=email)
        return queryset
    
class VendorDataView2(ListAPIView):
    serializer_class = OnboardVendorSerailizer
    model = serializer_class.Meta.model
    def get_queryset(self):
        vrefid = self.kwargs['vrefid']
        queryset = self.model.objects.filter(vendor=NewVendor.objects.get(vrefid=vrefid))
        return queryset
    
class VendorDataView3(ListAPIView):
    serializer_class = ListJobSerializer
    model = serializer_class.Meta.model
    def get_queryset(self):
        vrefid = self.kwargs['vrefid']
        queryset = self.model.objects.filter(vendor=NewVendor.objects.get(vrefid=vrefid),jobStatus="Active")
        return queryset

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }    
    
class VendorRegistrationView(GenericAPIView):

    serializer_class = VendorRegestrationSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request, vrefid):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = VendorRegistration.objects.get(email=user_data['email'])
        VendorRegistration.objects.filter(email=user_data['email']).update(vendor=NewVendor.objects.get(vrefid=vrefid))
        NewVendor.objects.filter(vrefid=vrefid).update(verified=True)
        token = RefreshToken.for_user(user).access_token
        tokens = get_tokens_for_user(user)
        return Response({"user_data": user_data, "tokens": tokens }, status=status.HTTP_201_CREATED)
    
class VendorLoginAPIView(GenericAPIView):
    serializer_class = VendorLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validate(request.data)
        dict=serializer.data
        # print(dict)
        email = dict['email']
        print(email)
        dict.update({'type': data["type"],'role': data["role"],'userObj':data["userObj"]})
        return Response(dict,status=status.HTTP_200_OK)
    
class ListVendorApiView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorDataSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
            user = SuperAdmin.objects.get(user=user)
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        organization = OrganizationProfile.objects.get(user=user)
        
        queryset = self.model.objects.filter(organization = organization).order_by('-verified')
        return queryset
    
class ActivateVendorApiView(GenericAPIView):
    serializer_class = VendorDataSerializer
    
    def post(self, request, vrefid):
        vendor = NewVendor.objects.filter(vrefid = vrefid)
        activate = request.POST.get('activate')
        if activate == "true":
            activate = True
        else:
            activate = False
        if NewVendor.objects.filter(vrefid = vrefid, verified=True):
            NewVendor.objects.filter(vrefid = vrefid).update(activate=activate)
            return Response({"message": "Update Successfully"})
        else:
            return Response({"message": "Update Failed"})
    
class OnboardVendorApiView(GenericAPIView):
    serializer_class = OnboardVendorSerailizer
    
    def post(self, request, vrefid):
        vendor = NewVendor.objects.filter(vrefid = vrefid)
        if NewVendor.objects.filter(vrefid = vrefid, verified=True):
            NewVendor.objects.filter(vrefid = vrefid).update(onboard=True,activate=True)
            return Response({"message": "Onboard Successfully"})
        else:
            return Response({"message": "Onboard Failed"})
        
class OnboardVendorListApiView(ListAPIView):
    serializer_class = OnboardVendorSerailizer
    model = serializer_class.Meta.model
    def get_queryset(self):
        unique_id = self.kwargs['unique_id']
        organization = OrganizationProfile.objects.get(unique_id = unique_id)
        vendors = NewVendor.objects.filter(organization = organization, verified = True, onboard = True)
        queryset = self.model.objects.filter(vendor__in = vendors)
        return queryset
    
class VendorCandidateProfileView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorCandidateProfileSerializer

    def post(self, request, refid, vrefid, format=None):
        vendor = NewVendor.objects.get(vrefid=vrefid)
        print(vendor)
        print("--------")
        job = Job.objects.get(refid = refid)
        email = request.POST.get('email')
        if VendorCandidateProfile.objects.filter(vendor=vendor,job=job,email=email).exists():
            return Response({'msg': 'Entry Already Exist'},status=204)
        else:
            vendorcandidateprofile = VendorCandidateProfile.objects.create(vendor=vendor,job=job)
            serializer = VendorCandidateProfileSerializer(vendorcandidateprofile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                vobj = VendorCandidateProfile.objects.filter(vendor=vendor,job=job,email=serializer.data["email"]).values()
                print(vobj)
                print("----------")
                return Response({"data": vobj}, status=status.HTTP_201_CREATED)
                # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, refid, vrefid, pk, format=None):
        vendor = NewVendor.objects.get(vrefid=vrefid)
        job = Job.objects.get(refid = refid)
        vendorcandidateprofile = VendorCandidateProfile.objects.get(vendor=vendor, pk=pk,job=job)
        serializer = VendorCandidateProfileSerializer(vendorcandidateprofile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, refid, vrefid,pk ,*args, **kwargs):
        vendor = NewVendor.objects.get(vrefid=vrefid)
        job = Job.objects.get(refid = refid)
        vendorcandidateprofile = VendorCandidateProfile.objects.get(vendor=vendor, pk=pk,job=job)
        vendorcandidateprofile.delete()
        return Response({'msg': 'Deleted'},status=204)
    

class VendorCandidateSocialLinkView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorCandidateSocialLinkSerializer

    def post(self, request,vcrefid, refid, format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        link = VendorCandidateSocialLink.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateSocialLinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,vcrefid,refid, pk, format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        link = VendorCandidateSocialLink.objects.get(user=vendor_candidate, pk=pk,job=job)
        serializer = VendorCandidateSocialLinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, vcrefid, refid, pk ,*args, **kwargs):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        link = VendorCandidateSocialLink.objects.get(user=vendor_candidate, pk=pk,job=job)
        link.delete()
        return Response({'msg': 'Deleted'},status=204)
    
class VendorCandidateCertificateView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorCandidateCertificateSerializer

    def post(self, request, vcrefid,refid,  format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        cert = VendorCandidateCertificate.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateCertificateSerializer(cert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, vcrefid,refid, pk, format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        cert = VendorCandidateCertificate.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateCertificateSerializer(cert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, vcrefid,refid,  pk ,*args, **kwargs):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        cert = VendorCandidateCertificate.objects.create(user=vendor_candidate,job=job)
        cert.delete()
        return Response({'msg': 'Deleted'},status=204)
    

class VendorCandidateEducationView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorCandidateEducationSerializer

    def post(self, request,vcrefid,refid,  format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        edu = VendorCandidateEducation.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateEducationSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, vcrefid,refid, pk, format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        edu = VendorCandidateEducation.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateEducationSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, vcrefid,refid,  pk ,*args, **kwargs):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        edu = VendorCandidateEducation.objects.create(user=vendor_candidate,job=job)
        edu.delete()
        return Response({'msg': 'Deleted'},status=204)
    
class VendorCandidateExperienceView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorCandidateExperienceSerializer

    def post(self, request,vcrefid,refid,  format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        edu = VendorCandidateExperience.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateExperienceSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, vcrefid,refid, pk, format=None):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        edu = VendorCandidateExperience.objects.create(user=vendor_candidate,job=job)
        serializer = VendorCandidateExperienceSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, vcrefid,refid,  pk ,*args, **kwargs):
        vendor_candidate = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)
        edu = VendorCandidateExperience.objects.create(user=vendor_candidate,job=job)
        edu.delete()
        return Response({'msg': 'Deleted'},status=204)

 
class VendorApplicantApplyView(GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, refid, vrefid, vcrefid):
        new_vendor = NewVendor.objects.get(vrefid=vrefid)
        job = Job.objects.get(refid = refid)
        profile = VendorCandidateProfile.objects.get(vcrefid=vcrefid)
        # applicant = VendorApplicant.objects.filter()
        if VendorApplicant.objects.filter(vendor=new_vendor, job=job, applicant=profile).exists():
            return Response({"Message": "Already Applied"}) 
        else:
            applicant = VendorApplicant.objects.create(vendor=new_vendor, job=job, applicant=profile,status="Sourced")
            applicant.save()
            return Response({"Message": "Successfully Applied"})
        

class SingleVendorApplicantView(ListAPIView):
    serializer_class = ListVendorApplicantSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
            queryset = self.model.objects.filter(job__user=user)
            return queryset
        elif Organization.objects.filter(user=self.request.user).exists():
            # sadmin = Organization.objects.filter(user=self.request.user).values()
            # for i in sadmin:
            #     sadmin_key = i['created_by_id']
            
            # user = SuperAdmin.objects.get(pk=sadmin_key)
            # erefid = self.kwargs['erefid']
            # refid = self.kwargs['refid']
            # user = Candidate.objects.get(erefid=erefid)
            # job = Job.objects.get(refid=refid)
            user = self.request.user
            queryset = self.model.objects.filter(job__team=user)
            print(queryset)
            return queryset
        
        
class NewVendorUpdateView(GenericAPIView):
    
    permission_classes = [
        IsAuthenticated,
    ]

    def put(self, request, vrefid):
        new_vendor = NewVendor.objects.filter(vrefid=vrefid)
        vendor = VendorRegistration.objects.get(vendor=new_vendor)
        serializer = VendorCandidateSocialLinkSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#list Vendor Applicant

class ListVendorApplicantView(ListAPIView):
    serializer_class = ListVendorApplicantSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        refid = self.kwargs['refid']
        vrefid = self.kwargs['vrefid']

        queryset = self.model.objects.filter(vendor = NewVendor.objects.get(vrefid=vrefid),job = Job.objects.get(refid=refid))
        return queryset


from rest_framework.views import APIView

class ListVendorCanView(APIView):
    def get(self, request,refid,vcrefid, format=None):

        user = VendorCandidateProfile.objects.get(vcrefid = vcrefid)
        job = Job.objects.get(refid = refid)

        queryset1 = VendorCandidateSocialLink.objects.filter(user=user,job=job)
        queryset2 = VendorCandidateEducation.objects.filter(user=user,job=job)
        queryset3 = VendorCandidateExperience.objects.filter(user=user,job=job)
        queryset4 = VendorCandidateCertificate.objects.filter(user=user,job=job)
        queryset5 = VendorCandidateProfile.objects.filter(vcrefid = vcrefid)
        
        data = {
            'vprofiledata': queryset5,
            'linkdata': queryset1,
            'vexpdata': queryset3,
            'vedudata': queryset2,
            'cerdata': queryset4,
        }
        serializer = VendorUserProfileSerializer(data)
        return Response(serializer.data)