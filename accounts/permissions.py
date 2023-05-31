from rest_framework import permissions

class OrganizationAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.organization.role == "ORGANISATION_ADMIN":
            return True

class HiringManager(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.organization.role == "HIRING_MANAGER":
            return True

class Recruiter(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.organization.role == "RECRUITER":
            return True

