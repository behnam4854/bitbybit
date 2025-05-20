from django.shortcuts import render

from .forms import GoalForm
from .models import Goal
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .forms import GoalForm
from django.urls import reverse


# Create your views here.


class GoalListView(ListView):
    """simple view to displaying the Goal"""
    model = Goal
    context_object_name = 'goals'
    ordering = ['created_at']
    form_class = GoalForm
    template_name = 'core/goal_list.html'

    def get_queryset(self):
        return super().get_queryset().order_by('created_at', 'is_completed')

    def get_context_data(self, **kwargs):
        context = super(GoalListView, self).get_context_data(**kwargs)
        context['form'] = GoalForm()
        return context

    def post(self, request, *args, **kwargs):
        form = GoalForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.request.path)

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


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
