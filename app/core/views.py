from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import GoalForm, ReminderForm
from .models import Goal, UserReminder
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .forms import GoalForm
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages


# Create your views here.


class GoalListView(ListView):
    """simple view to displaying the Goal"""
    model = Goal
    context_object_name = 'goals'
    ordering = ['-created_at', 'is_completed']
    form_class = GoalForm
    template_name = 'account/goals.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_date = self.request.GET.get('date')

        if selected_date:
            try:
                parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                return queryset.filter(due_date__gte=parsed_date)
            except ValueError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        # First call the base implementation to get the context
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

        context.update({
            'form': self.form_class(),
            'date_sequence': date_sequence,
            'selected_date': selected_date,
            'today': today
        })
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        print(form.data)
        if form.is_valid():
            # Create but don't save yet
            goal = form.save(commit=False)
            # Associate with logged-in user
            if request.user.is_authenticated:
                goal.user = request.user
                goal.save()
                messages.success(request, "Goal created successfully!")
                return redirect(self.request.path)
            else:
                print("3")
                messages.error(request, "You must be logged in to create goals")
                return redirect('login')

        # Handle invalid form
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['form'] = form

        # Add form errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.title()}: {error}")

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
