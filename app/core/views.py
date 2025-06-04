from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import GoalForm, ReminderForm
from .models import Goal, UserReminder, GoalInstance
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .forms import GoalForm
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)



class GoalListView(ListView):
    """Simple view to display Goals"""
    model = Goal
    context_object_name = 'goals'
    ordering = ['-created_at', 'is_completed']
    form_class = GoalForm
    template_name = 'account/goals.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter goals by logged-in user
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        else:
            queryset = queryset.none()  # No goals for unauthenticated users
        selected_date = self.request.GET.get('date')

        if selected_date:
            try:
                parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__gte=parsed_date)
            except ValueError:
                pass
        logger.debug(f"Goal queryset for user {self.request.user}: {queryset}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Generate date sequence
        date_sequence = [today + timedelta(days=i) for i in range(-3, 4)]

        # Handle date parsing safely
        try:
            selected_date = datetime.strptime(
                self.request.GET.get('date', today.isoformat()),
                '%Y-%m-%d'
            ).date()
        except ValueError:
            selected_date = today

        # Pass user to form
        form = self.form_class(user=self.request.user) if self.request.user.is_authenticated else self.form_class()
        context.update({
            'form': form,
            'date_sequence': date_sequence,
            'selected_date': selected_date,
            'today': today
        })
        logger.debug(f"Context for user {self.request.user}: form with goal_group queryset {form.fields['goal_group'].queryset}")
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(user=request.user, data=request.POST) if request.user.is_authenticated else self.form_class(data=request.POST)
        logger.debug(f"Form data: {form.data}")
        if form.is_valid():
            goal = form.save(commit=False)
            if request.user.is_authenticated:
                goal.user = request.user
                goal.save()
                logger.debug(f"Created goal: {goal.title} for user: {request.user}")
                messages.success(request, "Goal created successfully!")
                if goal.is_recurring:
                    GoalInstance.objects.create(goal=goal)
                    messages.success(request, "Goal Instance created successfully!")
                return redirect(self.request.path)
            else:
                logger.warning("Unauthenticated user attempted to create goal")
                messages.error(request, "You must be logged in to create goals")
                return redirect('login')

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['form'] = form

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.title()}: {error}")
        return self.render_to_response(context)


@csrf_exempt
@login_required
def update_progress(request, goal_id):
    if request.method == 'POST':
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        data = json.loads(request.body)
        current_value = float(data.get('current_value', 0))
        goal.current_value = current_value
        if goal.current_value >= goal.target_value:
            goal.is_completed = True
            goal.current_value = goal.target_value
            goal.save()
            return JsonResponse({
                'success': True,
                'progress': goal.progress,
                'current_value': goal.current_value,
                'target_value': goal.target_value,
                'is_completed': goal.is_completed
            })
        goal.save()
        return JsonResponse({'success': True, 'progress': goal.progress,
                             'current_value': current_value,
                             'target_value': goal.target_value})
    return JsonResponse({'success': False}, status=400)


def toggle_goal_status(request, goal_id):
    """for toggling the status of the goal if existed"""
    if request.method == "POST":
        goal = get_object_or_404(Goal, pk=goal_id)
        if goal.target_value and goal.current_value < goal.target_value:
            return JsonResponse({'success': False})
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
    if goal.is_completed:
        return redirect('core:goal-list')
    days = int(request.POST.get('days', 1))

    new_date = goal.due_date + timezone.timedelta(days=days)
    goal.due_date = new_date
    goal.snoozed_times += 1
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
            return redirect('account:dashboard')
    else:
        form = ReminderForm(instance=instance)
    return render(request, 'core/reminder_settings.html', {'form': form})
