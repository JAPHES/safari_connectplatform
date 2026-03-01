from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from .utils import is_approved_driver


class DriverRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "home"

    def test_func(self):
        return self.request.user.is_authenticated


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "home"

    def test_func(self):
        profile = getattr(self.request.user, "profile", None)
        return bool(self.request.user.is_staff or (profile and profile.user_type == "admin"))


class ApprovedDriverRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "home"

    def test_func(self):
        return is_approved_driver(self.request.user)

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Only approved drivers can offer rides. Complete verification and wait for approval.",
        )
        return redirect("dashboard")
