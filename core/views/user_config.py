from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..models import UserConfig
from ..serializers import UserConfigSerializer


class UserConfigView(generics.RetrieveUpdateAPIView):
    queryset = UserConfig.objects.all()
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserConfig.objects.filter(user=user)
