# function_registration/forms.py
from django import forms
from .models import Function

class FunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        fields = ['name','language','memory_limit','cpu_limit',]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['memory_limit'].widget = forms.Select(choices=self.get_memory_limit_choices())
        self.fields['cpu_limit'].widget = forms.Select(choices=self.get_cpu_limit_choices())

    def get_memory_limit_choices(self):
        return [(128, '128 MB'), (256, '256 MB'), (512, '512 MB'), (1024, '1 GB')]

    def get_cpu_limit_choices(self):
        return [(5000, '5000 CPU units'), (10000, '10000 CPU units'), (20000, '20000 CPU units')]    
