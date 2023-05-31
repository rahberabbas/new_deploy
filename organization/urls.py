from django.urls import path
from .views import *

urlpatterns = [
    path('registration/superadmin/', SuperAdminRegistrationView.as_view(), name='register'),
    # path('orgregister/', OrgRegistrationView.as_view(), name='register'),
    path('create/org/user/', OrganizationAdminCreateView.as_view(), name='register'),
    path('listorguser/', ListOrganizationUserView.as_view(), name='list'),
    path('updateorguser/<int:pk>/', OrganizationAdminCreateView.as_view(), name='update'),

    path('login/', LoginAPIView.as_view(), name='login'),

    path('permission/', OrganizationUserAdminPermissions.as_view(), name='login'),
    # path('userinfo/<str:orefid>/', UserInfi.as_view(), name='login'),
    path('job/', OrganizationUserJobPermissions.as_view(), name='login'),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),


    #Organization Profie
    path('organizationprofile/update/', OrganizationProfileView.as_view(), name='update-organization-Profie'),
    path('listorganizationprofile/', ListOrganizationProfileView.as_view(), name='get-organization-Profie'),
    path('list_organization_account/', ListOrganizationAccountView.as_view(), name='get-organization-account'),
    path('list_organization_account_and_individual_profile/', ListOrganizationAccountAndProfilesView.as_view(), name='get-organization-account-and-individual-profile'),
    
    path('get/organizationprofilecid/carrier/<str:cname>/', CarrierOrgView1.as_view(), name='get-organization-Profie-CarrierID'),

    path('get/organizationprofile/carrier/<str:unique_id>/', CarrierOrgView.as_view(), name='get-organization-Profie-Carrier'),
    path('get/organizationprofile/vendor/<int:pk>/', CarrierOrgView3.as_view(), name='get-organization-Profie-Vendorr'),
    
    #Organization Gallery
    path('listorganizationgallery/', ListOrganizationGalleryView.as_view(), name='list-organization-gallery'),
    path('organizationgallery/', OrganizationGalleryAPIView.as_view(), name='create-organization-gallery'),
    path('organizationgallery/<int:pk>/delete/', OrganizationGalleryAPIView.as_view(), name='delete-organization-gallery'),
    
    #Organization FOunder
    path('listorganizationfounder/', ListOrganizationFounderView.as_view(), name='list-organization-founder'),
    path('organizationfounder/', OrganizationFounderAPIView.as_view(), name='create-organization-founder'),
    path('organizationfounder/<int:pk>/update/', OrganizationFounderAPIView.as_view(), name='update-organization-founder'),
    path('organizationfounder/<int:pk>/delete/', OrganizationFounderAPIView.as_view(), name='delete-organization-founder'),
    
    #Individual Profie
    path('individualprofile/update/', IndividualProfileView.as_view(), name='update-individual-Profie'),
    path('listindividualprofile/', ListIndividualProfileView.as_view(), name='get-individual-Profie'),
    
    #Individual Link 
    path('individuallink/<str:uniqueid>/', IndividualLinkView.as_view(), name='create-individual-link'),
    path('individuallink/<str:uniqueid>/<int:pk>/update/', IndividualLinkView.as_view(), name='update-individual-link'),
    path('individuallink/<str:uniqueid>/<int:pk>/delete/', IndividualLinkView.as_view(), name='delete-individual-link'),
    path('listindividuallink/<str:uniqueid>/', ListIndividualLinkView.as_view(), name='list-individual-link'),
    
    # Calendar Integration
    path('create_calendar_integration/<str:unique_id>/', create_calendar_integration, name='create-calendar-integration'),
    path('delete_calendar_integration/<int:integration_id>/', delete_calendar_integration, name='delete-calendar-integration'),
    path('integrations/calendar/<str:unique_id>/', get_calendar_integration, name='get-calendar-integration'),
    
    # Calendar Automation
    path('integrations/calendar_automation/<str:unique_id>/<str:arefid>/', calander_automation, name='get-calendar-integration'),
    path('integrations/update_calendar_automation/<str:unique_id>/<str:calendar_id>/<str:event_id>/', update_calander_automation, name='get-calendar-integration'),
    path('integrations/calendar_get_free_slots/<str:unique_id>/', calendar_choose_slots, name='get-free-slots'),

    # Mail Integration
    path('create_mail_integration/<str:unique_id>/', create_mail_integration, name='create-mail-integration'),
    path('delete_mail_integration/<int:integration_id>/', delete_mail_integration, name='delete-mail-integration'),
    path('integrations/mail/<str:unique_id>/', get_mail_integration, name='get-mail-integration'),
    path('email_inbox/mail/<str:unique_id>/', email_inbox, name='get-mail-integration'),
    path('email_inbox_send/mail/<str:unique_id>/', email_inbox_send, name='get-mail-integration'),
    
    
    path('get_dashboard_and_analytics/', DashboardCandidatesApiView.as_view(), name='get-mail-integration'),
    path('activity-log/', ActivityLogView.as_view(), name='activity-log'),
    path('activity-log/unauth/', ActivityLogView2.as_view(), name='activity-log'),
    path('list-activity-log/', ListingActivityLogView.as_view(), name='activity-log'),
]