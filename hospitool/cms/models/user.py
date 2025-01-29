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
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.core.exceptions import PermissionDenied
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import group_names, job_types
from .abstract_base_model import AbstractBaseModel


class CustomUserManager(BaseUserManager):
    """
    This manager provides custom methods for user creation
    """

    def create_user(
        self,
        creator,
        personnel_id,
        email,
        group,
        assigned_ward=None,
        is_active=False,
        **extra_fields,
    ):
        """
        Create a new user and ensure they are added to the correct group (if any)

        :param creator: the user who attempts to create this new user
        :type creator: ~hospitool.cms.models.user.User

        :param personnel_id: employee's ID
        :type personnel_id: int

        :param email: email address of the user, also used in lieu of username
        :type email: str

        :param group: one of :attr:`~hospitool.cms.constants.group_names.CHOICES`
        :type group: str

        :param assigned_ward: the ward this user is assigned to or None
        :type assigned_ward: ~hospitool.cms.models.ward.Ward

        :param is_active: Whether this user should be active
        :type is_active: bool

        :param extra_fields: additional fields
        :type extra_fields: dict

        :return: the newly created user
        :rtype: ~hospitool.cms.models.users.user.User
        """
        # Check that no user is able to create over-privileged new users
        if not self.filter(id=creator.id).exists() or not (
            creator.is_superuser
            or str(group)
            in dict(group_names.IS_CREATABLE_BY[str(creator.group)]).keys()
        ):
            raise PermissionDenied()

        email = self.normalize_email(email)
        user = self.model(
            creator=creator,
            personnel_id=personnel_id,
            email=email,
            assigned_ward=assigned_ward,
            is_active=is_active,
            **extra_fields,
        )

        user.set_password(None)
        user.save(using=self._db)

        user.groups.add(Group.objects.get(name=group))
        user.save()

        return user

    def create_superuser(self, personnel_id, email, password=None, **extra_fields):
        """
        Create a new super user

        :param personnel_id: employee's ID
        :type personnel_id: int

        :param email: email address of the user, also used in lieu of username
        :type email: str

        :param password: user password
        :type password: str

        :param extra_fields: additional fields
        :type extra_fields: dict

        :return: the newly created user
        :rtype: ~hospitool.cms.models.users.user.User
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(personnel_id, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    A custom User model that replaces the default Django User model.
    """

    creator = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(default=timezone.now, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    personnel_id = models.CharField(
        null=True,
        unique=True,
        verbose_name=_("personnel ID"),
        help_text=_(
            "Employment ID number of the hospital staff. Used for authentication."
        ),
        max_length=10,
        validators=[MinLengthValidator(10)],
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("email"),
        help_text=_("Valid email address for this user"),
    )
    job_type = models.CharField(
        null=True,
        max_length=16,
        verbose_name=_("job type"),
        help_text=_("Job type of the employee"),
        choices=job_types.CHOICES,
    )
    first_name = models.CharField(
        null=True,
        max_length=32,
        verbose_name=_("first name"),
        help_text=_("First name of the employee"),
    )
    last_name = models.CharField(
        null=True,
        max_length=64,
        verbose_name=_("last name"),
        help_text=_("Last name of the employee"),
    )
    assigned_ward = models.ForeignKey(
        "cms.Ward",
        null=True,
        blank=True,
        verbose_name=_("Ward"),
        help_text=_("Ward this employee is assigned to (if any)"),
        on_delete=models.SET_NULL,
    )
    ward_as_timeline = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "personnel_id"
    REQUIRED_FIELDS = ["email", "job_type", "first_name", "last_name"]

    @cached_property
    def group(self):
        """
        Return the primary group of this user

        :return: The first group of this user
        :rtype: ~django.contrib.auth.models.Group
        """
        return self.groups.first()

    @cached_property
    def title(self):
        """
        Return the title of this user

        :return: The title of this user
        :rtype: str
        """
        return dict(job_types.CHOICES)[self.job_type]

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``User object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the user
        :rtype: str
        """
        return f"{self.job_type} {self.first_name} {self.last_name}"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<User: User object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the user
        :rtype: str
        """
        fields = [
            f"id: {self.id}",
            f"personnel_id: {self.personnel_id}",
            f"email: {self.email}",
            f"job_type: {self.job_type}",
            f"first_name: {self.first_name}",
            f"last_name: {self.last_name}",
            f"group: {self.groups.first()}",
            f"is_staff: {self.is_staff}",
        ]
        return f"<User ({', '.join(fields)})>"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["personnel_id"]
        default_permissions = ("add", "change", "delete", "view")
