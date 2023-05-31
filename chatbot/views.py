from django.shortcuts import render
from .serializers import *
from .models import *
from accounts.renderers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, status
import jwt
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAIChat
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from rest_framework.views import APIView


# Create your views here.

class ChatView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer

    def post(self, request,format=None):
        user= request.user
        chat = Chat.objects.create(user=user)
        serializer = ChatSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,pk,format=None):
        chat = Chat.objects.get(pk=pk)
        serializer = ChatSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListChatView(generics.ListAPIView):
    serializer_class = ListChatSerializer
    model = serializer_class.Meta.model
    paginate_by = 100
    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(user=user)
        return queryset


class InterviewQuestionGenerator(generics.GenericAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = InterviewQuestionGeneratorSerailizer
    
    def get(self, request, erefid):
        final_arr = []
        user = Candidate.objects.get(erefid=erefid)
        res = Resume.objects.filter(user=user)
        for i in res.values():
            text = i['full_text']
        final_dic = {}
        final_dic['Combined'] = text
        final_arr.append(final_dic)
        sources = []
        for i in final_arr:
            doc = Document(
                page_content=i['Combined'],
                metadata={"source": erefid},
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
        template = """You are a Hr AI Chat you have a Candidate Resume in this there are all the Data of the Candidate. Write 15 techniacal Question based on their Resume Skills and Technology.

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
        
        mainans = answer("Write 15 techniacal Question based on their Resume Skills and Technology")
        return Response({"res":mainans})


# from langchain.docstore.document import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores.faiss import FAISS
# from langchain.prompts import PromptTemplate
# from langchain.llms import OpenAIChat
# from langchain.chains.qa_with_sources import load_qa_with_sources_chain

# class ChatUserJobWiseView(APIView):
#     def post(self, request, refid, format=None):
#         prompt = request.POST.get('prompt')
#         print(prompt)
#         print("-------")
#         arr = []
#         dic = {}
#         dic2 = {}
#         final_arr = []
#         job = Job.objects.get(refid=refid)
#         # if SuperAdmin.objects.filter(user=self.request.user).exists():
#         #     user = self.request.user
#         # elif Organization.objects.filter(user=self.request.user).exists():
#         #     sadmin = Organization.objects.filter(user=self.request.user).values()
#         #     for i in sadmin:
#         #         sadmin_key = i['created_by_id']
            
#         #     user = SuperAdmin.objects.get(pk=sadmin_key)
#         # job = Job.objects.filter(refid=refid)
#         print(job)
#         for i in Candidate.objects.filter().values():
#             # print(i)
#             user = Candidate.objects.get(pk=i['id'])
#             queryset0 = Candidate.objects.filter(pk=i['id'])
#             # arr.append(i['erefid'])
#             queryset1 = Skill.objects.filter(user=user, job=job)
#             queryset2 = CandidateExperience.objects.filter(user=user, job=job)
#             queryset3 = CandidateEducation.objects.filter(user=user, job=job)
#             queryset4 = Certificate.objects.filter(user=user, job=job)
#             queryset5 = Resume.objects.filter(user=user, job=job)
#             queryset6 = Link.objects.filter(user=user, job=job)
#             queryset7 = CandidateProfile.objects.filter(user=user, job=job)
#             if queryset7.count() != 0:
#                 print(queryset7)
#                 arr.append(i['erefid'])
#             # print(queryset1)
#             data = {
#                 # 'Candidatedata': queryset0,
#                 'cprofiledata': queryset7,
#                 'skilldata': queryset1,
#                 'linkdata': queryset6,
#                 'cexpdata': queryset2,
#                 'cedudata': queryset3,
#                 'cerdata': queryset4,
#                 'resumedata': queryset5,
#             }
#             serializer = UserProfileSerializer1(data)
#             dic[i['erefid']] = serializer.data
#         count = 1
#         for i in arr:
            
#             final_dic = {}
#             final_dic['No'] = count
#             count = count + 1
#             final_dic['refid'] = i
            
#             final_skill = []
#             final_summary = []
#             curr_sal = []
#             exp_sal = []
            
#             for j in dic[i]['Skill']:
#                 # print(j['title'])
#                 final_skill.append(j['title'])
#             final_dic['skill_title'] = ', '.join(final_skill)
#             for j in dic[i]['CandidateProfile']:
#                 final_summary.append(j['summary'])
#                 curr_sal.append(j['current_salary'])
#                 exp_sal.append(j['expected_salary'])
#             final_dic['cprofile_summary'] = ', '.join(final_summary)
#             final_dic['curr_sal'] = ', '.join(curr_sal)
#             final_dic['exp_sal'] = ', '.join(exp_sal)
#             final_dic['Combined'] = "Summary: " + final_dic['cprofile_summary'] + " ;Skills: " + final_dic['skill_title'] + " ;Current Salary: " + final_dic['curr_sal'] + " ;Expected Salary: " + final_dic['exp_sal']
#             final_arr.append(final_dic)
            
#         sources = []
#         for i in final_arr:
#             doc = Document(
#                 page_content=i['Combined'],
#                 metadata={"source": i['refid']},
#             )
#             # append the Document object to the list
#             sources.append(doc)
#         chunks = []
#         splitter = RecursiveCharacterTextSplitter(
#             separators=["\n", ".", "!", "?", ",", " ", "<br>"],
#             chunk_size=1024,
#             chunk_overlap=0
#         )
#         for source in sources:
#             for chunk in splitter.split_text(source.page_content):
#                 chunks.append(Document(page_content=chunk, metadata=source.metadata)) 
#         index = FAISS.from_documents(chunks, OpenAIEmbeddings(openai_api_key='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'))
#         template = """You are a chatbot who have candidates data of summary , skills, current salary, expected salary.

#         QUESTION: {question}
#         =========
#         {summaries}
#         =========
#         FINAL ANSWER:"""
#         PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
#         chain = load_qa_with_sources_chain(OpenAIChat(openai_api_key='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', temperature=0, model_name="gpt-3.5-turbo"), prompt=PROMPT)
#         def answer(question):
#             mainans = (
#                 chain(
#                     {
#                         "input_documents": index.similarity_search(question, k=4),
#                         "question": question,
#                     },
#                     return_only_outputs=True,
#                 )["output_text"]
#             )
#             print(mainans)
#             return mainans
        
#         mainans = answer(prompt)
#         return Response({"res":mainans})

import pinecone
from langchain.chains import VectorDBQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import openai

class ChatUserJobWiseView(APIView):
    def post(self, request, refid ,format=None):
        prompt = request.POST.get('prompt')
        final_arr= []
        openai.api_key='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'
        pinecone.init(api_key='7f1409cf-e246-4b48-810c-e8b6f9a6ef3b', environment='us-east1-gcp')
        index = pinecone.Index('somhako')        
        query = "Show all the Candidate"
        vectors = openai.Embedding.create(input=[query], model="text-embedding-ada-002")['data'][0]['embedding']
        
        result = index.query(top_k=1536, queries=[vectors], include_metadata=True)
        for i in result['results']:
            for j in i['matches']:
                final_arr.append(j['metadata'])
                
        sources = []
        for i in final_arr:
            if i['Job ID'] == refid:
                doc = Document(
                    page_content=i['text'],
                    metadata={"source": i['Candidate ID'],'Candidate ID': i['Candidate ID'], 'Job ID': i['Job ID'], 'Organization ID': i['Organization ID']},
                )
                sources.append(doc)
            else:
                continue
        # print(final_arr)
        chunks = []
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n", ".", "!", "?", ",", " ", "<br>"],
            chunk_size=1024,
            chunk_overlap=0
        )
        for i in sources:
            for chunk in splitter.split_text(i.page_content):
                # print(i.metadata)
                chunks.append(Document(page_content=chunk, metadata=i.metadata)) 
        data = FAISS.from_documents(chunks, OpenAIEmbeddings(openai_api_key='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'))
        template = """You are a Hr AI Assistance who have candidates data of summary , Skills, current salary, expected salary, Name, Email, Phone. You need to find the Candidates on the basis of questions and Return their Name and Email

        QUESTION: {question}
        =========
        {summaries}
        =========
        FINAL ANSWER:"""
        PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
        chain = load_qa_with_sources_chain(OpenAIChat(openai_api_key='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', temperature=0, model_name="gpt-3.5-turbo"), prompt=PROMPT)
        def answer(question):
            # print(chain)
            mainans = (
                chain(
                    {
                        "input_documents": data.similarity_search(question, k=4),
                        "question": question,
                    },
                    return_only_outputs=True,
                )["output_text"]
            )
            print(mainans)
            return mainans
        
        mainans = answer(prompt)
        
        return Response({"res":mainans})
    
class ChatUserOrganizationWiseView(APIView):
    permission_classes = [
            IsAuthenticated,
    ]
    
    def post(self, request ,format=None):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)

        oID = OrganizationProfile.objects.filter(user=user).values()
        for i in oID:
            unique_id = i["unique_id"]

        prompt = request.POST.get('prompt')
        final_arr= []
        openai.api_key='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'
        pinecone.init(api_key='7f1409cf-e246-4b48-810c-e8b6f9a6ef3b', environment='us-east1-gcp')
        index = pinecone.Index('somhako')        
        query = "Show all the Candidate"
        vectors = openai.Embedding.create(input=[query], model="text-embedding-ada-002")['data'][0]['embedding']
        
        result = index.query(top_k=1536, queries=[vectors], include_metadata=True)
        for i in result['results']:
            for j in i['matches']:
                final_arr.append(j['metadata'])
                
        sources = []
        for i in final_arr:
            if i['Organization ID'] == unique_id:
                doc = Document(
                    page_content=i['text'],
                    metadata={"source": i['Candidate ID'],'Candidate ID': i['Candidate ID'], 'Job ID': i['Job ID'], 'Organization ID': i['Organization ID']},
                )
                sources.append(doc)
            else:
                continue
        # print(final_arr)
        chunks = []
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n", ".", "!", "?", ",", " ", "<br>"],
            chunk_size=1024,
            chunk_overlap=0
        )
        for i in sources:
            for chunk in splitter.split_text(i.page_content):
                # print(i.metadata)
                chunks.append(Document(page_content=chunk, metadata=i.metadata)) 
        data = FAISS.from_documents(chunks, OpenAIEmbeddings(openai_api_key='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'))
        template = """You are a Hr AI Assistance who have candidates data of summary , Skills, current salary, expected salary, Name, Email, Phone. You need to find the Candidates on the basis of questions and Return their Name and Email

        QUESTION: {question}
        =========
        {summaries}
        =========
        FINAL ANSWER:"""
        PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
        chain = load_qa_with_sources_chain(OpenAIChat(openai_api_key='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', temperature=0, model_name="gpt-3.5-turbo"), prompt=PROMPT)
        def answer(question):
            # print(chain)
            mainans = (
                chain(
                    {
                        "input_documents": data.similarity_search(question, k=4),
                        "question": question,
                    },
                    return_only_outputs=True,
                )["output_text"]
            )
            print(mainans)
            return mainans
        
        mainans = answer(prompt)
        
        return Response({"res":mainans})
    

class NotificationView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        to_user = self.request.user
        notification = Notification.objects.create(from_user=user, to_user=to_user, Org=OrganizationProfile.objects.get(user=user))
        serializer = NotificationSerializer(notification ,data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.POST.get('refid'):
                refid = request.POST.get('refid')
                serializer.save(job = Job.objects.get(refid=refid))
            elif request.POST.get('arefid'):
                arefid = request.POST.get('arefid')
                serializer.save(applicant = Applicant.objects.get(arefid=arefid))
            elif request.POST.get('arefid'):
                arefid = request.POST.get('arefid')
                serializer.save(applicant = Applicant.objects.get(arefid=arefid))
            elif request.POST.get('irefid'):
                irefid = request.POST.get('irefid')
                serializer.save(interview = CandidateInterview.objects.get(irefid=irefid))
            else:
                serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)
        

class NotificationView2(APIView):
    serializer_class = NotificationSerializer
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        if SuperAdmin.objects.filter(user=user).exists():
            user = user
        elif Organization.objects.filter(user=user).exists():
            sadmin = Organization.objects.filter(user=user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        to_user =  User.objects.get(email=email)
        notification = Notification.objects.create(from_user=user, to_user=to_user, Org=OrganizationProfile.objects.get(user=user))
        serializer = NotificationSerializer(notification ,data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.POST.get('refid'):
                refid = request.POST.get('refid')
                serializer.save(job = Job.objects.get(refid=refid))
            elif request.POST.get('arefid'):
                arefid = request.POST.get('arefid')
                serializer.save(applicant = Applicant.objects.get(arefid=arefid))
            elif request.POST.get('arefid'):
                arefid = request.POST.get('arefid')
                serializer.save(applicant = Applicant.objects.get(arefid=arefid))
            elif request.POST.get('irefid'):
                irefid = request.POST.get('irefid')
                serializer.save(interview = CandidateInterview.objects.get(irefid=irefid))
            else:
                serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)
        

class ListingNotificationView(generics.ListAPIView):
    serializer_class = ListNotificationSerializer
    model = serializer_class.Meta.model
    # paginate_by = 100
    def get_queryset(self):
        queryset = self.model.objects.filter(to_user=self.request.user).order_by("-timestamp")
        return queryset

class ListingNotificationViewAdmin(generics.ListAPIView):
    serializer_class = ListNotificationSerializer
    model = serializer_class.Meta.model
    # paginate_by = 100
    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        org=OrganizationProfile.objects.get(user=user)
        queryset = self.model.objects.filter(Org=org).order_by("-timestamp")
        return queryset

class ListingNotificationView2(generics.ListAPIView):
    serializer_class = ListNotificationSerializer
    model = serializer_class.Meta.model
    # paginate_by = 100
    def get_queryset(self):
        queryset = self.model.objects.filter(to_user=self.request.user,read=False)
        return queryset

class ListingNotificationView22(generics.ListAPIView):
    serializer_class = ListNotificationSerializer
    model = serializer_class.Meta.model
    # paginate_by = 100
    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        org=OrganizationProfile.objects.get(user=user)
        queryset = self.model.objects.filter(Org=org,adminRead=False)
        return queryset

class ListingNotificationView3(generics.ListAPIView):
    serializer_class = ListNotificationSerializer
    model = serializer_class.Meta.model
    # paginate_by = 100
    def get_queryset(self):
        Notification.objects.filter(to_user=self.request.user).update(read=True)
        queryset = self.model.objects.filter(to_user=self.request.user,read=False)
        return queryset

class ListingNotificationView33(generics.ListAPIView):
    serializer_class = ListNotificationSerializer
    model = serializer_class.Meta.model
    # paginate_by = 100
    def get_queryset(self):
        if SuperAdmin.objects.filter(user=self.request.user).exists():
            user = self.request.user
        elif Organization.objects.filter(user=self.request.user).exists():
            sadmin = Organization.objects.filter(user=self.request.user).values()
            for i in sadmin:
                sadmin_key = i['created_by_id']
            
            user = SuperAdmin.objects.get(pk=sadmin_key)
        org=OrganizationProfile.objects.get(user=user)

        Notification.objects.filter(Org=org).update(adminRead=True)
        queryset = self.model.objects.filter(Org=org,adminRead=False)
        return queryset