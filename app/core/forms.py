from django.forms import ModelForm, DateInput, TextInput, Textarea, TimeInput
from .models import Goal, UserReminder


class GoalForm(ModelForm):
    """for creating a goal"""

    class Meta:
        model = Goal
        fields = '__all__'
        widgets = {
            'due_date': DateInput(attrs={
                'type': 'date',
                'autocomplete': 'off',
                'readonly': 'readonly',
            }),
            'description': Textarea(attrs={
                'type': 'text',
                'autocomplete': 'off',
                'rows': 3,
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