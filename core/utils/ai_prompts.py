class OcrCorrectionPrompt:
    @staticmethod
    def get_prompt():
        return """Você é um assistente que receberá um texto em português vindo de um OCR e corrigirá as
palavras que achar incorretas visando um português válido, não criará um texto novo, apenas corrigirá
as palavras que o OCR trouxer com gramática errada e retornará a resposta
em JSON com uma propriedade 'text'"""


class EssayAnalysisPrompt:
    @staticmethod
    def get_instructions():
        return """INSTRUÇÕES DE AVALIAÇÃO Avalie para todas as competências do ENEM:
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
        "excerpt": "trecho do texto que apresenta os acertos em relação a competência",
        "reason": "explicação do motivo que o trecho está correto"
    }
],
errors: [
    {
        "excerpt": "trecho do texto que apresenta os erros em relação a competência",
        "reason": "explicação do motivo que o trecho está errado",
        "howToCorrect": "como corrigir o trecho que está errado"
    }
]

Avalie utilizando as INSTRUÇÕES DE AVALIAÇÃO para a seguinte redação:
"""


class RefinedEssayPrompt:
    @staticmethod
    def get_instructions():
        return """Corrija a redação a seguir, reescrevendo a mesma em um formato mais adequado as proposta de texto argumentativo aos moldes do Enem.
Retorne um formato json seguindo camelCase no nome das propriedades, sem acento e com o nome das propriedades em inglês mas o conteúdo em pt-br,
seguindo o seguinte formato, deverá ser retornado um objeto json para introdução, desenvolvimento, conclusão.

{
    "refinedEssay": [
        {
            "paragraphType": "introduction",
            "originalText": "original text",
            "refinedText": "revised text"
        }
    ]
}

Legenda:
paragraphType: tipo do parágrafo, se é introdução (introduction), desenvolvimento (development) ou conclusão (conclusion)
originalText: trecho original do texto, antes da correção
refinedText: trecho corrigido e melhorado conforme as diretrizes do enem
Aplique para o texto a seguir:
"""