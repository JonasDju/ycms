# Copyright [2019] [Integreat Project]
# Copyright [2023] [YCMS]
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
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from ...decorators import permission_required
from ...forms import RegistrationForm
from ...utils.email_utils import send_activation_mail

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.add_user"), name="dispatch")
class RegistrationView(CreateView):
    """
    View allowing new users to sign up as offer providers
    """

    template_name = "authentication/create_user.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("cms:protected:create_user")

    def get_form_kwargs(self):
        """
        Return the keyword arguments for instantiating the form

        :return: The form kwargs
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs["additional_instance_attributes"] = {"creator": self.request.user}
        return kwargs

    def form_valid(self, form):
        r"""
        Overwrite the form_valid method to additionally send a confirmation email

        :param form: The user-submitted form
        :type form: ~hospitool.cms.forms.registration_form.RegistrationForm
        """
        response = super().form_valid(form)
        messages.success(
            self.request,
            _(
                'A confirmation email has been sent to "{}". Please use the link in the email to activate the account.'
            ).format(self.object.email),
        )

        send_activation_mail(self.object)
        return response
