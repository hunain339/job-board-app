from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """Custom permission to ensure user is authenticated."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsCandidate(permissions.BasePermission):
    """Permission to check if user is a Candidate."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'candidate'
        )


class IsEmployer(permissions.BasePermission):
    """Permission to check if user is an Employer."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'employer'
        )


class IsApprovedEmployer(permissions.BasePermission):
    """Permission to check if user is an approved Employer."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'employer' and
            request.user.is_approved_employer
        )


class IsAdminUser(permissions.BasePermission):
    """Permission to check if user is Admin."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsCandidateOwner(permissions.BasePermission):
    """
    Permission to check if the requesting user is the candidate owner
    of the application or job application.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.candidate == request.user


class IsEmployerOwner(permissions.BasePermission):
    """
    Permission to check if the requesting user is the employer owner
    of a job posting.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.employer == request.user


class IsApplicantOrEmployer(permissions.BasePermission):
    """
    Permission for application viewing:
    - Candidate can view their own applications
    - Employer can view applications to their jobs
    """
    
    def has_object_permission(self, request, view, obj):
        return (
            obj.candidate == request.user or
            obj.job.employer == request.user
        )
