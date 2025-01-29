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
import pytest
from django.contrib import auth
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("personnel_id", ["ROOT_00001", "ZBM_000001"])
def test_login_success(load_test_data, client, settings, personnel_id):
    """
    Test whether login via personnel_id works as expected

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :type load_test_data: tuple

    :param client: The fixture providing the an unauthenticated user client
    :type client: :fixture:`client`

    :param settings: The Django settings
    :type settings: :fixture:`settings`

    :param personnel_id: The personnel_id to use for login
    :type personnel_id: str
    """
    response = client.post(
        reverse(settings.LOGIN_URL),
        data={"username": personnel_id, "password": "changeme"},
    )
    assert response.status_code == 302
    user = auth.get_user(client)
    assert user.is_authenticated


@pytest.mark.django_db
@pytest.mark.parametrize(
    "personnel_id",
    ["root", "manager@hospitool.de", "ROOT_00001", "non-existing-email@example.com", ""],
)
def test_login_failure(load_test_data, client, settings, personnel_id):
    """
    Test whether login with incorrect credentials does not work

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :type load_test_data: tuple

    :param client: The fixture providing the an unauthenticated user client
    :type client: :fixture:`client`

    :param settings: The Django settings
    :type settings: :fixture:`settings`

    :param personnel_id: The personnel_id to use for login
    :type personnel_id: str
    """
    settings.LANGUAGE_CODE = "en"
    response = client.post(
        reverse(settings.LOGIN_URL),
        data={"username": personnel_id, "password": "incorrect"},
    )
    assert response.status_code == 200
    assert "The username or the password is incorrect." in response.content.decode()
