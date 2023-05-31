from django.urls import path
from .views import *

urlpatterns = [
    path('create-job/', CreateJobAPIView.as_view(), name="Create-Job"),
    path('list-job/', JobListingApiView.as_view(), name="List-Job"),
    path('update-job/<str:refid>/', CreateJobAPIView.as_view(), name="Update-Job"),
    path('delete-job/<str:refid>/', CreateJobAPIView.as_view(), name="Delete-Job"),
    path('detail-job/<str:refid>/', JobDetailingApiView.as_view(), name="Detail-Job"),
    path('detail-list-job/', JobListingApiView.as_view(), name="detail-Job"),

    
    # path('applicant/apply/<str:erefid>/<str:refid>/', ApplicantApplyView.as_view(), name="apply-Job"),
    path('applicant/apply/<str:refid>/', ApplicantApplyView.as_view(), name="apply-Job"),
    path('applicant/check/<str:refid>/', ApplicantApplyView1.as_view(), name="apply-Job"),
    path('applicants/alls/<str:unique_id>/', CandidateApplicantDashboardView.as_view(), name="Lol"),

    
    # Applicant

    path('applicant/<str:arefid>/update/', ApplicantView.as_view(), name='update-applicant'),
    path('applicant/<str:erefid>/delete/', ApplicantView.as_view(), name='delete-applicant'),
    path('listapplicant/', ListApplicantView.as_view(), name='list-applicant'),
    path('listapplicant/<str:refid>/', ListApplicantView1.as_view(), name='list-applicant'),

    #feedback
    path('listfeedback/<str:arefid>/', ListFeedbackView.as_view(), name='list-feedback'),
    path('feedback/<str:arefid>/create/', FeedbackView.as_view(), name='create-feedback'),
    path('feedback/<int:pk>/update/', FeedbackView.as_view(), name='update-feedback'),
    path('currentuser/', CurrentUserView.as_view(), name='current-user'),
    
    # Offer Management
    path('create-offer/<str:arefid>/', CreateOfferManagementAPIView.as_view(), name="Create-offer"),
    path('update-offer/<str:omrefid>/', CreateOfferManagementAPIView.as_view(), name="Create-offer"),
    path('update-offer-step2/<str:omrefid>/', CreateOfferManagementAPIViewStep2.as_view(), name="Create-offer"),
    path('delete-offer/<int:pk>/', CreateOfferManagementAPIView.as_view(), name="Create-offer"),
    path('list-offer/', OfferManagementListingApiView.as_view(), name="Create-offer"),

    #offer feedback
    path('create-offerfeedback/<str:omrefid>/', CreateOfferFeedbackAPIView.as_view(), name="Create-offer-feedback"),
    path('list-offerfeedback/<str:omrefid>/', OfferFeedbackListingApiView.as_view(), name="List-offer-feedback"),
    path('send-email-offer/<str:omrefid>/', SendEmailOfferManagementAPIView.as_view(), name="List-offer-feedback"),
    
    path('offer-schedule-call/<str:unique_id>/<str:omrefid>/', offer_schedule_call, name="List-offer-feedback"),
    
    # Interview Create, Update, Delete, Get
    path('upcoming-listing-interview/', UpcomingInterviewListingApiView.as_view(), name="Interview-list"),
    path('past-listing-interview/', PastInterviewListingApiView.as_view(), name="Interview-list"),
    path('create-interview/<str:arefid>/<str:refid>/', CreateUpdateInterviewApiView.as_view(), name="Create-Job"),
    path('update-interview/<str:irefid>/', CreateUpdateInterviewApiView.as_view(), name="Update-Job"),
    path('delete-interview/<str:irefid>/', CreateUpdateInterviewApiView.as_view(), name="Delete-Job"),

]

