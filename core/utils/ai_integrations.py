import json
import base64

from django.conf import settings
from google.cloud import vision
from google.oauth2 import service_account
from openai import OpenAI

from ai_prompts import OcrCorrectionPrompt, EssayAnalysisPrompt, RefinedEssayPrompt

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
        text = _get_corrected_text(ocr_response, ocr_response.full_text_annotation.text)
        return {'text': text, 'confidence': average_confidence}
    except ValueError:
        raise ValueError("Could not process text from image.")


def _get_corrected_text(ocr_response, extracted_text):
    chat_gpt_response = openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": OcrCorrectionPrompt.get_prompt()},
            {"role": "user", "content": extracted_text}
        ]
    )
    try:
        json_content = json.loads(chat_gpt_response.choices[0].message.content)
        return json_content["text"]
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        print(f"Erro ao processar resposta do ChatGPT (correção OCR): {e}, Content: {chat_gpt_response.choices[0].message.content if chat_gpt_response.choices else 'No content'}")
        return extracted_text  # Retorna o texto original em caso de erro


def _get_average_confidence(ocr_response):
    confidences_per_block = [
        block.confidence
        for page in ocr_response.full_text_annotation.pages
        for block in page.blocks
    ]
    return sum(confidences_per_block) / len(confidences_per_block) if confidences_per_block else 0


def analyse_essay_with_gpt(text, theme):
    filter_by_theme = f"Baseado no tema do enem de {theme.year}, {theme.title}. "
    prompt_content = EssayAnalysisPrompt.get_instructions()
    return _send_to_chat_gpt(prompt_content, filter_by_theme, text, "análise de redação")


def refine_essay_with_gpt(text, theme):
    filter_by_theme = f"Baseado no tema do enem de {theme.year}, {theme.title}. "
    prompt_content = RefinedEssayPrompt.get_instructions()
    return _send_to_chat_gpt(prompt_content, filter_by_theme, text, "refinamento de redação")


def _send_to_chat_gpt(prompt_content, filter_by_theme, text, context_name=""):
    messages = [
        {"role": "system", "content": filter_by_theme + prompt_content},
        {"role": "user", "content": text}
    ]
    chat_gpt_response = openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=messages
    )
    try:
        json_content = json.loads(chat_gpt_response.choices[0].message.content)
        return json_content
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        print(f"Erro ao processar resposta do ChatGPT ({context_name}): {e}, Content: {chat_gpt_response.choices[0].message.content if chat_gpt_response.choices else 'No content'}")
        return {}