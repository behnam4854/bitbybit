from datetime import timezone

from django.db import models
from django.conf import settings


class DefaultGoalGroup(models.Model):
    """common groups that should be add after the user have been verified"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TaskGroup(models.Model):
    """for grouping the goal, for example the work and personal stuff"""
    title = models.CharField(max_length=256)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class Goal(models.Model):
    """for every micro-goal in this app"""
    RECURRENCE_CHOICES = [
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    snoozed_times = models.IntegerField(default=0)
    target_value = models.FloatField(blank=True, null=True)
    current_value = models.FloatField(default=0)
    priority = models.IntegerField(default=1)
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='NONE')

    @property
    def progress(self):
        if self.target_value and self.target_value > 0:
            return min((self.current_value / self.target_value * 100), 100)
        return 0.0

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.now().date()

    def __str__(self):
        """string representation for the model"""
        return f"{self.title} - {self.user.email}"


class UserReminder(models.Model):
    """reminder model for all the undone task for today"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reminder_time = models.TimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.reminder_time}"


class UserProfile(models.Model):
    """simple user profile"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.mobile}"
