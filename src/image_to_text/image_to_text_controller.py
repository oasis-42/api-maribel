from pydantic import BaseModel
from fastapi import APIRouter, UploadFile
from google.cloud import vision
import json

from openai import OpenAI

client_chat_gpt = OpenAI()

router = APIRouter(prefix="/api/v1/ocr", tags=["image_to_text"])

client = vision.ImageAnnotatorClient()


class FeedbackDto(BaseModel):
    text: str


@router.post("/feedback")
async def get_feedback(dto: FeedbackDto):
    chat_gpt_response_verificacao_redacao = client_chat_gpt.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Baseado no tema do enem de  2018, Manipulação do comportamento de usuário pelo controle de dados na internet.  Verifique se não de forma explícita e muito problemática os problemas listados a seguir: PLÁGIO: Grandes partes do texto são uma cópia de obras conhecidas sem menção ou citação.  FUGA DE TEMA: O texto apresentado não possui uma estrutura dissertativa argumentativa, ou não se enquadra ao tema proposto de forma alguma. VIOLAÇÕES DOS DIREITOS HUMANOS: O texto se usa de linguagem agressiva como opiniões pessoais do autor refletindo em violações dos direitos humanos. Em aspectos graves como, apologia a violência, preconceito, etc… Verifique se não há esse problema para o texto, e se não houver retorne apenas:  “TEXTO OK” Caso contrário, e exista um problema evidente, retorne apenas nas seguintes propriedades do json forma. falha: falha apontada dentro dos problemas listados. motivo: Trechos que se enquadrem e justificativas para ser enquadrado no problema apresentado. Considere esse problemas apresentados para texto enviado a seguir"},
            {"role": "user", "content": dto.text}
        ]
    )

    json_content_verificacao_redacao = json.loads(chat_gpt_response_verificacao_redacao.choices[0].message.content)

    chat_gpt_response_avaliacao_redacao = client_chat_gpt.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Baseado no tema do enem de  2018, Manipulação do comportamento de usuário pelo controle de dados na internet. INSTRUÇÕES DE AVALIAÇÃO Avalie para todas as competências do ENEM: 1.Domínio da escrita formal da língua portuguesa 2.Compreender o tema e não fugir do que é proposto 3.Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista. 4.Conhecimento dos mecanismos linguísticos necessários para a construção da argumentação. 5. Respeito aos direitos humanos. Assim, apresente as considerações para cada uma das competências nas seguintes propriedades json, todas as propriedades json com letras minúsculas: COMPETÊNCIA número e nome da competência do enem analisada NOTA  Número de 0 a 200 para a nota da competência analisada PARECER Parecer geral sobre a competência analisada ACERTOS trechos do texto que apresentam acertos em relação a competência, apresentando o trecho e por que se aplica ERROS trechos do texto que apresentam erros e por que se aplicam SUGESTÕES apresentação dos trechos com erros, reescritos de uma forma mais adequada a competência analisada Avalie utilizando as INSTRUÇÕES DE AVALIAÇÃO para a seguinte redação:"},
            {"role": "user", "content": dto.text}
        ]
    )

    json_content_avaliacao_redacao = json.loads(chat_gpt_response_avaliacao_redacao.choices[0].message.content)

    return {
        "verificacao_redacao": json_content_verificacao_redacao,
        "avaliacao_redacao": json_content_avaliacao_redacao
    }


@router.post("/")
async def process_ocr(file: UploadFile):
    response = await get_ocr_response(file)
    average_confidence = get_average_confidence(response)
    text = get_corrected_text(response)
    return {
        "text": text,
        "confidence": average_confidence
    }


async def get_ocr_response(file):
    content = await file.read()
    image = vision.Image(content=content)
    return client.document_text_detection(image=image)


def get_corrected_text(response):
    chat_gpt_response = client_chat_gpt.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Você é um assistente que receberá um texto em portugues vindo de um OCR e corrigirá as palavras que achar incorretas visando um português valido, não criará um texto novo, apenas corrigirá as palavras que o OCR trouxer com gramática errada e retornará a resposta em JSON com uma propriedade 'text'"},
            {"role": "user", "content": response.full_text_annotation.text}
        ]
    )
    json_content = json.loads(chat_gpt_response.choices[0].message.content)
    return json_content["text"]


def get_average_confidence(response):
    confidences_per_block = [
        block.confidence
        for page in response.full_text_annotation.pages
        for block in page.blocks
    ]

    return sum(confidences_per_block) / len(confidences_per_block)
