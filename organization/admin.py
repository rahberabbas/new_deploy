from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *
from django import forms

class AddOrganizationForm(forms.ModelForm):
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
        model = Organization
        fields = ('email','name','organization_permissions', 'role','created_by','dept')

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


class UpdateOrganizationForm(forms.ModelForm):
    """
    Update User Form. Doesn't allow changing password in the Admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Organization
        fields = (
            'email', 'password','created_by','name', 'role', 'organization_permissions','dept',
        )

    def clean_password(self):
# Password can't be changed in the admin
        return self.initial["password"]


class EmployerAdmin(BaseUserAdmin):
    form = UpdateOrganizationForm
    add_form = AddOrganizationForm

    list_display = ('email','created_by','name', 'orefid', 'role','dept')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('created_by', 'name', 'verified', 'orefid', 'role','organization_permissions','dept')}),
        # ('Permissions', {'fields': ('is_active', 'staff','admin')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email','name','created_by', 'password1', 'organization_permissions',
                    'password2','dept'
                )
            }
        ),
    )
    search_fields = ()
    ordering = ('email','created_by','name')
    filter_horizontal = ()

admin.site.register(Organization,EmployerAdmin)
admin.site.register(OrganizationPermission)


class AddSuperAdminForm(forms.ModelForm):
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
        model = SuperAdmin
        fields = ('email','company_name','name',)

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


class UpdateSuperAdminForm(forms.ModelForm):
    """
    Update User Form. Doesn't allow changing password in the Admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = SuperAdmin
        fields = (
            'email', 'password','company_name','name',
        )

    def clean_password(self):
# Password can't be changed in the admin
        return self.initial["password"]


class EmployerSuperAdmin(BaseUserAdmin):
    form = UpdateSuperAdminForm
    add_form = AddSuperAdminForm

    list_display = ('email','company_name','name', 'srefid')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('company_name', 'name', 'verified', 'srefid')}),
        # ('Permissions', {'fields': ('is_active', 'staff','admin')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email','company_name','name', 'password1',
                    'password2'
                )
            }
        ),
    )
    search_fields = ()
    ordering = ('email','company_name','name')
    filter_horizontal = ()

admin.site.register(SuperAdmin,EmployerSuperAdmin)
admin.site.register(OrganizationProfile)
admin.site.register(OrganizationGallery)
admin.site.register(OrganizationFounder)
admin.site.register(IndividualProfile)
admin.site.register(IndividualLink)
admin.site.register(OrganizationCalendarIntegration)
admin.site.register(OrganizationMailIntegration)
admin.site.register(ActivityLog)