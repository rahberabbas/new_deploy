from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import pytz
from .models import *
from .serializers import *
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework import generics, status
import threading
from notifications.signals import notify
from notifications.models import Notification

# Create your views here.


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class CreateJobAPIView(generics.GenericAPIView):
    queryset = Job.objects.all()
    serializer_class = JobCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        idss = request.POST.get("teamID")
        jobObj = Job.objects.create()
        if idss is not None and len(idss) > 0:
            arrlist = idss.split("|")
            farrlist = [eval(i) for i in arrlist]
            print(arrlist)
            for i in farrlist:
                jobObj.team.add(int(i))
        serializer = JobCreateUpdateSerializer(jobObj, data=request.data)
        if serializer.is_valid(raise_exception=True):
            if SuperAdmin.objects.filter(user=request.user).exists():
                serializer.save(
                    user=request.user,
                )
            elif Organization.objects.filter(user=request.user).exists():
                sadmin = Organization.objects.filter(user=request.user).values()
                for i in sadmin:
                    sadmin_key = i["created_by_id"]

                print(sadmin)
                serializer.save(
                    user=SuperAdmin.objects.get(pk=sadmin_key),
                )
            # notify.send(sadmin, recipient=sadmin, verb=f"{sadmin} has create the Job")
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def put(self, request, refid, *args, **kwargs):
        idss = request.POST.get("teamID")
        job = Job.objects.get(refid=refid)
        if idss is not None and len(idss) > 0:
            arrlist = idss.split("|")
            farrlist = [eval(i) for i in arrlist]
            print(arrlist)
            for i in farrlist:
                job.team.add(int(i))
        serializer = JobCreateUpdateSerializer(job, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, refid, *args, **kwargs):
        job = Job.objects.filter(refid=refid)
        job.delete()
        return Response({"msg": "Deleted"}, status=204)


class JobListingApiView(generics.ListAPIView):
    serializer_class = ListJobSerializer
    model = serializer_class.Meta.model

    # paginate_by = 100
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

    # queryset = Job.objects.all()
    # serializer_class = ListJobSerializer
    # model = serializer_class.Meta.model
    # permission_classes = [
    #     IsAuthenticated,
    # ]

    # def get_queryset(self):
    #     queryset = self.model.objects.filter()
    #     return queryset


class JobDetailingApiView(ListAPIView):
    serializer_class = ListJobSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        refid = self.kwargs["refid"]
        queryset = self.model.objects.filter(refid=refid)
        return queryset


import pinecone
import openai

# class ApplicantApplyView(APIView):
#     permission_classes = [
#         IsAuthenticated,
#     ]

#     def post(self, request, refid):
#         user = Candidate.objects.get(user=self.request.user)
#         job = Job.objects.get(refid = refid)
#         if Applicant.objects.filter(user=user, job=job).exists():
#             return Response({"Message": "Already Applied"})
#         else:
#             applicant = Applicant.objects.create(user=user, job=job, status="Sourced")
#             applicant.save()
#             return Response({"Message": "Successfully Applied"})

# class ApplicantApplyView(APIView):

#     def post(self, request):
#         pinecone.init(api_key='7f1409cf-e246-4b48-810c-e8b6f9a6ef3b', environment='us-east1-gcp')
#         active_indexes = pinecone.list_indexes()
#         print(active_indexes)
#         return Response({"Message": "Successfully Applied"})
#         user = Candidate.objects.get(user=self.request.user)
#         job = Job.objects.get(refid = refid)
#         if Applicant.objects.filter(user=user, job=job).exists():
#             return Response({"Message": "Already Applied"})
#         else:
#             applicant = Applicant.objects.create(user=user, job=job, status="Sourced")
#             applicant.save()
#             return Response({"Message": "Successfully Applied"})

from uuid import uuid4

# class ApplicantApplyView(APIView):
#     permission_classes = [
#         IsAuthenticated,
#     ]

#     def post(self, request, refid):
#         user = Candidate.objects.get(user=self.request.user)
#         job = Job.objects.get(refid = refid)
#         job2 = Job.objects.filter(refid = refid).values()
#         pinecone.init(api_key='7f1409cf-e246-4b48-810c-e8b6f9a6ef3b', environment='us-east1-gcp')
#         active_indexes = pinecone.list_indexes()
#         index = pinecone.Index('somhako')
#         print(index.describe_index_stats())
#         if Applicant.objects.filter(user=user, job=job).exists():
#             return Response({"Message": "Already Applied"})
#         else:
#             applicant = Applicant.objects.create(user=user, job=job, status="Sourced")
#             applicant.save()
#             for i in job2:
#                 user_id = i['user_id']
#             org_id = OrganizationProfile.objects.filter(user=SuperAdmin.objects.get(pk=user_id)).values()
#             for i in org_id:
#                 org_unique_id = i['unique_id']
#             arr = []
#             dic = {}
#             final_arr = []
#             for i in Candidate.objects.filter(user=self.request.user).values():
#                 email = i['email']
#                 user = Candidate.objects.get(pk=i['id'])
#                 queryset0 = Candidate.objects.filter(pk=i['id'])
#                 queryset1 = Skill.objects.filter(user=user, job=job)
#                 queryset2 = CandidateExperience.objects.filter(user=user, job=job)
#                 queryset3 = CandidateEducation.objects.filter(user=user, job=job)
#                 queryset4 = Certificate.objects.filter(user=user, job=job)
#                 queryset5 = Resume.objects.filter(user=user, job=job)
#                 queryset6 = Link.objects.filter(user=user, job=job)
#                 queryset7 = CandidateProfile.objects.filter(user=user, job=job)
#                 if queryset7.count() != 0:
#                     arr.append(i['erefid'])
#                 data = {
#                     'cprofiledata': queryset7,
#                     'skilldata': queryset1,
#                     'linkdata': queryset6,
#                     'cexpdata': queryset2,
#                     'cedudata': queryset3,
#                     'cerdata': queryset4,
#                     'resumedata': queryset5,
#                 }
#                 serializer = UserProfileSerializer1(data)
#                 dic[i['erefid']] = serializer.data
#             count = 1
#             for i in arr:

#                 final_dic = {}
#                 final_dic['erefid'] = i
#                 final_dic['Organization id'] = org_unique_id
#                 final_dic['Job refid'] = refid

#                 final_skill = []
#                 final_summary = []
#                 curr_sal = []
#                 exp_sal = []

#                 for j in dic[i]['Skill']:
#                     final_skill.append(j['title'])
#                 final_dic['skill_title'] = ', '.join(final_skill)
#                 for j in dic[i]['CandidateProfile']:
#                     final_summary.append(j['summary'])
#                     curr_sal.append(j['current_salary'])
#                     exp_sal.append(j['expected_salary'])
#                     final_dic['Candidate Name'] = j['first_name'] + " " + j['last_name']
#                     final_dic['Candidate Mobile'] = j['mobile']
#                     final_dic['Candidate Email'] = email
#                 final_dic['cprofile_summary'] = ', '.join(final_summary)
#                 final_dic['curr_sal'] = ', '.join(curr_sal)
#                 final_dic['exp_sal'] = ', '.join(exp_sal)
#                 final_dic['Combined'] = "Summary: " + final_dic['cprofile_summary'] + " ;Skills: " + final_dic['skill_title'] + " ;Current Salary: " + final_dic['curr_sal'] + " ;Expected Salary: " + final_dic['exp_sal'] + " ;Candidate Name: " + final_dic['Candidate Name'] + " ;Candidate Mobile: " + final_dic['Candidate Mobile'] + " ;Candidate Email: " + final_dic['Candidate Email'] + " ;Candidate Refid: " + final_dic['erefid']
#                 final_arr.append(final_dic)
#             # print(final_arr)
#             openai.api_key = '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'
#             pinecone_vectors = []
#             for i in final_arr:
#                 embedding = openai.Embedding.create(
#                     input=i['Combined'],
#                     model="text-embedding-ada-002"
#                 )
#                 vector = embedding["data"][0]["embedding"]
#                 pinecone_vectors.append((str(uuid4()), vector, {"Job ID": i['Job refid'], "Organization ID": i['Organization id'], "Candidate ID": i['erefid']}))
#             # print(pinecone_vectors)
#             upsert_response = index.upsert(vectors=pinecone_vectors, namespace="Candidates")
#             # metadatas = {'Organization ID': 'clf0u40lt0009dcu0wqwram4u'}
#             # query = pinecone.query.Filter(query={"metadata.Organization ID": 'clf0u40lt0009dcu0wqwram4u'})
#             # result = index.query(
#             #     vector=vector,
#             #     filter={
#             #         'Organization ID': 'clf0u40lt0009dcu0wqwram4u'
#             #     },
#             #     top_k=10,
#             #     include_metadata=True
#             # )
#             # results = index.fetch(ids=index.list())
#             # results = index.query(
#             #     top_k=1536,
#             #     namespace='',
#             #     include_values=True
#             # )
#             # results = index.query(query={}, top_k=1)
#             # print(results)
#             # result = index.query(queries="Show all", metadata=metadatas, top_k=5)
#             # print(results)
#             # query = "Show all the Candidate Whose skills is Django and experience is 4 years"
#             # vectors = openai.Embedding.create(input=[query], model="text-embedding-ada-002")['data'][0]['embedding']

#             # result = index.query(namespace='Candidates', top_k=1536, vector=vectors, include_values=False, include_metadata=True)
#             # print(result)
#             print("Uploaded")
#             return Response({"Message": "Successfully Applied"})

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class ApplicantApplyView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, refid):
        user = Candidate.objects.get(user=self.request.user)
        job = Job.objects.get(refid=refid)
        job2 = Job.objects.filter(refid=refid).values()
        pinecone.init(
            api_key="7f1409cf-e246-4b48-810c-e8b6f9a6ef3b", environment="us-east1-gcp"
        )
        active_indexes = pinecone.list_indexes()
        index = pinecone.Index("somhako")
        # print(index.describe_index_stats())
        if Applicant.objects.filter(user=user, job=job).exists():
            return Response({"Message": "Already Applied"})
        else:
            applicant = Applicant.objects.create(user=user, job=job, status="Sourced")
            applicant.save()
            for i in job2:
                user_id = i["user_id"]
            org_id = OrganizationProfile.objects.filter(
                user=SuperAdmin.objects.get(pk=user_id)
            ).values()
            for i in org_id:
                org_unique_id = i["unique_id"]
            arr = []
            dic = {}
            final_arr = []
            for i in Candidate.objects.filter(user=self.request.user).values():
                email = i["email"]
                user = Candidate.objects.get(pk=i["id"])
                queryset0 = Candidate.objects.filter(pk=i["id"])
                queryset1 = Skill.objects.filter(user=user, job=job)
                queryset2 = CandidateExperience.objects.filter(user=user, job=job)
                queryset3 = CandidateEducation.objects.filter(user=user, job=job)
                queryset4 = Certificate.objects.filter(user=user, job=job)
                queryset5 = Resume.objects.filter(user=user, job=job)
                queryset6 = Link.objects.filter(user=user, job=job)
                queryset7 = CandidateProfile.objects.filter(user=user, job=job)
                if queryset7.count() != 0:
                    arr.append(i["erefid"])
                data = {
                    "cprofiledata": queryset7,
                    "skilldata": queryset1,
                    "linkdata": queryset6,
                    "cexpdata": queryset2,
                    "cedudata": queryset3,
                    "cerdata": queryset4,
                    "resumedata": queryset5,
                }
                serializer = UserProfileSerializer1(data)
                dic[i["erefid"]] = serializer.data
            count = 1
            for i in arr:
                final_dic = {}
                final_dic["erefid"] = i
                final_dic["Organization id"] = org_unique_id
                final_dic["Job refid"] = refid

                final_skill = []
                final_summary = []
                curr_sal = []
                exp_sal = []

                for j in dic[i]["Skill"]:
                    final_skill.append(j["title"])
                final_dic["skill_title"] = ", ".join(final_skill)
                for j in dic[i]["CandidateProfile"]:
                    final_summary.append(j["summary"])
                    curr_sal.append(j["current_salary"])
                    exp_sal.append(j["expected_salary"])
                    final_dic["Candidate Name"] = j["first_name"] + " " + j["last_name"]
                    final_dic["Candidate Mobile"] = j["mobile"]
                    final_dic["Candidate Email"] = email
                final_dic["cprofile_summary"] = ", ".join(final_summary)
                final_dic["curr_sal"] = ", ".join(curr_sal)
                final_dic["exp_sal"] = ", ".join(exp_sal)
                final_dic["Combined"] = (
                    "Summary: "
                    + final_dic["cprofile_summary"]
                    + " ;Skills: "
                    + final_dic["skill_title"]
                    + " ;Current Salary: "
                    + final_dic["curr_sal"]
                    + " ;Expected Salary: "
                    + final_dic["exp_sal"]
                    + " ;Candidate Name: "
                    + final_dic["Candidate Name"]
                    + " ;Candidate Mobile: "
                    + final_dic["Candidate Mobile"]
                    + " ;Candidate Email: "
                    + final_dic["Candidate Email"]
                    + " ;Candidate Refid: "
                    + final_dic["erefid"]
                )
                final_arr.append(final_dic)
            # print(final_arr)
            openai.api_key = "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"
            pinecone_vectors = []
            sources = []
            for i in final_arr:
                doc = Document(
                    page_content=i["Combined"],
                    metadata={
                        "Job ID": i["Job refid"],
                        "Organization ID": i["Organization id"],
                        "Candidate ID": i["erefid"],
                    },
                )
                # append the Document object to the list
                sources.append(doc)
            chunks = []
            splitter = RecursiveCharacterTextSplitter(
                separators=["\n", ".", "!", "?", ",", " ", "<br>"],
                chunk_size=1024,
                chunk_overlap=0,
            )
            for source in sources:
                for chunk in splitter.split_text(source.page_content):
                    chunks.append(
                        Document(page_content=chunk, metadata=source.metadata)
                    )
            embeddings = OpenAIEmbeddings(
                openai_api_key="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"
            )
            docsearch = Pinecone.from_documents(
                chunks, embeddings, index_name="somhako"
            )

            print("Uploaded")

            return Response({"Message": "Successfully Applied"})


class ApplicantApplyView1(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, refid):
        user = Candidate.objects.get(user=self.request.user)
        job = Job.objects.get(refid=refid)
        if Applicant.objects.filter(user=user, job=job).exists():
            return Response({"Message": 1})
        else:
            return Response({"Message": 0})


class CandidateApplicantDashboardView(ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = DashboardAllApplicantSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        arr = []
        unique_id = self.kwargs["unique_id"]
        # user = OrganizationProfile.objects.get(unique_id = unique_id)
        user = OrganizationProfile.objects.filter(unique_id=unique_id).values()
        print(user)
        for i in user:
            user_id = i["user_id"]
        user2 = SuperAdmin.objects.get(pk=user_id)
        for job in Job.objects.filter(user=user2):
            arr.append(job.id)
        queryset = self.model.objects.filter(user=self.request.user, job__in=arr)

        return queryset


# Applicants


class ApplicantView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicantSerializer

    def put(self, request, arefid, *args, **kwargs):
        applicant = Applicant.objects.get(arefid=arefid)
        serializer = ApplicantSerializer(applicant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, arefid, *args, **kwargs):
        applicant = Applicant.objects.get(arefid=arefid)
        applicant.delete()
        return Response({"msg": "Deleted"}, status=204)


class ListApplicantView1(generics.ListAPIView):
    serializer_class = ListApplicantSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        refid = self.kwargs["refid"]

        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        queryset = self.model.objects.filter(job__user=user, job__refid=refid)
        return queryset


class ListApplicantView(generics.ListAPIView):
    serializer_class = ListApplicantSerializer
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


class ListFeedbackView(generics.ListAPIView):
    serializer_class = ListFeedbackSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        arefid = self.kwargs["arefid"]
        queryset = self.model.objects.filter(
            applicant=Applicant.objects.get(arefid=arefid)
        )
        return queryset


class FeedbackView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeedbackSerializer

    def post(self, request, arefid, format=None):
        applicant = Applicant.objects.get(arefid=arefid)
        feedback = Feedback.objects.create(user=self.request.user, applicant=applicant)
        serializer = FeedbackSerializer(feedback, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        feedback = Feedback.objects.get(pk=pk)
        serializer = FeedbackSerializer(feedback, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.ListAPIView):
    serializer_class = CurrentUserSerializer
    model = serializer_class.Meta.model
    paginate_by = 100

    def get_queryset(self):
        # queryset = self.request.user
        # print(queryset)
        # print(self.request.user)
        queryset = self.model.objects.filter(email=self.request.user)
        return queryset


class CreateOfferManagementAPIView(generics.GenericAPIView):
    serializer_class = OfferManagementCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, arefid, *args, **kwargs):
        authority = request.POST.get("authority")
        offermanagement = OfferManagement.objects.create()
        if authority is not None and len(authority) > 0:
            arrlist = authority.split("|")
            farrlist = [eval(i) for i in arrlist]
            print(arrlist)
            for i in farrlist:
                offermanagement.approval_authorities.add(int(i))
        serializer = OfferManagementCreateUpdateSerializer(
            offermanagement, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            if SuperAdmin.objects.filter(user=request.user).exists():
                serializer.save(
                    user=request.user, applicant=Applicant.objects.get(arefid=arefid)
                )
            elif Organization.objects.filter(user=request.user).exists():
                sadmin = Organization.objects.filter(user=request.user).values()
                for i in sadmin:
                    sadmin_key = i["created_by_id"]

                print(sadmin)
                serializer.save(
                    user=SuperAdmin.objects.get(pk=sadmin_key),
                    applicant=Applicant.objects.get(arefid=arefid),
                )
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def put(self, request, omrefid, *args, **kwargs):
        authority = request.POST.get("authority")
        offermanagement = OfferManagement.objects.get(omrefid=omrefid)
        if authority is not None and len(authority) > 0:
            arrlist = authority.split("|")
            farrlist = [eval(i) for i in arrlist]
            print(arrlist)
            for i in farrlist:
                offermanagement.approval_authorities.add(int(i))
        serializer = OfferManagementCreateUpdateSerializer(
            offermanagement, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if OfferFeedback.objects.filter(
                offer=OfferManagement.objects.get(omrefid=omrefid)
            ).exists():
                OfferFeedback.objects.filter(
                    offer=OfferManagement.objects.get(omrefid=omrefid)
                ).delete()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, pk, *args, **kwargs):
        offermanagement = OfferManagement.objects.filter(id=pk)
        offermanagement.delete()
        return Response({"msg": "Deleted"}, status=204)


class OfferManagementListingApiView(generics.ListAPIView):
    serializer_class = OfferManagementSerializer
    model = serializer_class.Meta.model

    # paginate_by = 100
    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i["created_by_id"]

            user = SuperAdmin.objects.get(pk=sadmin_key)
        arr = []
        applicant = Applicant.objects.filter(status="Offer").values()
        for i in applicant:
            arr.append(i["id"])
        queryset = self.model.objects.filter(user=user, applicant__in=arr)
        return queryset


class CreateOfferFeedbackAPIView(generics.GenericAPIView):
    serializer_class = OfferFeedbackCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, omrefid, *args, **kwargs):
        if OfferFeedback.objects.filter(
            organization=request.user,
            offer=OfferManagement.objects.get(omrefid=omrefid),
        ).exists():
            OfferFeedback.objects.filter(
                organization=request.user,
                offer=OfferManagement.objects.get(omrefid=omrefid),
            ).delete()

        offerfeedback = OfferFeedback.objects.create()

        serializer = OfferFeedbackCreateUpdateSerializer(
            offerfeedback, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                organization=request.user,
                offer=OfferManagement.objects.get(omrefid=omrefid),
            )
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def put(self, request, ofrefid, *args, **kwargs):
        offerfeedback = OfferFeedback.objects.get(ofrefid=ofrefid)

        serializer = OfferFeedbackCreateUpdateSerializer(
            offerfeedback, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, ofrefid, *args, **kwargs):
        offerfeedback = OfferFeedback.objects.filter(ofrefid=ofrefid)
        offerfeedback.delete()
        return Response({"msg": "Deleted"}, status=204)


class OfferFeedbackListingApiView(generics.ListAPIView):
    serializer_class = OfferFeedbackSerializer
    model = serializer_class.Meta.model

    # paginate_by = 100
    def get_queryset(self):
        omrefid = self.kwargs["omrefid"]
        queryset = self.model.objects.filter(offer__omrefid=omrefid)
        return queryset


class CreateOfferManagementAPIViewStep2(generics.GenericAPIView):
    serializer_class = OfferManagementCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def put(self, request, omrefid, *args, **kwargs):
        offermanagement = OfferManagement.objects.get(omrefid=omrefid)
        serializer = OfferManagementCreateUpdateSerializer(
            offermanagement, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)


from django.core.mail import send_mail


class SendEmailOfferManagementAPIView(generics.GenericAPIView):
    serializer_class = OfferManagementCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, omrefid, *args, **kwargs):
        offermanagement = OfferManagement.objects.filter(omrefid=omrefid).values()
        for i in offermanagement:
            aid = i["applicant_id"]
        app = Applicant.objects.filter(id=aid).values()
        for i in app:
            uid = i["user_id"]
        user = Candidate.objects.filter(id=uid).values()
        for i in user:
            user_email = i["email"]
        subject = "Offer Letter From "
        message = f"Your OTP is Nice. It will expire in 5 minutes."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)

        offermanagement = OfferManagement.objects.filter(omrefid=omrefid).update(
            status="step4"
        )

        return Response({"msg": "Send Successfully"})


from datetime import datetime, timedelta, timezone
import pytz
import pickle
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from uuid import uuid4


from googleapiclient.errors import HttpError
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def offer_schedule_call(request, unique_id: str, omrefid: str):
    offermanagement = OfferManagement.objects.filter(omrefid=omrefid).values()
    for i in offermanagement:
        aid = i["applicant_id"]
    app = Applicant.objects.filter(id=aid).values()
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
                "client_id": "882310705492-sq44k182dibgd30ve6m585c9rq71ek0e.apps.googleusercontent.com",
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
        # CandidateInterview.objects.create(applicant=Applicant.objects.get(arefid=arefid), job=Job.objects.get(pk=jobpk), date_time_from=start_time, date_time_to=end_time)
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

        return JsonResponse(
            {"data": {"event_id": event["id"], "calendar_id": calendar_id}}
        )


class CreateUpdateInterviewApiView(APIView):
    serializer_class = InterviewCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, refid, arefid, *args, **kwargs):
        idss = request.POST.get("teamID")
        applicant = Applicant.objects.get(arefid=arefid)
        job = Job.objects.get(refid=refid)
        interviewObj = CandidateInterview.objects.create(
            applicant=applicant, job=job, user=request.user
        )
        if idss is not None and len(idss) > 0:
            arrlist = idss.split("|")
            farrlist = [eval(i) for i in arrlist]
            print(arrlist)
            for i in farrlist:
                interviewObj.add_interviewer.add(int(i))
        serializer = InterviewCreateUpdateSerializer(interviewObj, data=request.data)
        if serializer.is_valid(raise_exception=True):
            if SuperAdmin.objects.filter(user=request.user).exists():
                serializer.save(
                    org=OrganizationProfile.objects.get(user=request.user),
                )
            elif Organization.objects.filter(user=request.user).exists():
                sadmin = Organization.objects.filter(user=request.user).values()
                for i in sadmin:
                    sadmin_key = i["created_by_id"]

                serializer.save(
                    org=OrganizationProfile.objects.get(
                        SuperAdmin.objects.get(pk=sadmin_key)
                    ),
                )
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def put(self, request, irefid, *args, **kwargs):
        idss = request.POST.get("teamID")
        interview = CandidateInterview.objects.get(irefid=irefid)
        if idss is not None and len(idss) > 0:
            arrlist = idss.split("|")
            farrlist = [eval(i) for i in arrlist]
            print(arrlist)
            for i in farrlist:
                interview.add_interviewer.add(int(i))
        serializer = InterviewCreateUpdateSerializer(interview, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, irefid, *args, **kwargs):
        interview = CandidateInterview.objects.filter(irefid=irefid)
        interview.delete()
        return Response({"msg": "Deleted"}, status=204)


from django.db.models import Q


class PastInterviewListingApiView(generics.ListAPIView):
    serializer_class = ListInterViewSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        fuser = self.request.user
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
            my_date = datetime.now(pytz.utc)
            queryset = (
                self.model.objects.filter(
                    org=OrganizationProfile.objects.get(user=user)
                )
                .filter(date_time_from__lt=my_date)
                .order_by("date_time_from")
            )
        elif Organization.objects.filter(user=self.request.user).exists():
            orgobj = Organization.objects.filter(user=self.request.user).values()
            for i in orgobj:
                orgid = i["id"]

            print(orgid)
            my_date = datetime.now(pytz.utc)
            queryset = (
                self.model.objects.filter(Q(user=fuser) | Q(add_interviewer__id=orgid))
                .filter(date_time_from__lt=my_date)
                .order_by("date_time_from")
            )
        return queryset


class UpcomingInterviewListingApiView(generics.ListAPIView):
    serializer_class = ListInterViewSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        fuser = self.request.user
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
            my_date = datetime.now(pytz.utc)
            queryset = (
                self.model.objects.filter(
                    org=OrganizationProfile.objects.get(user=user)
                )
                .filter(date_time_from__gte=my_date)
                .order_by("date_time_from")
            )
        elif Organization.objects.filter(user=self.request.user).exists():
            orgobj = Organization.objects.filter(user=self.request.user).values()
            for i in orgobj:
                orgid = i["id"]

            print(orgid)
            my_date = datetime.now(pytz.utc)
            queryset = (
                self.model.objects.filter(Q(user=fuser) | Q(add_interviewer__id=orgid))
                .filter(date_time_from__gte=my_date)
                .order_by("date_time_from")
            )
        return queryset
