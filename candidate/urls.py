from django.urls import path
from .views import *

urlpatterns = [
    path('candidate-email-registration/<str:unique_id>/', CandidateRegistrationEmailView.as_view(), name='register'),
    path('candidate-id-registration/<str:unique_id>/', CandidateRegistrationIDView.as_view(), name='register'),
    path('candidatelogin/', CLoginAPIView.as_view(), name='login'),
    path('candidatecheck/<str:erefid>/<str:oid>/', CLoginAPIViewCheck1.as_view(), name='login'),
    path('verify-otp/<str:unique_id>/', VerifyOTPView.as_view(), name='verify_otp'),

    path('listuser/<str:erefid>/<str:refid>/', ListUserView.as_view(), name='list-candidate-profile'),
    path('listuser1/', ListUserView1.as_view(), name='list-candidate-profile'),
    path('chatuserjob/<str:refid>/', ChatUserJobWiseView.as_view(), name='list-candidate-profile'),

    #Candidate Profile

    # path('candidateprofile/<str:erefid>/<str:refid>/', FinalCandidateProfileView.as_view(), name='create-candidate-profile'),
    path('candidateprofile/<str:refid>/', FinalCandidateProfileView.as_view(), name='create-candidate-profile'),
    path('candidateprofile/<str:erefid>/<str:refid>/<int:pk>/update/', FinalCandidateProfileView.as_view(), name='update-candidate-profile'),
    path('candidateprofile/<str:erefid>/<str:refid>/<int:pk>/delete/', FinalCandidateProfileView.as_view(), name='delete-candidate-profile'),
    path('listcandidateprofile/<str:erefid>/<str:refid>/', ListCandidateProfileView.as_view(), name='list-candidate-profile'),

    # path('candidateprofile/<str:erefid>/<str:refid>/', CandidateProfileView.as_view(), name='candidate-profile'),
    # path('candidateprofileaccont/<str:erefid>/', CandidateAccountView.as_view(), name='candidate-profile-accont'),
    # path('candidatebio/<str:erefid>/<str:refid>/', BioView.as_view(), name='candidate-bio'),

    # Skill

    path('candidateskill/<str:erefid>/<str:refid>/', SkillView.as_view(), name='create-candidate-skill'),
    path('candidateskill/<str:erefid>/<str:refid>/<int:pk>/update/', SkillView.as_view(), name='update-candidate-skill'),
    path('candidateskill/<str:erefid>/<str:refid>/<int:pk>/delete/', SkillView.as_view(), name='delete-candidate-skill'),
    path('listskill/<str:erefid>/<str:refid>/', ListSkillView.as_view(), name='list-candidate-skill'),

    # Link

    path('candidatelink/<str:erefid>/<str:refid>/', LinkView.as_view(), name='create-candidate-link'),
    path('candidatelink/<str:erefid>/<str:refid>/<int:pk>/update/', LinkView.as_view(), name='update-candidate-link'),
    path('candidatelink/<str:erefid>/<str:refid>/<int:pk>/delete/', LinkView.as_view(), name='delete-candidate-link'),
    path('listlink/<str:erefid>/<str:refid>/', ListLinkView.as_view(), name='list-candidate-link'),

    # Resume

    # path('candidateresume/<str:erefid>/<str:refid>/', ResumeView.as_view(), name='create-candidate-resume'),
    path('candidateresume/<str:refid>/', ResumeView.as_view(), name='create-candidate-resume'),
    path('candidateresume/<str:erefid>/<str:refid>/<int:pk>/update/', ResumeView.as_view(), name='update-candidate-resume'),
    path('candidateresume/<str:erefid>/<str:refid>/<int:pk>/delete/', ResumeView.as_view(), name='delete-candidate-resume'),
    path('listresume/<str:erefid>/<str:refid>/', ListResumeView.as_view(), name='list-candidate-resume'),

    # Certificate

    path('candidatecertificate/<str:erefid>/<str:refid>/', CertificateView.as_view(), name='create-candidate-certificate'),
    path('candidatecertificate/<str:erefid>/<str:refid>/<int:pk>/update/', CertificateView.as_view(), name='update-candidate-certificate'),
    path('candidatecertificate/<str:erefid>/<str:refid>/<int:pk>/delete/', CertificateView.as_view(), name='delete-candidate-certificate'),
    path('listcertificate/<str:erefid>/<str:refid>/', ListCertificateView.as_view(), name='list-candidate-certificate'),
    

    # Education

    path('candidateeducation/<str:erefid>/<str:refid>/', EducationView.as_view(), name='create-candidate-education'),
    path('candidateeducation/<str:erefid>/<str:refid>/<int:pk>/update/', EducationView.as_view(), name='update-candidate-education'),
    path('candidateeducation/<str:erefid>/<str:refid>/<int:pk>/delete/', EducationView.as_view(), name='delete-candidate-education'),
    path('listeducation/<str:erefid>/<str:refid>/', ListEducationView.as_view(), name='list-candidate-education'),

    # Experience

    path('candidateexperience/<str:erefid>/<str:refid>/', ExperienceView.as_view(), name='create-candidate-experience'),
    path('candidateexperience/<str:erefid>/<str:refid>/<int:pk>/update/', ExperienceView.as_view(), name='update-candidate-experience'),
    path('candidateexperience/<str:erefid>/<str:refid>/<int:pk>/delete/', ExperienceView.as_view(), name='delete-candidate-experience'),
    path('listexperience/<str:erefid>/<str:refid>/', ListExperienceView.as_view(), name='list-candidate-experience'),


]