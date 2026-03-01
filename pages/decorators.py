from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def user_type_required(*allowed_types):
    """Project policy: any authenticated non-admin user can access app pages."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("home")

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


driver_required = user_type_required("driver", "admin")
admin_required = user_type_required("admin")


def superuser_required(view_func):
    """Allow access only to authenticated superusers."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please sign in to continue.")
            return redirect("login")

        if not request.user.is_superuser:
            messages.error(request, "Only superusers can access the admin dashboard.")
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return _wrapped
