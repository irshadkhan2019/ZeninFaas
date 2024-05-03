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
            deploy_function_to_kubernetes(function,request)

            return redirect('function_registry:function_list')
    else:
        form = FunctionForm(request.user)
    return render(request, 'function_registry/register_function.html', {'form': form})

@login_required(login_url='authentication:login')
def function_list(request):
    functions = Function.objects.filter(user=request.user)
    return render(request, 'function_registry/function_list.html', {'functions': functions})

@login_required(login_url='authentication:login')
def deploy_function_to_kubernetes(function,request):
    user_namespace = request.user.username.lower()
    function_name = function.name.replace(' ', '-').lower()

    print(user_namespace,function_name)
    imageName=""
    if function.language.lower() == "python":
        imageName='python:latest'
    else:
        imageName='node:latest'    
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


    service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{function_name}-service"
            },
            "spec": {
                "selector": {
                    "app": function_name
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 8080,
                        "targetPort": 8080
                    }
                ],
                "type": "ClusterIP"
            }
        }
    api_core.create_namespaced_service(namespace=user_namespace, body=service_manifest)

    deployment_manifest = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": str(function_name),
    },
    "spec": {
        "selector": {
            "matchLabels": {
                "app": str(function_name),
                "function_id": str(function.id)
            }
        },
        "replicas": 1,
        "template": {
            "metadata": {
                "labels": {
                    "app": str(function_name),
                    "function_id": str(function.id)
                }
            },
            "spec": {
                "containers": [
                    {
                        "name": str(function_name),
                        "image": str(imageName),
                        "ports": [
                            {
                                "containerPort": 8080,
                            }
                        ],
                        "command": [ "/bin/bash", "-c" ],
                        "args": [ f"while true; do sleep 30; done;" ],
                     
                    }
                ]
            }
        }
    }
}

    api_instance.create_namespaced_deployment(namespace=user_namespace, body=deployment_manifest)
    print("Deployment created successfully")

@login_required(login_url='authentication:login')
def zenin_faas(request):
    # functions = Function.objects.filter(user=request.user)
    return render(request, 'function_registry/zenin_faas.html')    