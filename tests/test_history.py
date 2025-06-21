# test_history.py

import os

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from yourapp.models import OriginalEssayText, RefinedEssayText

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


def test_refined_essay_text_view(client, user):
    # Crie um exemplo de RefinedEssayText
    essay = RefinedEssayText.objects.create(original_essay=some_essay, user=user)

    # Requisição GET para a view
    response = client.get(
        "/api/refined-essay-text/"
    )  # URL que você configurou para a view

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == essay.id


def test_original_essay_text_view(client, user):
    essay = OriginalEssayText.objects.create(original_essay=some_essay, user=user)

    response = client.get("/api/original-essay-text/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == essay.id
