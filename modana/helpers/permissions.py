from django.core.urlresolvers import resolve

from rest_framework.permissions import BasePermission


class PermissionMixin(BasePermission):
    def has_permission(self, request, view):
        url_name = resolve(request.path_info).url_name
        method = request.method.lower()
        user = request.user
        return url_name, method, user

    def has_object_permission(self, request, view, obj):
        try:
            model = view.queryset.model or view.model
        except AttributeError:
            raise Exception("It seems the view is not associated with any model.\
Please overwrite this method as per need.")

        try:
            method_name = "can_{}".format(view.action or request.method.lower())
            return not not getattr(obj, method_name)(request)
        except AttributeError as e:
            print(e)
            raise Exception("Please implement {}.{}.".format(model, method_name))
