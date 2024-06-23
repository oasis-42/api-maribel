import json
import base64

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
        theme_id = serializer.validated_data['theme_id']

        try:
            theme = Theme.objects.get(theme=theme_id)

            json_content_refined_essay = self.get_refined_essay(text, theme)
            json_content_essay_analysis = self.analyse_essay(text, theme)

            return Response({
                "refinedEssay": json_content_refined_essay['refinedEssay'],
                "essayAnalysis": json_content_essay_analysis["essayAnalysis"]
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def analyse_essay(self, text, theme):
        filter_by_theme = f"Baseado no tema do enem de {theme.year}, {theme.title}. "

        content = """
        INSTRUÇÕES DE AVALIAÇÃO Avalie para todas as competências do ENEM: 
        1. Domínio da escrita formal da língua portuguesa 
        2. Compreender o tema e não fugir do que é proposto 
        3. Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista. 
        4. Conhecimento dos mecanismos linguísticos necessários para a construção da argumentação. 
        5. Respeito aos direitos humanos. 
        Assim, apresente as considerações para cada uma das 5 competências nas seguintes propriedades json, 
        todas as propriedades json com letras minúsculas, sem acento e seguindo camel case, o nome das propriedades em inglês mas o conteúdo em pt-br, 
        seguindo o seguinte formato deverá ser retornando  com um objeto do json para cada competência: 
         
        {
            "essayAnalysis": [
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
        } 
        
        Legenda:
        analyzedSkill: o número de um a 1 referente a competência do ENEM.
        grade: o número de 0 a 200 para a nota de competência analisada.
        feedback: Parecer geral sobre a competência analisada.
        successes: [
            {
                excerpt: trecho do texto que apresenta os acertos em relação a competência
                reason: explicação do motivo que o trecho está errado
            } 
        ], 
        errors: [
            {
                excerpt: trecho do texto que apresenta os erros em relação a competência
                reason: explicação do motivo que o trecho está errado
                howToCorrect: como corrigir o trecho que está errado
            } 
        ] 
        
        Avalie utilizando as INSTRUÇÕES DE AVALIAÇÃO para a seguinte redação:
        """

        return self.send_to_chat_gpt(content, filter_by_theme, text)

    def get_refined_essay(self, text, theme):
        filter_by_theme = f"Baseado no tema do enem de {theme.year}, {theme.title}. "

        content = """
        Corrija a redação a seguir, reescrevendo a mesma em um formato mais adequado as proposta de texto argumentativo aos moldes do Enem. 
        Retorne um formato json seguindo camelCase no nome das propriedades, sem acento e com o nome das propriedades em inglês mas o conteúdo em pt-br,
        seguindo o seguinte formato, deverá ser retornado um objeto json para introdução, desenvolvimento, conclusão.
         
        {
            "refinedEssay": [
                {
                    "paragraphType": "introduction",
                    "originalText": "orignal text",
                    "refinedText": "revised text",
                }, 
            ]
        }
         
        Legenda:
        paragraphType: tipo do paragrafo, se é introdução (introduction), desenvolvimento (development) ou conclusão (conclusion)
        originalText: trecho original do texto, antes da correção
        refinedText: trecho corrigido e melhorado conforme as diretrizes do enem 
        Aplique para o texto a seguir:
        """

        return self.send_to_chat_gpt(content, filter_by_theme, text)

    def send_to_chat_gpt(self, content, filter_by_theme, text):
        chat_gpt_response = client_chat_gpt.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": filter_by_theme + content
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        json_content = json.loads(chat_gpt_response.choices[0].message.content)
        return json_content

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
