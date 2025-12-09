from django.urls import path
from .views import TikTokLoginCallback, FacebookLoginCallback, InstagramLoginCallback

urlpatterns = [
    path('social/tiktok/callback/', TikTokLoginCallback.as_view(), name='tiktok-callback'),
    path('social/facebook/callback/', FacebookLoginCallback.as_view(), name='facebook-callback'),
    path('social/instagram/callback/', InstagramLoginCallback.as_view(), name='instagram-callback'),
]
