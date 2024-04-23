from django.shortcuts import render, redirect
from .models import Function
from .forms import FunctionForm
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from django.contrib.auth.decorators import login_required

@login_required(login_url='authentication:login')
def register_function(request):
    if request.method == 'POST':
        form = FunctionForm(request.user,request.POST)
        if form.is_valid():
            function = form.save(commit=False)
            function.user = request.user
            function.save()
            return redirect('function_registry:function_list')
    else:
        form = FunctionForm(request.user)
    return render(request, 'function_registry/register_function.html', {'form': form})

@login_required(login_url='authentication:login')
def function_list(request):
    functions = Function.objects.filter(user=request.user)
    return render(request, 'function_registry/function_list.html', {'functions': functions})


@login_required(login_url='authentication:login')
def zenin_faas(request):
    # functions = Function.objects.filter(user=request.user)
    return render(request, 'function_registry/zenin_faas.html')    