from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .models import Blog, Read, Streak
from .serializers import BlogSerializer, ReadSerializer, StreakSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone

# Get CustomUser model
User = get_user_model()

# 🔹 Blog ViewSet (Create, Read, Update, Delete for Authors)
class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       """Return all blogs, irrespective of the user."""
       return Blog.objects.all().order_by('-created_at')  # Fetch all blogs in descending order


    def perform_create(self, serializer):
        """Ensure only authors can create blogs."""
        user = self.request.user
        if user.role != 'author':
            raise PermissionDenied("Only authors can create blogs.")
        serializer.save(author=user)

    def perform_update(self, serializer):
        """Ensure authors can only edit their own blogs."""
        blog = self.get_object()
        if blog.author != self.request.user:
            raise PermissionDenied("You can only edit your own blogs.")
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure authors can only delete their own blogs."""
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own blogs.")
        instance.delete()

# 🔹 Read ViewSet (Tracking Read Blogs)
class ReadViewSet(viewsets.ModelViewSet):
    serializer_class = ReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own read blogs."""
        return Read.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure a user can only mark a blog as read once, and increment views only once per user."""
        user = self.request.user
        blog = serializer.validated_data['blog']

        # Ensure the user hasn't read this blog before
        if Read.objects.filter(user=user, blog=blog).exists():
            raise PermissionDenied("You have already read this blog.")

        # Increment the blog view count once per user
        blog.increment_views()

        # Save the read record
        serializer.save(user=user)

# 🔹 Streak View (Tracks User Reading Streaks)
class StreakView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        streak, created = Streak.objects.get_or_create(user=user)

        # Update streak count based on today's reading
        streak.update_streak()  # Using the method in Streak model to update

        # Return streak information
        serializer = StreakSerializer(streak)
        return Response(serializer.data)
