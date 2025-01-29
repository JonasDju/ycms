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

from django.contrib.auth.views import redirect_to_login
from django.urls import resolve

from ...cms.constants import namespaces

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class AccessControlMiddleware:
    """
    Middleware class that performs a basic access control. For urls that are whitelisted (see
    :attr:`~hospitool.core.middleware.access_control_middleware.AccessControlMiddleware.whitelist`), no additional
    rules are enforced.
    For all other urls, the user has to be logged in.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware for the current view

        :param get_response: A callable to get the response for the current request
        :type get_response: ~collections.abc.Callable
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Call the middleware for the current request

        :param request: Django request
        :type request: ~django.http.HttpRequest

        :return: The response
        :rtype: ~django.http.HttpResponse
        """
        resolver_match = resolve(request.path)
        if (
            namespaces.PUBLIC not in resolver_match.namespaces
            and not request.user.is_authenticated
            and "admin" not in resolver_match.namespaces
        ):
            return redirect_to_login(request.path)
        return self.get_response(request)
