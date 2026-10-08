from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
            return Response({'mensaje': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)
        return Response({'error': 'No hay sesión activa'}, status=status.HTTP_400_BAD_REQUEST)
