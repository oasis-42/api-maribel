# test_user_config.py
import os

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from yourapp.models import UserConfig

# Defina o DJANGO_SETTINGS_MODULE no código
os.environ["DJANGO_SETTINGS_MODULE"] = "api_maribel.settings"

import django

django.setup()

# Agora, você pode importar o que for necessário


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def client(user):
    client = APIClient()
    client.login(username="testuser", password="testpassword")
    return client


def test_user_config_view(client, user):
    user_config = UserConfig.objects.create(
        user=user, config_key="theme", config_value="dark"
    )

    response = client.get(f"/api/user-config/{user_config.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["config_key"] == "theme"
    assert response.data["config_value"] == "dark"


def test_update_user_config(client, user):
    user_config = UserConfig.objects.create(
        user=user, config_key="theme", config_value="dark"
    )
    new_data = {"config_value": "light"}

    response = client.put(f"/api/user-config/{user_config.id}/", new_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["config_value"] == "light"
