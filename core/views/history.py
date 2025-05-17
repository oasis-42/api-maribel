from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..models import RefinedEssayText, OriginalEssayText
from ..serializers import RefinedEssayTextSerializer, OriginalEssayTextSerializer


class RefinedEssayTextView(generics.RetrieveAPIView):
    queryset = RefinedEssayText.objects.all()
    serializer_class = RefinedEssayTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return RefinedEssayText.objects.filter(original_essay__feedback__user=user)


class OriginalEssayTextView(generics.RetrieveAPIView):
    queryset = OriginalEssayText.objects.all()
    serializer_class = OriginalEssayTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OriginalEssayText.objects.filter(feedback__user=user)