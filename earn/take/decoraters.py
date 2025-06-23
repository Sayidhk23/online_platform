# decorators.py
from django.core.exceptions import PermissionDenied


def instructor_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_instructor:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return wrap
