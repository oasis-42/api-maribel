import json
import base64

from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from openai import OpenAI
from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from google.cloud import vision
from google.oauth2 import service_account
from django.conf import settings
from django.contrib.auth.models import User

from .models import RefinedEssayText, OriginalEssayText, Theme, UserConfig, MotivationalText
from .serializers import FeedbackDtoSerializer, CapturedPictureSerializer, RefinedEssayTextSerializer, \
    OriginalEssayTextSerializer, ThemeSerializer, UserConfigSerializer, UserSerializer, MotivationalTextSerializer

import openai

openai.api_key = settings.OPENAI_API_KEY

service_account_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = vision.ImageAnnotatorClient(credentials=credentials)

client_chat_gpt = OpenAI()


def activate(request, uid, token):
    uid = force_str(urlsafe_base64_decode(uid))
    user = User.objects.get(pk=uid)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Your account has been activated successfully.')
    else:
        return HttpResponse('Activation link is invalid!', status=400)


def password_reset_confirm(request, uid, token):
    uid = force_str(urlsafe_base64_decode(uid))
    user = User.objects.get(pk=uid)

    if default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form, 'uid': uid, 'token': token})
    else:
        return HttpResponse('Token is invalid or has expired', status=400)

class SendTestMailView(APIView):
    def post(self, request):
        send_mail("Teste", "TESTE ENVIO DE EMAIL", settings.EMAIL_FROM, ['contato@maribel.cloud'])
        return Response(status=status.HTTP_200_OK)

class TextExtractionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CapturedPictureSerializer

    def post(self, request):
        serializer = CapturedPictureSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        content = base64.b64decode(serializer.validated_data['base64'])
        image = vision.Image(content=content)
        ocr_response = client.document_text_detection(image=image)
        average_confidence = self.get_average_confidence(ocr_response)

        try:
            text = self.get_corrected_text(ocr_response)
            return Response({'text': text, 'confidence': average_confidence})
        except ValueError:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_corrected_text(self, ocr_response):
        chat_gpt_response = client_chat_gpt.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": """Você é um assistente que receberá um texto em portugues vindo de um OCR e corrigirá as 
                 palavras que achar incorretas visando um português valido, não criará um texto novo, apenas corrigirá 
                 as palavras que o OCR trouxer com gramática errada e retornará a resposta 
                 em JSON com uma propriedade 'text'"""},
                {"role": "user", "content": ocr_response.full_text_annotation.text}
            ]
        )

        json_content = json.loads(chat_gpt_response.choices[0].message.content)
        return json_content["text"]

    def get_average_confidence(self, ocr_response):
        confidences_per_block = [
            block.confidence
            for page in ocr_response.full_text_annotation.pages
            for block in page.blocks
        ]

        return sum(confidences_per_block) / len(confidences_per_block)


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackDtoSerializer

    def post(self, request):
        serializer = FeedbackDtoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data['text']

        chat_gpt_response_verificacao_redacao = client_chat_gpt.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "Baseado no tema do enem de  2018, Manipulação do comportamento de usuário pelo controle de dados na internet.  Verifique se não de forma explícita e muito problemática os problemas listados a seguir: PLÁGIO: Grandes partes do texto são uma cópia de obras conhecidas sem menção ou citação.  FUGA DE TEMA: O texto apresentado não possui uma estrutura dissertativa argumentativa, ou não se enquadra ao tema proposto de forma alguma. VIOLAÇÕES DOS DIREITOS HUMANOS: O texto se usa de linguagem agressiva como opiniões pessoais do autor refletindo em violações dos direitos humanos. Em aspectos graves como, apologia a violência, preconceito, etc… Verifique se não há esse problema para o texto, e se não houver retorne apenas:  “TEXTO OK” Caso contrário, e exista um problema evidente, retorne apenas nas seguintes propriedades do json forma. falha: falha apontada dentro dos problemas listados. motivo: Trechos que se enquadrem e justificativas para ser enquadrado no problema apresentado. Considere esse problemas apresentados para texto enviado a seguir"},
                {"role": "user", "content": text}
            ]
        )

        json_content_verificacao_redacao = json.loads(chat_gpt_response_verificacao_redacao.choices[0].message.content)

        chat_gpt_response_avaliacao_redacao = client_chat_gpt.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": """Baseado no tema do enem de  2018, Manipulação do comportamento de usuário pelo controle de dados na internet. 
                 INSTRUÇÕES DE AVALIAÇÃO Avalie para todas as competências do ENEM: 
                 1. Domínio da escrita formal da língua portuguesa 
                 2. Compreender o tema e não fugir do que é proposto 
                 3. Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista. 
                 4. Conhecimento dos mecanismos linguísticos necessários para a construção da argumentação. 
                 5. Respeito aos direitos humanos. 
                 Assim, apresente as considerações para cada uma das competências nas seguintes propriedades json, 
                 todas as propriedades json com letras minúsculas, sem acento e seguindo camel case: 
                 
                 [
                    {
                        "analyzedSkill": "1" 
                        "grade": 120,
                        "feedback": "",
                        "successes": [
                            {
                                "excerpt": "",
                                "reason": ""
                            }                        
                        ],
                        "errors": [
                            {
                                "excerpt": "",
                                "reason": ""
                                "howToCorrect": ""
                            } 
                        ]
                    },
                ]
                 
                 COMPETÊNCIA número e nome da competência do enem analisada 
                 NOTA  Número de 0 a 200 para a nota da competência analisada 
                 PARECER Parecer geral sobre a competência analisada 
                 ACERTOS trechos do texto que apresentam acertos em relação a competência, apresentando o trecho e por que se aplica 
                 ERROS trechos do texto que apresentam erros e por que se aplicam 
                 SUGESTÕES apresentação dos trechos com erros, reescritos de uma forma mais adequada a competência analisada 
                 Avalie utilizando as INSTRUÇÕES DE AVALIAÇÃO para a seguinte redação:"""},
                {"role": "user", "content": text}
            ]
        )

        json_content_avaliacao_redacao = json.loads(chat_gpt_response_avaliacao_redacao.choices[0].message.content)

        return Response({
            "verificacao_redacao": json_content_verificacao_redacao,
            "avaliacao_redacao": json_content_avaliacao_redacao
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefinedEssayTextView(RetrieveAPIView):
    queryset = RefinedEssayText.objects.all()
    serializer_class = RefinedEssayTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OriginalEssayText.objects.filter(feedback__user=user)


class OriginalEssayTextView(RetrieveAPIView):
    queryset = OriginalEssayText.objects.all()
    serializer_class = OriginalEssayTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OriginalEssayText.objects.filter(feedback__user=user)


class ThemeView(ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]


class UserConfigView(RetrieveUpdateAPIView):
    queryset = UserConfig.objects.all()
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserConfig.objects.filter(user=user)

class MotivationalTextByThemeView(generics.ListAPIView):
    serializer_class = MotivationalTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        theme_id = self.kwargs['theme_id']
        return MotivationalText.objects.filter(theme_id=theme_id)
