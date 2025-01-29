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
Debug lists and forms for all models
"""
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

if settings.DEBUG:
    admin.site.register(apps.get_model("auth", "Permission"))
    for model in apps.get_app_config("cms").get_models():
        admin.site.register(model)
    for model in apps.get_app_config("admin").get_models():
        admin.site.register(model)
    for model in apps.get_app_config("contenttypes").get_models():
        admin.site.register(model)
    for model in apps.get_app_config("sessions").get_models():
        admin.site.register(model)
else:
    admin.site.register(get_user_model())
