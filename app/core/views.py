from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import GoalForm, ReminderForm
from .models import Goal, UserReminder
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .forms import GoalForm
from django.urls import reverse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.


class GoalListView(ListView):
    """simple view to displaying the Goal"""
    model = Goal
    context_object_name = 'goals'
    ordering = ['created_at']
    form_class = GoalForm
    template_name = 'core/goal_list.html'

    def get_context_data(self, **kwargs):
        context = super(GoalListView, self).get_context_data(**kwargs)
        context['form'] = GoalForm()
        today = timezone.now().date()

        date_sequence = [today + timedelta(days=i) for i in range(-3, 4)]
        selected_date = self.request.GET.get('date', today.isoformat())

        context.update({
            'date_sequence': date_sequence,
            'selected_date': datetime.strptime(selected_date, '%Y-%m-%d').date(),
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('created_at', 'is_completed')
        selected_date = self.request.GET.get('date')

        if selected_date:
            return queryset.filter(due_date=selected_date)
        return queryset

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


# @require_POST
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    goal.delete()
    return redirect('core:goal-list')

# todo messege functionalty
@require_POST
def snooze_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    days = int(request.POST.get('days', 1))

    new_date = timezone.now().date() + timezone.timedelta(days=days)
    goal.due_date = new_date
    goal.save()

    return redirect('core:goal-list')


@login_required
def reminder_settings(request):
    """for setting up the reminder or setting of the reminder"""
    instance, created = UserReminder.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ReminderForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('core:reminder-settings')
    else:
        form = ReminderForm(instance=instance)
    return render(request, 'core/reminder_settings.html', {'form': form})