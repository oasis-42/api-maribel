from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Skill, Theme
from ..serializers import CapturedPictureSerializer, FeedbackDtoSerializer
from ..utils.ai_integrations import (
    analyse_essay_with_gpt,
    process_ocr,
    refine_essay_with_gpt,
)


class TextExtractionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CapturedPictureSerializer

    def post(self, request):
        serializer = CapturedPictureSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        base64_content = serializer.validated_data["base64"]
        try:
            ocr_result = process_ocr(base64_content)
            return Response(ocr_result)
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackDtoSerializer

    def post(self, request):
        serializer = FeedbackDtoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data["text"]
        theme_id = serializer.validated_data["theme_id"]

        try:
            theme = Theme.objects.get(theme_id=theme_id)
            refined_essay_result = refine_essay_with_gpt(text, theme)
            essay_analysis_result = analyse_essay_with_gpt(text, theme)

            for item in essay_analysis_result.get("essayAnalysis", []):
                try:
                    skill = Skill.objects.get(skill_id=item["analyzedSkill"])
                    item["skillDescription"] = skill.skill_description
                except Skill.DoesNotExist:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(
                {
                    "refinedEssay": refined_essay_result.get("refinedEssay"),
                    "essayAnalysis": essay_analysis_result.get("essayAnalysis"),
                },
                status=status.HTTP_200_OK,
            )
        except Theme.DoesNotExist:
            return Response(
                {"error": "Theme not found"}, status=status.HTTP_400_BAD_REQUEST
            )
