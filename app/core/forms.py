from django.forms import ModelForm, DateInput
from .models import Goal


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
        }
