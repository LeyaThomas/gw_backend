from django.db import models
from django.conf import settings  # Import settings to use AUTH_USER_MODEL
from django.utils import timezone

# Blog Model (Blog posts created by users)
class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'author'})  # Author is a CustomUser with 'author' role
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def increment_views(self, user):
        """Increment the view count for this blog only once per user."""
        # Check if the user has already viewed this blog
        if not Read.objects.filter(user=user, blog=self).exists():
            # If the user hasn't viewed the blog yet, increment the views count
            self.views += 1
            self.save()

            # Track that the user has read this blog
            Read.objects.create(user=user, blog=self)


# Read Model (Tracks which blogs a user has read)
class Read(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use CustomUser model
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')  # A user can only read a blog once

    def __str__(self):
        return f'{self.user.username} read {self.blog.title} on {self.read_at}'


# Streak Model (Tracks reading streaks for a user)
class Streak(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use CustomUser model
    streak_count = models.PositiveIntegerField(default=0)
    last_read_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - Streak: {self.streak_count} days'

    def update_streak(self):
        """Update the user's reading streak."""
        last_read = Read.objects.filter(user=self.user).order_by('-read_at').first()
        today = timezone.now().date()

        if last_read and last_read.read_at.date() == today:
            if self.last_read_date == today:
                pass  # Already counted for today
            else:
                self.streak_count += 1
                self.last_read_date = today
        else:
            self.streak_count = 0  # Reset streak if no read blogs today

        self.save()
