# test_essay.py
import pytest
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient
import os
from django.conf import settings

# Defina o DJANGO_SETTINGS_MODULE no código
os.environ['DJANGO_SETTINGS_MODULE'] = 'api_maribel.settings'

import django
django.setup()

# Agora, você pode importar o que for necessário
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def mock_process_ocr():
    with patch('yourapp.views.process_ocr') as mock:
        yield mock

def test_text_extraction_view(client, mock_process_ocr):
    # Simule uma resposta bem-sucedida do OCR
    mock_process_ocr.return_value = {'text': 'Texto extraído', 'confidence': 0.95}

    url = '/api/text-extraction/'
    data = {'base64': 'base64_imagem'}

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'Texto extraído' in response.data['text']