from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from ..forms import UserForm


class UserSettingsView(TemplateView):
    """
    View to see user settings
    """

    template_name = "user_settings.html"

    def get(self, request, *args, **kwargs):
        user_form = UserForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

        return render(
            request,
            self.template_name,
            {"user_form": user_form, "password_form": password_form},
        )

    def post(self, request, *args, **kwargs):
        """
        This function updates the settings
        """
        form_type = request.POST["form_type"]

        if form_type == "general":
            user_form = UserForm(data=request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, _("Your settings were successfully updated!"))

            password_form = PasswordChangeForm(request.user)

        if form_type == "password":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _("Your password was successfully updated!"))

            user_form = UserForm(instance=request.user)

        return render(
            request,
            self.template_name,
            {"user_form": user_form, "password_form": password_form},
        )
