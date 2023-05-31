from django.urls import path
from .views import *

urlpatterns = [
    path('new_vendor/', NewVendorApiView.as_view(), name='new-vendor'),
    path('vendor_data/<str:vrefid>/', VendorDataView.as_view(), name='vendor-data'),
    path('vendor_data1/<str:email>/', VendorDataView1.as_view(), name='vendor-data'),
    path('vendor_data2/<str:vrefid>/', VendorDataView2.as_view(), name='vendor-data'),
    path('vendor_registration/<str:vrefid>/', VendorRegistrationView.as_view(), name='vendor-registration'),
    path('vendor_login/', VendorLoginAPIView.as_view(), name='vendor-login'),
    path('list_vendors/', ListVendorApiView.as_view(), name='vendor-list'),
    path('onboard_list_vendors/<str:unique_id>/', OnboardVendorListApiView.as_view(), name='vendor-list'),
    path('onboard_vendors/<str:vrefid>/', OnboardVendorApiView.as_view(), name='vendor-onboard'),
    path('activate_vendors/<str:vrefid>/', ActivateVendorApiView.as_view(), name='vendor-onboard'),

    
    path('vendor_job_data/<str:vrefid>/', VendorDataView3.as_view(), name='vendor-data'),
    
    # Vendor Profile
    path('vendor-candidate/<str:refid>/<str:vrefid>/', VendorCandidateProfileView.as_view(), name='create-candidate-profile'),
    path('vendor-candidate/<str:refid>/<str:vrefid>/<int:pk>/update/', VendorCandidateProfileView.as_view(), name='update-candidate-profile'),
    path('vendor-candidate/<str:refid>/<str:vrefid>/<int:pk>/delete/', VendorCandidateProfileView.as_view(), name='delete-candidate-profile'),
    
    # Vendor Social Link
    path('vendor-candidate-social/<str:refid>/<str:vcrefid>/', VendorCandidateSocialLinkView.as_view(), name='create-candidate-profile'),
    path('vendor-candidate-social/<str:refid>/<str:vcrefid>/<int:pk>/update/', VendorCandidateSocialLinkView.as_view(), name='update-candidate-profile'),
    path('vendor-candidate-social/<str:refid>/<str:vcrefid>/<int:pk>/delete/', VendorCandidateSocialLinkView.as_view(), name='delete-candidate-profile'),
    
    # Vendor cretificate Link
    path('vendor-candidate-cretificate/<str:refid>/<str:vcrefid>/', VendorCandidateCertificateView.as_view(), name='create-candidate-profile'),
    path('vendor-candidate-cretificate/<str:refid>/<str:vcrefid>/<int:pk>/update/', VendorCandidateCertificateView.as_view(), name='update-candidate-profile'),
    path('vendor-candidate-cretificate/<str:refid>/<str:vcrefid>/<int:pk>/delete/', VendorCandidateCertificateView.as_view(), name='delete-candidate-profile'),
    
    # Vendor education Link
    path('vendor-candidate-education/<str:refid>/<str:vcrefid>/', VendorCandidateEducationView.as_view(), name='create-candidate-profile'),
    path('vendor-candidate-education/<str:refid>/<str:vcrefid>/<int:pk>/update/', VendorCandidateEducationView.as_view(), name='update-candidate-profile'),
    path('vendor-candidate-education/<str:refid>/<str:vcrefid>/<int:pk>/delete/', VendorCandidateEducationView.as_view(), name='delete-candidate-profile'),
    
    # Vendor experience Link
    path('vendor-candidate-experience/<str:refid>/<str:vcrefid>/', VendorCandidateExperienceView.as_view(), name='create-candidate-profile'),
    path('vendor-candidate-experience/<str:refid>/<str:vcrefid>/<int:pk>/update/', VendorCandidateExperienceView.as_view(), name='update-candidate-profile'),
    path('vendor-candidate-experience/<str:refid>/<str:vcrefid>/<int:pk>/delete/', VendorCandidateExperienceView.as_view(), name='delete-candidate-profile'),
    
    # Vendor Applicant Apply View
    path('vendor-applicant-apply/<str:refid>/<str:vrefid>/<str:vcrefid>/', VendorApplicantApplyView.as_view(), name="vendor-applicant-apply"),


    #vendor Applicant list
    path('vendor-list/<str:refid>/<str:vrefid>/', ListVendorApplicantView.as_view(), name="vendor-applicant-list"),

    #list Applicant Detail
    path('vendoruser/<str:refid>/<str:vcrefid>/', ListVendorCanView.as_view(), name='list-vendor-candidate-profile'),
]