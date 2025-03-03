# blogs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSet, ReadViewSet, StreakView

router = DefaultRouter()

# Specify basename for viewsets
router.register(r'blog', BlogViewSet, basename='blog')
router.register(r'reads', ReadViewSet, basename='read')

urlpatterns = [
    path('streak/', StreakView.as_view(), name='streak'),
    path('', include(router.urls)),
]
