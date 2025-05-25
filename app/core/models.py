from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class TaskGroup(models.Model):
    """for grouping the task, for example the work and personal stuff"""
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class Goal(models.Model):
    """for every micro-goal in this app"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        """string representation for the model"""
        return self.title


class UserReminder(models.Model):
    """reminder model for all the undone task for today"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reminder_time = models.TimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.reminder_time}"

