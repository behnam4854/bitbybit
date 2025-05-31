from datetime import timezone

from django.db import models
from django.conf import settings

# Create your models here.

# todo which user created this task group
class TaskGroup(models.Model):
    """for grouping the task, for example the work and personal stuff"""
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class Goal(models.Model):
    """for every micro-goal in this app"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    snoozed_times = models.IntegerField(default=0)

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.now().date()

    def __str__(self):
        """string representation for the model"""
        return self.title


class UserReminder(models.Model):
    """reminder model for all the undone task for today"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reminder_time = models.TimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.reminder_time}"


class UserProfile(models.Model):
    """simple user profile"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.IntegerField(max_length=11)

    def __str__(self):
        return f"{self.user.username} - {self.mobile}"
