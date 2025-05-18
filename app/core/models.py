from django.db import models


# Create your models here.


class Goal(models.Model):
    """for every micro-goal in this app"""
    title = models.CharField(max_length=256)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        """string representation for the model"""
        return self.title
