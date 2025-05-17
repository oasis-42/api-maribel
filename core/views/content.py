from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..models import Theme, MotivationalText
from ..serializers import ThemeSerializer, MotivationalTextSerializer


class ThemeView(generics.ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]


class MotivationalTextByThemeView(generics.ListAPIView):
    serializer_class = MotivationalTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        theme_id = self.kwargs['theme_id']
        return MotivationalText.objects.filter(theme_id=theme_id)