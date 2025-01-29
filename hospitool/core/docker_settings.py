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
Django settings for different database configuration.
The docker container started in :github-source:`tools/run.sh` exposes the alternative port ``5434``.

All other settings are imported from :mod:`~hospitool.core.settings`.

For more information on this file, see :doc:`django:topics/settings`.
For the full list of settings and their values, see :doc:`django:ref/settings`.
"""
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from .settings import *

#: A dictionary containing the settings for all databases to be used with this Django installation
#: (see :setting:`django:DATABASES`)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hospitool",
        "USER": "hospitool",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5434",
    }
}
