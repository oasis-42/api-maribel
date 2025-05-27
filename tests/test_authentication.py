# test_authentication.py

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import os
from django.conf import settings

# Defina o DJANGO_SETTINGS_MODULE no código
os.environ['DJANGO_SETTINGS_MODULE'] = 'api_maribel.settings'

import django
django.setup()

# Agora, você pode importar o que for necessário
from rest_framework.test import APIClient


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpassword")

@pytest.fixture
def client():
    return APIClient()

def test_activate(client, user):
    # Suponha que você tenha um link de ativação de conta
    uid = "encoded_user_id"  # Você pode codificar o ID do usuário manualmente para os testes
    token = "valid_token"

    url = reverse('account:activate', kwargs={'uid': uid, 'token': token})
    response = client.get(url)

    assert response.status_code == 200
    assert 'Your account has been activated successfully.' in response.content.decode()

def test_password_reset_confirm(client, user):
    uid = "encoded_user_id"
    token = "valid_token"
    url = reverse('account:password_reset_confirm', kwargs={'uid': uid, 'token': token})

    response = client.get(url)
    assert response.status_code == 200