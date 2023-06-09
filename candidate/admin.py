from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *
from django import forms

class AddCandidateForm(forms.ModelForm):
    """
    New User Form. Requires password confirmation.
    """
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirm password', widget=forms.PasswordInput
    )

    class Meta:
        model = Candidate
        fields = ('email','first_name','last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UpdateCandidateForm(forms.ModelForm):
    """
    Update User Form. Doesn't allow changing password in the Admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Candidate
        fields = (
            'email', 'password','first_name','last_name', 'organizations','erefid'
        )

    def clean_password(self):
# Password can't be changed in the admin
        return self.initial["password"]


class CandidateAdmin(BaseUserAdmin):
    form = UpdateCandidateForm
    add_form = AddCandidateForm

    list_display = ('email','first_name','last_name','erefid')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name','mobile','verified', 'organizations','erefid')}),
        # ('Permissions', {'fields': ('is_active', 'staff','admin')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email','first_name','last_name', 'password1',
                    'password2', 'organizations'
                )
            }
        ),
    )
    search_fields = ()
    ordering = ('email','first_name','last_name')
    filter_horizontal = ()

admin.site.register(Candidate,CandidateAdmin)
admin.site.register(CandidateProfile)
admin.site.register(Link)
admin.site.register(Skill)
admin.site.register(CandidateEducation)
admin.site.register(CandidateExperience)
admin.site.register(Certificate)
admin.site.register(Resume)

