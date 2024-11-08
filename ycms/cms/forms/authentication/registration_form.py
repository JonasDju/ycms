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

from django import forms
from django.utils.translation import gettext as _

from ...constants import group_names
from ...models import User
from ..custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class RegistrationForm(CustomModelForm):
    """
    Form for user self-registration
    """

    group = forms.ChoiceField(
        choices=[("", "---------")],
        required=True,
        initial="",
        label=_("Permission group"),
        help_text=_("Determines what permissions the user will have"),
    )

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = User
        fields = [
            "personnel_id",
            "email",
            "job_type",
            "first_name",
            "last_name",
            "assigned_ward",
        ]

    def __init__(self, *args, **kwargs):
        r"""
        Initialize user registration form

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict
        """
        super().__init__(*args, **kwargs)

        self.fields["group"].choices += (
            group_names.IS_CREATABLE_BY[str(self.instance.creator.group)]
            if not self.instance.creator.is_superuser
            else group_names.CHOICES
        )

    def clean_personnel_id(self):
        """
        Ensure the personnel_id does not exist yet, see :ref:`overriding-modelform-clean-method`:
        If the personnel_id is already registered, add a :class:`~django.core.exceptions.ValidationError`.

        :return: The personnel_id
        :rtype: str
        """

        personnel_id = self.cleaned_data["personnel_id"]
        if User.objects.filter(personnel_id=personnel_id).first():
            self.add_error(
                "personnel_id",
                forms.ValidationError(
                    _(
                        'An account for the personnel ID "{}" does already exist.'
                    ).format(personnel_id)
                ),
            )
        return personnel_id

    def clean_email(self):
        """
        Ensure the email does not exist yet, see :ref:`overriding-modelform-clean-method`:
        If the email is already registered, add a :class:`~django.core.exceptions.ValidationError`.

        :return: The email
        :rtype: str
        """

        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).first():
            self.add_error(
                "email",
                forms.ValidationError(
                    _('An account for the email "{}" does already exist.').format(email)
                ),
            )
        return email

    def save(self, commit=True):
        """
        This method extends the default ``save()``-method of the base :class:`~django.forms.ModelForm`
        to create a new non-active user with role nurse.

        :param commit: Whether or not the changes should be written to the database
        :type commit: bool

        :return: The saved user
        :rtype: ~ycms.cms.models.user.User
        """
        cleaned_data = self.cleaned_data
        new_user = User.objects.create_user(
            creator=self.instance.creator,
            personnel_id=cleaned_data["personnel_id"],
            email=cleaned_data["email"],
            job_type=cleaned_data["job_type"],
            first_name=cleaned_data["first_name"],
            last_name=cleaned_data["last_name"],
            group=cleaned_data["group"],
            assigned_ward=cleaned_data["assigned_ward"],
            is_active=False,
        )

        logger.debug("Created new user %s", self.cleaned_data["personnel_id"])
        return new_user
