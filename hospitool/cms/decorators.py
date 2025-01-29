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
"""
Django view decorators can be used to restrict the execution of a view function on certain conditions.

For more information, see :doc:`django:topics/http/decorators`.
"""

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def permission_required(permission):
    """
    Decorator for views that checks whether a user has a particular permission enabled.
    If not, the PermissionDenied exception is raised.

    :param permission: The required permission
    :type permission: str

    :return: The decorated function
    :rtype: ~collections.abc.Callable
    """

    def check_permission(user):
        """
        This function checks the permission of a user

        :param user: The user, that is checked
        :type user: ~hospitool.cms.models.users.user.User

        :raises ~django.core.exceptions.PermissionDenied: If user doesn't have the given permission

        :return: Whether this account has the permission or not
        :rtype: bool
        """

        if user.has_perm(permission):
            return True
        raise PermissionDenied(f"{user!r} does not have the permission {permission!r}")

    return user_passes_test(check_permission)
