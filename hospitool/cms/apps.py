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
from django.apps import AppConfig
from django.utils.translation import gettext as __
from django.utils.translation import gettext_lazy as _


class CmsConfig(AppConfig):
    """
    This class represents the Django-configuration of the CMS.

    See :class:`django.apps.AppConfig` for more information.

    :param name: The name of the app
    :type name: str
    """

    name = "hospitool.cms"
    verbose_name = _("CMS")

    def ready(self):
        # pylint: disable-next=import-outside-toplevel
        from django.contrib.auth.models import Group

        Group.__str__ = lambda self: __(self.name)
