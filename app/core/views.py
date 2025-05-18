from django.shortcuts import render
from core.models import Goal
from django.views.generic import ListView

# Create your views here.


class GoalListView(ListView):
    """simple view to displaying the Goal"""
    model = Goal
    context_object_name = 'goals'
    ordering = ['-created_at']

