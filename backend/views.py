from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers import UserSerializer


class GetUserView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
