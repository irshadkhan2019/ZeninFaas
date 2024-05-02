from django.shortcuts import render,redirect
from .forms import TriggerForm
from .models import Trigger
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
@login_required(login_url='authentication:login')
def register_trigger(request):
    if request.method == 'POST':
        form = TriggerForm(request.user,request.POST)
        if form.is_valid(): 
            trigger = form.save(commit=False)
            trigger.user = request.user
            trigger.save()
            return redirect('trigger_registry:trigger_list')
    else:
        form = TriggerForm(request.user)
    return render(request, 'trigger_registry/register_trigger.html', {'form': form})

@login_required(login_url='authentication:login')
def trigger_list(request):
    triggers = Trigger.objects.filter(user=request.user)
    return render(request, 'trigger_registry/trigger_list.html', {'triggers': triggers})