from rest_framework import permissions


class BlacklistPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists() # true / false
        return not blacklisted


class AnonPermissionOnly(permissions.BasePermission):
    message = 'You are already authenticated. Please log out to try again.'
    """
    Non-authenicated Users only
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated # request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    message  = 'You must be the owner of this content to change.'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        # if obj.user == request.user:
        #     return True
        return obj.owner == request.user

class IsStaffReadWriteOrAuthReadOnly(permissions.BasePermission):
    message  = 'You do not have sufficient permissions to perform this operation'
    """
    Object-level permission to only allow realtor change content.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            print("I am in permissions")
            print(request.user)
            print(request.user.is_authenticated)
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    message  = 'You must be the owner of this content to change.'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        # if obj.user == request.user:
        #     return True
        if request.user.is_staff:
          return True
        return obj.user == request.user

class UserViewPermission(permissions.BasePermission):
    message  = 'You must be the owner of this content to change.'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
          return True
        return ((request.user.is_staff) & (not obj.is_superuser))
        #if request.user.is_superuser:
        #  return True
        #return obj == request.user
        #return ((request.user.is_staff) & (not obj.is_superuser))



class IsAdminOwner(permissions.BasePermission):
    message  = 'You must be the owner of this content to change.'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        # Instance must have an attribute named `owner`.
        # if obj.user == request.user:
        #     return True
        if request.user.is_staff:
          return True
        return obj.user == request.user
