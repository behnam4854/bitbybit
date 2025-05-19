from django.shortcuts import render
from .models import Goal
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


# Create your views here.


class GoalListView(ListView):
    """simple view to displaying the Goal"""
    model = Goal
    context_object_name = 'goals'
    ordering = ['-created_at']


def toggle_goal_status(request, goal_id):
    """for toggling the status of the goal if existed"""
    if request.method == "POST":
        goal = get_object_or_404(Goal, pk=goal_id)
        goal.is_completed = not goal.is_completed
        goal.save()

        return JsonResponse({
            "success": True,
            "is_completed": goal.is_completed
        })
    return JsonResponse({
        "success": False,
    },
        status=400)
