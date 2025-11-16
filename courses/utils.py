# courses/utils.py 
from django.core.exceptions import PermissionDenied

def instructor_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'instructor':
                return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def student_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'student':
                return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap