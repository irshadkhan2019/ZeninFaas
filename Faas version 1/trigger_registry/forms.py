from django import forms
from .models import Trigger
from function_registry.models import Function

class TriggerForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TriggerForm, self).__init__(*args, **kwargs)
        self.fields['function'].queryset = Function.objects.filter(user=user)
        
    class Meta:
        model = Trigger
        fields = ['name', 'function']  