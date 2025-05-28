from django.forms import ModelForm, DateInput, TextInput, Textarea, TimeInput, Select
from .models import Goal, UserReminder


class GoalForm(ModelForm):
    """for creating a goal"""

    class Meta:
        model = Goal
        fields = ['title', "goal_group", 'description', 'due_date']
        widgets = {
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
            })
        }

class ReminderForm(ModelForm):
    """for creating a reminder"""
    class Meta:
        model = UserReminder
        fields = ['reminder_time', 'active']
        widgets = {
            'reminder_time': TimeInput(attrs={'type': 'time'}),
        }