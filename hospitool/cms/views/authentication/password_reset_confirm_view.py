# Copyright [2019] [Integreat Project]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext as _

from ...models import User
from ...utils.token_generator import password_reset_token_generator

logger = logging.getLogger(__name__)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    View to set a new password.
    """

    token_generator = password_reset_token_generator
    template_name = "authentication/password_reset_confirm.html"
    success_url = reverse_lazy("cms:public:login")

    def dispatch(self, *args, **kwargs):
        r"""
        The view part of the view. Handles all HTTP methods equally.

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: The rendered template response or a redirection to the login page
        :rtype: ~django.template.response.TemplateResponse or ~django.http.HttpResponseRedirect
        """
        if self.request.user.is_authenticated:
            messages.success(self.request, _("You are already logged in."))
            return redirect("cms:protected:index")

        user = User.objects.filter(
            pk=int(urlsafe_base64_decode(kwargs.get("uidb64")))
        ).first()
        if not user:
            messages.error(
                self.request,
                _("The account you are trying to set a password for does not exist."),
            )
            return redirect("cms:protected:index")

        if self.token_generator.check_token(user, kwargs.get("token")):
            user.is_active = True
            user.save()
            logger.info("Account activation for user %r was successful", user)

        response = super().dispatch(*args, **kwargs)
        if isinstance(response, HttpResponseRedirect) or self.validlink:
            # If the link is valid, render the password reset confirm form (redirect means valid because the first step
            # is to store the token in a session variable and redirect to the generic [...]-set-password/ url)
            return response
        messages.error(
            self.request,
            " ".join(
                [
                    _("This password reset link is invalid."),
                    _("It may have already been used."),
                    _("Please request a new link to reset your password."),
                ]
            ),
        )
        logger.debug("An invalid account activation link was used.")
        return redirect("cms:public:password_reset_request")

    def form_valid(self, form):
        """
        If the form is valid, show a success message.

        :param form: The supplied form
        :type form: ~django.contrib.auth.forms.SetPasswordForm

        :return: form validation
        :rtype: ~django.http.HttpResponse

        """
        messages.success(
            self.request,
            " ".join(
                [
                    _("Your password has been successfully reset."),
                    _("You can now log in with your new password."),
                ]
            ),
        )
        logger.info("The password for %r was changed.", form.user)
        return super().form_valid(form)
