from django.urls import path
from .views import SocialLoginAPIView

urlpatterns = [
    path('login/', SocialLoginAPIView.as_view(), name='login'),
]
