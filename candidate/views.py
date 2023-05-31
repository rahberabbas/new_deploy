from django.shortcuts import render
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
from rest_framework.views import APIView
import random
import string
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.conf import settings
import threading
from accounts.utils import *
from django.core.mail import send_mail
from django.utils import timezone

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.template.loader import render_to_string, get_template
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import pandas as pd

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
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

class CandidateRegistrationEmailView(generics.GenericAPIView):

    serializer_class = CandidateRegestrationSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request, *args, **kwargs):
        unique_id = self.kwargs['unique_id']
        print(unique_id)
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        updated_organization = OrganizationProfile.objects.filter(unique_id=unique_id).values()
        for i in updated_organization:
            org_id = (i['id'])
        user_data = serializer.data
        user = Candidate.objects.get(email=user_data['email'])
        c1 = Candidate.objects.get(email=user_data['email'])
        c1.organizations.add(org_id)
        token = RefreshToken.for_user(user).access_token
        tokens = get_tokens_for_user(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        #print(token)
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        # email_body = 'Hi '+user.name + \
        #     ' Use the link below to verify your email \n' + absurl
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Verify your email'}

        email_body = render_to_string('verify-email.html',{
            'user': user.email,
            'absurl': absurl,
        })
        # #print(absurl)
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Activate your account'}

        email = EmailMessage(subject='Activate your account', body=email_body, from_email="somahkopvt@gmail.com", to=[user.email])
        email.content_subtype = 'html'
        EmailThread(email).start()
        
        return Response({"user_data": user_data, "tokens": tokens }, status=status.HTTP_201_CREATED)

class CandidateRegistrationIDView(generics.GenericAPIView):


    def post(self, request, *args, **kwargs):

        candidate_id = request.POST.get('candidate_id')
        unique_id = self.kwargs['unique_id']
        print(candidate_id)
        user = Candidate.objects.get(erefid=candidate_id)
        user2 = Candidate.objects.filter(erefid=candidate_id).values()
        for i in user2:
            user_email = i['email']
        print(user_email)
        updated_organization = OrganizationProfile.objects.filter(unique_id=unique_id).values()
        for i in updated_organization:
            org_id = (i['id'])
        if user_email:
            otp = generate_otp()
            print(otp)
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(email=user_email, otp=otp, expires_at=expires_at)

            subject = 'Your OTP for authentication'
            message = f'Your OTP is {otp}. It will expire in 5 minutes.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user_email]
            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'OTP sent successfully.'})
        else:
            return Response({'error': 'OTP not sended'})

class VerifyOTPView(APIView):
    def post(self, request,  *args, **kwargs):
        unique_id = self.kwargs['unique_id']
        email = request.data.get('email')
        otp = request.data.get('otp')
        if email and otp:
            try:
                otp_obj = OTP.objects.get(email=email, otp=otp, expires_at__gte=timezone.now())
                otp_obj.delete()  # Delete the OTP object once it has been used
                user = Candidate.objects.get(email=email)
                updated_organization = OrganizationProfile.objects.filter(unique_id=unique_id).values()
                for i in updated_organization:
                    org_id = (i['id'])
                user.organizations.add(org_id)
                return Response({'message': 'OTP verified successfully.'})
            except OTP.DoesNotExist:
                return Response({'error': 'Invalid OTP or OTP has expired.'})
        else:
            return Response({'error': 'Please provide an email address and OTP.'})

class CLoginAPIViewCheck1(APIView):
    def post(self, request, erefid,oid,  *args, **kwargs):
        if User.objects.filter(email=erefid).exists() and Candidate.objects.filter(user=User.objects.get(email=erefid)).exists():
            user = Candidate.objects.get(user=User.objects.get(email=erefid))
            oprofile = OrganizationProfile.objects.get(unique_id=oid)
            organization= user.organizations.all()
            if oprofile in organization:
                return Response({'success': 'Email Verified With This Org'})
            else: 
                user.organizations.add(oprofile)
                return Response({'success': 'Email Verified With This Org'})
                # return Response({'error': 'Email Exist But You not Register With This Org'})

        else:
            return Response({'error': 'Email Not Exist'})

class CLoginAPIView(generics.GenericAPIView):
    serializer_class = CLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validate(request.data)
        dict=serializer.data
        # print(dict)
        email = dict['email']
        print(email)
        try:
            user = Candidate.objects.filter(email=email).values()
            users = Candidate.objects.get(email=email)
            for i in user:
                verified = i['verified']
            if verified != "True":
                token = RefreshToken.for_user(users).access_token
                tokens = get_tokens_for_user(users)
            
            print(verified)
        except:
            pass
        dict.update({'type': data["type"],'role': data["role"],'userObj':data["userObj"]})
        return Response(dict,status=status.HTTP_200_OK)


from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework import generics, status
from django.http import JsonResponse
from django.db.models import Q


class CandidateProfileView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CandidateProfileSerializer

    def get(self, request,erefid, refid, format=None):
        cand = Candidate.objects.get(erefid=erefid)
        profile = CandidateProfile.objects.get(user=cand)
        job = Job.objects.get(refid=refid)
        serializer = CandidateProfileSerializer(profile,job)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BioView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BioSerializer

    def get(self, request,erefid,refid, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        profile = CandidateProfile.objects.get(user = cand)
        job = Job.objects.get(refid=refid)
        serializer = BioSerializer(profile,job)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request,erefid,refid, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        profile = CandidateProfile.objects.get(user = cand)
        job = Job.objects.get(refid=refid)
        serializer = BioSerializer(profile, job,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Candidate Profile

class FinalCandidateProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FinalCandidateProfileSerializer

    def post(self, request, refid, format=None):
        cand = Candidate.objects.get(user=self.request.user)
        print(cand)
        print("--------")
        job = Job.objects.get(refid = refid)
        if CandidateProfile.objects.filter(user=cand,job=job).exists():
            return Response({'msg': 'Entry Already Exist'},status=204)
        else:
            candidateProfile = CandidateProfile.objects.create(user=cand,job=job)
            serializer = FinalCandidateProfileSerializer(candidateProfile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid, refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        candidateProfile = CandidateProfile.objects.get(user=cand, pk=pk,job=job)
        serializer = FinalCandidateProfileSerializer(candidateProfile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid, refid, pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        candidateProfile = CandidateProfile.objects.get(user=cand, pk=pk,job=job)
        candidateProfile.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListCandidateProfileView(generics.ListAPIView):
    serializer_class = ListCandidateProfileSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset

class ListUserView(APIView):
    def get(self, request,erefid, refid, format=None):

        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset1 = Skill.objects.filter(user=user,job=job)
        queryset2 = CandidateExperience.objects.filter(user=user,job=job)
        queryset3 = CandidateEducation.objects.filter(user=user,job=job)
        queryset4 = Certificate.objects.filter(user=user,job=job)
        queryset5 = Resume.objects.filter(user=user,job=job)
        queryset6 = Link.objects.filter(user=user,job=job)
        queryset7 = CandidateProfile.objects.filter(user=user,job=job)
        
        data = {
            'cprofiledata': queryset7,
            'skilldata': queryset1,
            'linkdata': queryset6,
            'cexpdata': queryset2,
            'cedudata': queryset3,
            'cerdata': queryset4,
            'resumedata': queryset5,
        }
        serializer = UserProfileSerializer(data)
        return Response(serializer.data)

import json 
import csv   

class ListUserView1(APIView):
    def get(self, request, format=None):
        arr = []
        dic = {}
        dic2 = {}
        final_arr = []
        for i in Candidate.objects.filter().values():
            # print(i)
            user = Candidate.objects.get(pk=i['id'])
            queryset0 = Candidate.objects.filter(pk=i['id'])
            arr.append(i['erefid'])
            queryset1 = Skill.objects.filter(user=user)
            queryset2 = CandidateExperience.objects.filter(user=user)
            queryset3 = CandidateEducation.objects.filter(user=user)
            queryset4 = Certificate.objects.filter(user=user)
            queryset5 = Resume.objects.filter(user=user)
            queryset6 = Link.objects.filter(user=user)
            queryset7 = CandidateProfile.objects.filter(user=user)
        
            data = {
                # 'Candidatedata': queryset0,
                'cprofiledata': queryset7,
                'skilldata': queryset1,
                'linkdata': queryset6,
                'cexpdata': queryset2,
                'cedudata': queryset3,
                'cerdata': queryset4,
                'resumedata': queryset5,
            }
            serializer = UserProfileSerializer1(data)
            dic[i['erefid']] = serializer.data
        count = 1
        for i in arr:
            
            final_dic = {}
            final_dic['No'] = count
            count = count + 1
            final_dic['refid'] = i
            
            final_skill = []
            final_summary = []
            curr_sal = []
            exp_sal = []
            
            for j in dic[i]['Skill']:
                # print(j['title'])
                final_skill.append(j['title'])
            final_dic['skill_title'] = ', '.join(final_skill)
            for j in dic[i]['CandidateProfile']:
                final_summary.append(j['summary'])
                curr_sal.append(j['current_salary'])
                exp_sal.append(j['expected_salary'])
            final_dic['cprofile_summary'] = ', '.join(final_summary)
            final_dic['curr_sal'] = ', '.join(curr_sal)
            final_dic['exp_sal'] = ', '.join(exp_sal)
            
            final_arr.append(final_dic)
        print(final_dic)
            
        field_names = ['No', 'refid', 'curr_sal', 'summary', 'skill_title', 'exp_sal', 'cprofile_summary']
        
        with open('Names.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = field_names)
            writer.writeheader()
            writer.writerows(final_arr)
                
        return Response(dic)

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAIChat
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

class ChatUserJobWiseView(APIView):
    def post(self, request, refid, format=None):
        prompt = request.POST.get('prompt')
        print(prompt)
        print("-------")
        arr = []
        dic = {}
        dic2 = {}
        final_arr = []
        job = Job.objects.get(refid=refid)
        # if SuperAdmin.objects.filter(user=self.request.user).exists():
        #     user = self.request.user
        # elif Organization.objects.filter(user=self.request.user).exists():
        #     sadmin = Organization.objects.filter(user=self.request.user).values()
        #     for i in sadmin:
        #         sadmin_key = i['created_by_id']
            
        #     user = SuperAdmin.objects.get(pk=sadmin_key)
        # job = Job.objects.filter(refid=refid)
        print(job)
        for i in Candidate.objects.filter().values():
            # print(i)
            user = Candidate.objects.get(pk=i['id'])
            queryset0 = Candidate.objects.filter(pk=i['id'])
            # arr.append(i['erefid'])
            queryset1 = Skill.objects.filter(user=user, job=job)
            queryset2 = CandidateExperience.objects.filter(user=user, job=job)
            queryset3 = CandidateEducation.objects.filter(user=user, job=job)
            queryset4 = Certificate.objects.filter(user=user, job=job)
            queryset5 = Resume.objects.filter(user=user, job=job)
            queryset6 = Link.objects.filter(user=user, job=job)
            queryset7 = CandidateProfile.objects.filter(user=user, job=job)
            if queryset7.count() != 0:
                print(queryset7)
                arr.append(i['erefid'])
            # print(queryset1)
            data = {
                # 'Candidatedata': queryset0,
                'cprofiledata': queryset7,
                'skilldata': queryset1,
                'linkdata': queryset6,
                'cexpdata': queryset2,
                'cedudata': queryset3,
                'cerdata': queryset4,
                'resumedata': queryset5,
            }
            serializer = UserProfileSerializer1(data)
            dic[i['erefid']] = serializer.data
        count = 1
        for i in arr:
            
            final_dic = {}
            final_dic['No'] = count
            count = count + 1
            final_dic['refid'] = i
            
            final_skill = []
            final_summary = []
            curr_sal = []
            exp_sal = []
            
            for j in dic[i]['Skill']:
                # print(j['title'])
                final_skill.append(j['title'])
            final_dic['skill_title'] = ', '.join(final_skill)
            for j in dic[i]['CandidateProfile']:
                final_summary.append(j['summary'])
                curr_sal.append(j['current_salary'])
                exp_sal.append(j['expected_salary'])
            final_dic['cprofile_summary'] = ', '.join(final_summary)
            final_dic['curr_sal'] = ', '.join(curr_sal)
            final_dic['exp_sal'] = ', '.join(exp_sal)
            final_dic['Combined'] = "Summary: " + final_dic['cprofile_summary'] + " ;Skills: " + final_dic['skill_title'] + " ;Current Salary: " + final_dic['curr_sal'] + " ;Expected Salary: " + final_dic['exp_sal']
            final_arr.append(final_dic)
            
        sources = []
        for i in final_arr:
            doc = Document(
                page_content=i['Combined'],
                metadata={"source": i['refid']},
            )
            # append the Document object to the list
            sources.append(doc)
        chunks = []
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n", ".", "!", "?", ",", " ", "<br>"],
            chunk_size=1024,
            chunk_overlap=0
        )
        for source in sources:
            for chunk in splitter.split_text(source.page_content):
                chunks.append(Document(page_content=chunk, metadata=source.metadata)) 
        index = FAISS.from_documents(chunks, OpenAIEmbeddings(openai_api_key='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'))
        template = """You are a chatbot who have candidates data of summary , skills, current salary, expected salary.

        QUESTION: {question}
        =========
        {summaries}
        =========
        FINAL ANSWER:"""
        PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
        chain = load_qa_with_sources_chain(OpenAIChat(openai_api_key='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', temperature=0, model_name="gpt-3.5-turbo"), prompt=PROMPT)
        def answer(question):
            mainans = (
                chain(
                    {
                        "input_documents": index.similarity_search(question, k=4),
                        "question": question,
                    },
                    return_only_outputs=True,
                )["output_text"]
            )
            print(mainans)
            return mainans
        
        mainans = answer(prompt)
        return Response({"res":mainans})

# Skills

class SkillView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SkillSerializer

    def post(self, request,erefid, refid, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        skill = Skill.objects.create(user=cand,job=job)
        serializer = SkillSerializer(skill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid, refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        skill = Skill.objects.get(user=cand, pk=pk,job=job)
        serializer = SkillSerializer(skill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid, refid, pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        skill = Skill.objects.get(user=cand, pk=pk,job=job)
        skill.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListSkillView(generics.ListAPIView):
    serializer_class = ListSkillSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset

# Links

class LinkView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LinkSerializer

    def post(self, request,erefid, refid, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        link = Link.objects.create(user=cand,job=job)
        serializer = LinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid,refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        link = Link.objects.get(user=cand, pk=pk,job=job)
        serializer = LinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid, refid, pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        link = Link.objects.get(user=cand, pk=pk,job=job)
        link.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListLinkView(generics.ListAPIView):
    serializer_class = ListLinkSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset

# Resume

import fitz
import requests
import uuid

class ResumeView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResumeSerializer

    def post(self, request,refid,  format=None):
        cand = Candidate.objects.get(user=self.request.user)
        job = Job.objects.get(refid = refid)
        if Resume.objects.filter(user=cand,job=job).exists():
            return Response({'msg': 'Entry Already Exist'},status=204)
        else:
            resume = Resume.objects.create(user=cand,job=job)
            serializer = ResumeSerializer(resume, data=request.data)
            if serializer.is_valid():
                serializer.save()
                res = Resume.objects.filter(user=cand)[0]
                url = res.file.path
                # url = "/media/"+url
                print(url)
                with fitz.open(url) as doc:
                    pymupdf_text = ""
                    for page in doc:
                        pymupdf_text += page.get_text()
                print(pymupdf_text)
                res.full_text = pymupdf_text
                res.save()
                return Response({"Pdf Data": pymupdf_text}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid,refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        resume = Resume.objects.get(user=cand, pk=pk,job=job)
        serializer = ResumeSerializer(resume, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid, refid, pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        resume = Resume.objects.get(user=cand, pk=pk,job=job)
        resume.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListResumeView(generics.ListAPIView):
    serializer_class = ListResumeSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset

# Certificate

class CertificateView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CertificateSerializer

    def post(self, request,erefid,refid,  format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        cert = Certificate.objects.create(user=cand,job=job)
        serializer = CertificateSerializer(cert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid,refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        cert = Certificate.objects.get(user=cand, pk=pk,job=job)
        serializer = CertificateSerializer(cert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid,refid,  pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        cert = Certificate.objects.get(user=cand, pk=pk,job=job)
        cert.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListCertificateView(generics.ListAPIView):
    serializer_class = ListCertificateSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset

# Education

class EducationView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EducationSerializer

    def post(self, request,erefid,refid,  format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        edu = CandidateEducation.objects.create(user=cand,job=job)
        serializer = EducationSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid,refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        edu = CandidateEducation.objects.get(user=cand, pk=pk,job = job)
        serializer = EducationSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid,refid,  pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        edu = CandidateEducation.objects.get(user=cand, pk=pk, job=job)
        edu.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListEducationView(generics.ListAPIView):
    serializer_class = ListEducationSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset

# Experience

class ExperienceView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExperienceSerializer

    def post(self, request,erefid,refid,  format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        exp = CandidateExperience.objects.create(user=cand, job=job)
        serializer = ExperienceSerializer(exp, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,erefid,refid, pk, format=None):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        exp = CandidateExperience.objects.get(user=cand, pk=pk, job=job)
        serializer = ExperienceSerializer(exp, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, erefid, refid, pk ,*args, **kwargs):
        cand = Candidate.objects.get(erefid = erefid)
        job = Job.objects.get(refid = refid)
        exp = CandidateExperience.objects.get(user=cand, pk=pk, job=job)
        exp.delete()
        return Response({'msg': 'Deleted'},status=204)

class ListExperienceView(generics.ListAPIView):
    serializer_class = ListExperienceSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        erefid = self.kwargs['erefid']
        refid = self.kwargs['refid']
        user = Candidate.objects.get(erefid=erefid)
        job = Job.objects.get(refid=refid)
        queryset = self.model.objects.filter(user=user,job=job)
        return queryset


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        #print(token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        #print('payload ', payload)
        try:
            #print("hello")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            #print("Paylod:", payload)
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

            #         email = EmailMessage(subject='Welcome to Somhako', body=email_body, from_email=settings.DEFAULT_NO_REPLY_EMAIL, to=[user.email])
            #         email.content_subtype = 'html'
            #         EmailThread(email).start()

            #     return HttpResponseRedirect(redirect_to='https://somhako.com/marketplace/auth/signin/')
            if Candidate.objects.filter(id=payload['user_id']).exists():
                user = Candidate.objects.get(id=payload['user_id'])
                #print(user)
                if not user.verified:
                    user.verified = True
                    user.save()
                    #print(user)
                    email_body = render_to_string('recruiter-login.html',{
                        'cname': user.company_name,
                        'email': user.email,
                    })
                    # #print(absurl)
                    # data = {'email_body': email_body, 'to_email': user.email,
                    #         'email_subject': 'Activate your account'}

                    email = EmailMessage(subject='Welcome to Somhako', body=email_body, from_email="somahkopvt@gmail.com", to=[user.email])
                    email.content_subtype = 'html'
                    EmailThread(email).start()

                    
                return HttpResponseRedirect(redirect_to='https://somhako.com/marketplace/auth/signin/')
            else:
                return Response({'email': 'Not Activated'}, status=status.HTTP_200_OK)
            
            
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)