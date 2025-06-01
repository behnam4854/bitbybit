from core.models import *


def create_default_groups_for_user(user):
    """for creating default groups for a user"""
    default_groups = DefaultGoalGroup.objects.all()
    for group in default_groups:
        TaskGroup.objects.create(
            user=user,
            title=group.title
        )
