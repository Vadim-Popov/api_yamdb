from rest_framework import permissions

class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):

class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_staff
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS

            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


# class AdminNotAllowedOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return not request.user.is_staff

