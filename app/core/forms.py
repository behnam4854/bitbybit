from django.forms import ModelForm, DateInput, TextInput, Textarea, TimeInput, Select, NumberInput, BooleanField
from .models import Goal, UserReminder, TaskGroup
import logging
from django import forms

logger = logging.getLogger(__name__)


class GoalForm(ModelForm):
    """Form for creating a goal"""

    class Meta:
        model = Goal
        fields = ['title', 'goal_group', 'description', 'due_date', 'target_value', 'is_recurring', 'recurrence']
        widgets = {
            'target_value': NumberInput(attrs={
                'min': '0',
                'step': '1',
                'class': 'form-control',
            }),
            'due_date': DateInput(attrs={
                'type': 'date',
                'autocomplete': 'off',
                'class': 'form-control',
            }),
            'description': Textarea(attrs={
                'type': 'text',
                'autocomplete': 'off',
                'rows': 3,
                'class': 'form-control',
                'placeholder': "Enter goal description",
            }),
            'title': TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Enter goal title",
            }),
            'goal_group': Select(attrs={
                'class': 'form-control',
                'placeholder': "Please select",
            }),
            'recurrence': Select(attrs={
                'class': 'form-control',
                'placeholder': "Please select",
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Remove user from kwargs
        logger.debug(f"Initializing GoalForm with user: {user}")
        super().__init__(*args, **kwargs)
        if user:
            self.fields['goal_group'].queryset = TaskGroup.objects.filter(user=user)
            logger.debug(f"GoalForm queryset for user {user}: {self.fields['goal_group'].queryset}")
        else:
            logger.warning("No user provided to GoalForm")
            self.fields['goal_group'].queryset = TaskGroup.objects.none()  # Empty queryset if no user


class ReminderForm(ModelForm):
    """for creating a reminder"""

    class Meta:
        model = UserReminder
        fields = ['reminder_time', 'active']
        widgets = {
            'reminder_time': TimeInput(attrs={'type': 'time'}),
        }
