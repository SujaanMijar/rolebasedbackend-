from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserRole
from .serializers import UserSerializer

class SocialLoginAPIView(APIView):
    """
    React sends:
    {
        "username": "john",
        "email": "john@example.com",
        "role": "user"  # optional
    }
    """
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        role = request.data.get('role', 'user')

        if not username or not email:
            return Response({"error": "Username and email required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get User
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})

        # Create or update role
        userrole, _ = UserRole.objects.get_or_create(user=user, defaults={'role': role})
        if userrole.role != role:
            userrole.role = role
            userrole.save()

        # Generate JWT
        refresh = RefreshToken.for_user(user)

        # Serialize
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
