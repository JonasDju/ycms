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
"""
Django URL dispatcher for the cms package.
See :mod:`~hospitool.core.urls` for the other namespaces of this application.

For more information on this file, see :doc:`django:topics/http/urls`.
"""

from django.urls import include, path

from ..constants import namespaces

#: The namespace for this URL config (see :attr:`django.urls.ResolverMatch.app_name`)
app_name = "cms"

#: The url patterns of this module (see :doc:`django:topics/http/urls`)
urlpatterns = [
    path("", include(("hospitool.cms.urls.public", app_name), namespace=namespaces.PUBLIC)),
    path(
        "",
        include(("hospitool.cms.urls.protected", app_name), namespace=namespaces.PROTECTED),
    ),
]
