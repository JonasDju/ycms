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
WSGI config for hospitool project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import configparser
import os

from django.core.wsgi import get_wsgi_application


# pylint: disable=duplicate-code
def application(environ, start_response):
    """
    This returns the WSGI callable

    :param environ: The environment variables
    :type environ: dict

    :param start_response: A function which starts the response
    :type start_response: ~collections.abc.Callable

    :return: The WSGI callable
    :rtype: ~django.core.handlers.WSGIHandler
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospitool.core.settings")

    # Read config from config file
    config = configparser.ConfigParser(interpolation=None)
    config.read("/etc/hospitool.ini")
    for section in config.sections():
        for KEY, VALUE in config.items(section):
            os.environ.setdefault(f"HOSPITOOL_{KEY.upper()}", VALUE)

    # Read config from environment
    for key in environ:
        if key.startswith("HOSPITOOL_"):
            os.environ[key] = environ[key]

    _application = get_wsgi_application()

    return _application(environ, start_response)
