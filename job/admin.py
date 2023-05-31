from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Job)
admin.site.register(Applicant)
admin.site.register(Feedback)

admin.site.register(VendorCandidateProfile)
admin.site.register(VendorCandidateCertificate)
admin.site.register(VendorCandidateEducation)
admin.site.register(VendorCandidateExperience)
admin.site.register(VendorCandidateSocialLink)
admin.site.register(VendorApplicant)
admin.site.register(CandidateInterview)


admin.site.register(OfferManagement)
admin.site.register(OfferFeedback)