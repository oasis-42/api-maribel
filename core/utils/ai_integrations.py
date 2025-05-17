import json
import base64

from django.conf import settings
from google.cloud import vision
from google.oauth2 import service_account
from openai import OpenAI

service_account_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
credentials = service_account.Credentials.from_service_account_info(service_account_info)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def process_ocr(base64_content):
    content = base64.b64decode(base64_content)
    image = vision.Image(content=content)
    ocr_response = vision_client.document_text_detection(image=image)
    average_confidence = _get_average_confidence(ocr_response)
    try:
        text = _get_corrected_text(ocr_response)
        return {'text': text, 'confidence': average_confidence}
    except ValueError:
        raise ValueError("Could not process text from image.")


def _get_corrected_text(ocr_response):
    chat_gpt_response = openai_client.chat.completions.create(
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


def _get_average_confidence(ocr_response):
    confidences_per_block = [
        block.confidence
        for page in ocr_response.full_text_annotation.pages
        for block in page.blocks
    ]
    return sum(confidences_per_block) / len(confidences_per_block) if confidences_per_block else 0


def analyse_essay_with_gpt(text, theme):
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
                "analyzedSkill": "1",
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
                        "reason": "",
                        "howToCorrect": ""
                    }
                ]
            }
        ]
    }

    Legenda:
    analyzedSkill: o número de um a 5 referente a competência do ENEM.
    grade: o número de 0 a 200 para a nota de competência analisada.
    feedback: Parecer geral sobre a competência analisada.
    successes: [
        {
            excerpt: trecho do texto que apresenta os acertos em relação a competência,
            reason: explicação do motivo que o trecho está correto
        }
    ],
    errors: [
        {
            excerpt: trecho do texto que apresenta os erros em relação a competência,
            reason: explicação do motivo que o trecho está errado,
            howToCorrect: como corrigir o trecho que está errado
        }
    ]

    Avalie utilizando as INSTRUÇÕES DE AVALIAÇÃO para a seguinte redação:
    """
    return _send_to_chat_gpt(content, filter_by_theme, text)


def refine_essay_with_gpt(text, theme):
    filter_by_theme = f"Baseado no tema do enem de {theme.year}, {theme.title}. "
    content = """
    Corrija a redação a seguir, reescrevendo a mesma em um formato mais adequado as proposta de texto argumentativo aos moldes do Enem.
    Retorne um formato json seguindo camelCase no nome das propriedades, sem acento e com o nome das propriedades em inglês mas o conteúdo em pt-br,
    seguindo o seguinte formato, deverá ser retornado um objeto json para introdução, desenvolvimento, conclusão.

    {
        "refinedEssay": [
            {
                "paragraphType": "introduction",
                "originalText": "original text",
                "refinedText": "revised text",
            }
        ]
    }

    Legenda:
    paragraphType: tipo do paragrafo, se é introdução (introduction), desenvolvimento (development) ou conclusão (conclusion)
    originalText: trecho original do texto, antes da correção
    refinedText: trecho corrigido e melhorado conforme as diretrizes do enem
    Aplique para o texto a seguir:
    """
    return _send_to_chat_gpt(content, filter_by_theme, text)


def _send_to_chat_gpt(content, filter_by_theme, text):
    chat_gpt_response = openai_client.chat.completions.create(
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
    try:
        json_content = json.loads(chat_gpt_response.choices[0].message.content)
        return json_content
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        print(f"Erro ao processar resposta do ChatGPT: {e}, Content: {chat_gpt_response.choices[0].message.content if chat_gpt_response.choices else 'No content'}")
        return {}