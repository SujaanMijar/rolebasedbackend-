import os
import requests
from dotenv import load_dotenv
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserRole
from .serializers import UserSerializer

load_dotenv()

def get_or_create_user(username, email, role='user'):
    user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    userrole, _ = UserRole.objects.get_or_create(user=user, defaults={'role': role})
    return user

def generate_jwt(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}

# ---------------- TikTok ----------------
class TikTokLoginCallback(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_url = "https://open-api.tiktok.com/oauth/access_token/"
        data = {
            "client_key": os.getenv("TIKTOK_CLIENT_KEY"),
            "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code"
        }
        token_resp = requests.post(token_url, data=data).json()
        access_token = token_resp.get('data', {}).get('access_token')
        open_id = token_resp.get('data', {}).get('open_id')
        if not access_token:
            return Response({"error": "Failed to get TikTok access token"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_info_url = f"https://open-api.tiktok.com/oauth/userinfo/?access_token={access_token}&open_id={open_id}"
        user_info = requests.get(user_info_url).json().get('data', {})
        username = user_info.get('display_name') or f"tiktok_{open_id}"
        email = user_info.get('email') or f"{username}@tiktok.com"

        user = get_or_create_user(username, email)
        tokens = generate_jwt(user)
        serializer = UserSerializer(user)
        return Response({'user': serializer.data, **tokens})

# ---------------- Facebook ----------------
class FacebookLoginCallback(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_url = "https://graph.facebook.com/v17.0/oauth/access_token"
        params = {
            "client_id": os.getenv("FB_APP_ID"),
            "client_secret": os.getenv("FB_APP_SECRET"),
            "redirect_uri": os.getenv("FB_REDIRECT_URI"),
            "code": code
        }
        token_resp = requests.get(token_url, params=params).json()
        access_token = token_resp.get("access_token")
        if not access_token:
            return Response({"error": "Failed to get Facebook access token"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = "https://graph.facebook.com/me"
        user_info = requests.get(user_info_url, params={"access_token": access_token, "fields": "id,name,email"}).json()
        username = user_info.get('name')
        email = user_info.get('email') or f"{username}@facebook.com"

        user = get_or_create_user(username, email)
        tokens = generate_jwt(user)
        serializer = UserSerializer(user)
        return Response({'user': serializer.data, **tokens})

# ---------------- Instagram ----------------
class InstagramLoginCallback(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_url = "https://api.instagram.com/oauth/access_token"
        data = {
            "client_id": os.getenv("IG_APP_ID"),
            "client_secret": os.getenv("IG_APP_SECRET"),
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("IG_REDIRECT_URI"),
            "code": code
        }
        token_resp = requests.post(token_url, data=data).json()
        access_token = token_resp.get("access_token")
        user_id = token_resp.get("user_id")
        if not access_token:
            return Response({"error": "Failed to get Instagram access token"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = f"https://graph.instagram.com/{user_id}?fields=id,username"
        user_info = requests.get(user_info_url, params={"access_token": access_token}).json()
        username = user_info.get('username')
        email = f"{username}@instagram.com"

        user = get_or_create_user(username, email)
        tokens = generate_jwt(user)
        serializer = UserSerializer(user)
        return Response({'user': serializer.data, **tokens})
