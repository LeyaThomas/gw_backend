from rest_framework import serializers
from .models import Blog, Read, Streak
from django.contrib.auth import get_user_model
from datetime import date

# Get CustomUser model
User = get_user_model()

# Blog Serializer (Handles Create, Read, Update, Delete)
class BlogSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  # Display author's username

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'views']
        read_only_fields = ['author', 'created_at', 'updated_at', 'views']

    def create(self, validated_data):
        """Ensure the author is automatically assigned from the logged-in user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ensure views are updated only once per user."""
        user = self.context['request'].user
        # Increment views only if the user has not viewed this blog before
        instance.increment_views(user)
        return super().update(instance, validated_data)


class ReadSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Allow user selection
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())  # Allow blog selection

    class Meta:
        model = Read
        fields = ['user', 'blog', 'read_at']


class StreakSerializer(serializers.ModelSerializer):
    last_read_date = serializers.SerializerMethodField()

    class Meta:
        model = Streak
        fields = ["streak_count", "last_read_date"]

    def get_last_read_date(self, obj):
        return obj.last_read_date.strftime("%Y-%m-%d") if obj.last_read_date else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["streak_count"] = data.get("streak_count", 0)  # ✅ Default to 0
        return data
