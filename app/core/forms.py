from django.forms import ModelForm, DateInput, TextInput, Textarea
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
            'description': Textarea(attrs={
                'type': 'text',
                'autocomplete': 'off',
                'rows': 3,
            })
        }
