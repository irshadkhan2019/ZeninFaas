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
            check_or_create_namespace(function,request)

            return redirect('function_registry:function_list')
    else:
        form = FunctionForm(request.user)
    return render(request, 'function_registry/register_function.html', {'form': form})

@login_required(login_url='authentication:login')
def function_list(request):
    functions = Function.objects.filter(user=request.user)
    return render(request, 'function_registry/function_list.html', {'functions': functions})

@login_required(login_url='authentication:login')
def check_or_create_namespace(function,request):
    user_namespace = request.user.username.lower()
    function_name = function.name.replace(' ', '-').lower()
   
    config.load_kube_config()

    # Create Kubernetes API client
    api_core = client.CoreV1Api()
    api_instance = client.AppsV1Api()

    # check namespace
     # Check if the user's namespace exists
    try:
        api_core.read_namespace(name=user_namespace)
    except ApiException as e:
        if e.status == 404:
            # Create the user's namespace
            namespace_manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": user_namespace
                }
            }
            api_core.create_namespace(body=namespace_manifest)
    

    api_instance.create_namespaced_deployment(namespace=user_namespace, body=deployment_manifest)
    print("Deployment created successfully")

@login_required(login_url='authentication:login')
def zenin_faas(request):
    # functions = Function.objects.filter(user=request.user)
    return render(request, 'function_registry/zenin_faas.html')    