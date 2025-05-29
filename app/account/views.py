from datetime import datetime

from django.shortcuts import render
from core.models import *


# Create your views here.
def dashboard(request):
    """simple test dashboard"""

    goal_groups = []
    # groups = TaskGroup.objects.filter(user=request.user)
    # todo refactor the code to the currect one that filter user after editing the model
    groups = TaskGroup.objects.all()

    for group in groups:
        total_goals = group.goal_set.count()
        completed_goals = group.goal_set.filter(is_completed=True).count()

        goal_groups.append({
            'title': group.title,
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'completion_percentage': (completed_goals / total_goals * 100) if total_goals > 0 else 0
        })

    total_tasks = Goal.objects.filter(user=request.user).count()
    completed_tasks = Goal.objects.filter(is_completed=True, user=request.user).count()
    in_progress_tasks = Goal.objects.filter(is_completed=False, user=request.user, due_date__lte=datetime.now()).count()
    over_due_tasks = Goal.objects.filter(is_completed=False, user=request.user, due_date__gte=datetime.now()).count()
    return render(request, "account/home_dashboard.html", {"completed_tasks": completed_tasks,
                                                           "total_tasks": total_tasks,
                                                           "in_progress_tasks": in_progress_tasks,
                                                           "over_due_tasks": over_due_tasks,
                                                           "goal_groups": goal_groups})


def login(request):
    """simple test dashboard"""
    return render(request, "account/login.html")


def profile(request):
    """simple test dashboard"""
    return render(request, "account/profile.html")


def goals(request):
    """simple test dashboard"""
    return render(request, "account/goals.html")


def goal_groups(request):
    """simple test dashboard"""
    return render(request, "account/goal_groups.html")


def verification(request):
    """simple test dashboard"""
    return render(request, "account/verification_code.html")