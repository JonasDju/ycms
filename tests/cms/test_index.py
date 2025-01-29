import pytest
from django.test.client import Client
from django.urls import reverse

from hospitool.cms.models import User


@pytest.mark.django_db
def test_medical_personnel_default_view(load_test_data):
    """
    Check if logged-in medical personnel are being redirected according to their roles default view

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :type load_test_data: tuple
    """
    client = Client()
    # Login the DR_0000001 user of group MEDICAL_PERSONNEL
    client.force_login(User.objects.get(id=4))

    view_name = "cms:protected:index"
    endpoint = reverse(view_name)
    response = client.get(endpoint, {}, format="html", content_type="text/html")
    assert response.status_code == 302
    assert response.url == "/patients/"


@pytest.mark.django_db
def test_stationmanager_default_view(load_test_data):
    """
    Check if logged-in station managers are being redirected according to their roles default view

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :type load_test_data: tuple
    """
    client = Client()
    # Login the STATION_MG user of group STATION_MANAGER
    client.force_login(User.objects.get(id=3))

    view_name = "cms:protected:index"
    endpoint = reverse(view_name)
    response = client.get(endpoint, {}, format="html", content_type="text/html")
    assert response.status_code == 302
    assert response.url == "/ward/"


@pytest.mark.django_db
def test_default_default_view(load_test_data):
    """
    Check if logged-in root users are being redirected according to the default index view

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    :type load_test_data: tuple
    """
    client = Client()
    # Login the ROOT user, who has no group
    client.force_login(User.objects.get(id=1))

    view_name = "cms:protected:index"
    endpoint = reverse(view_name)
    response = client.get(endpoint, {}, format="html", content_type="text/html")
    assert response.status_code == 302
    assert response.url == "/ward/"
