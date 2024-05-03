from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from trigger_registry.models import Trigger
from kubernetes import client, config
from kubernetes.client import configuration
from kubernetes.stream import stream,portforward 
from django.contrib.auth.decorators import login_required   
import time      
import os
from kubernetes.client import AppsV1Api
import threading
from datetime import datetime
from django.utils.timesince import timesince   
from django.contrib import messages                          
configuration.assert_hostname = False


@login_required(login_url='authentication:login')
def dispatch_test_trigger(request, trigger_id):
    trigger = get_object_or_404(Trigger, pk=trigger_id)
    if request.method == 'POST':
        code = request.POST.get('code', '')  
        parameters_str = request.POST.get('parameters', '')  
        start_time = time.time()

        try:
            config.load_kube_config()  # Load Kubernetes config
            api = client.CoreV1Api()   # Create Kubernetes API client

            pods = api.list_namespaced_pod(namespace=request.user.username.lower(), label_selector=f"function_id={trigger.function.pk}")
            pod_name = pods.items[0].metadata.name 
            pod_ip = pods.items[0].status.pod_ip
            
            # dispatch code
            exec_command = [
                    '/bin/bash',
                    '-c',
                    f"echo '{code}' > /home/file.py" 
                ]

                # Execute the command in the pod
            resp = stream(api.connect_get_namespaced_pod_exec, pod_name, request.user.username.lower(),
                                command=exec_command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)
            
            # test code
            # Split the parameters string by comma to get individual parameters
            parameters_list = parameters_str.split(',')
            command = f"python3 /home/file.py {' '.join(parameters_list)}"
            # print(command)

            command = ["/bin/bash", "-c",command]

          
            resp = stream(api.connect_get_namespaced_pod_exec, pod_name, request.user.username.lower(),
                                command=command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)

            end_time = time.time()
            request_time=end_time-start_time
            response_data = {'status': 'success', 'message': 'Code deployed successfully','response':resp,'request_time':request_time}
        except Exception as e:
            response_data = {'status': 'error', 'message': str(e)}

        # response_data = {'status': 'success', 'message': 'Code test ran successfully','response':resp}
        return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,'response_data': response_data,'pod_name':pod_name,'pod_ip':pod_ip})
    else:
        # Render the template with the trigger details
       return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,'pod_name':pod_name,'pod_ip':pod_ip})


@login_required(login_url='authentication:login')
def code_detail(request, trigger_id):
    trigger = get_object_or_404(Trigger, pk=trigger_id)
    language=trigger.function.language

    try:
        config.load_kube_config()  # Load Kubernetes config
        api = client.CoreV1Api()   # Create Kubernetes API client

        pods = api.list_namespaced_pod(namespace=request.user.username.lower(), label_selector=f"function_id={trigger.function.pk}")
        # print(pods)
        # pod_names = [pod.metadata.name for pod in pods.items]
        if pods.items:
            pod = pods.items[0]

            # Extract pod details
            pod_name = pod.metadata.name
            pod_ip = pod.status.pod_ip
            print(pod.status)

    except Exception as e:
            response_data = {'status': 'error', 'message': str(e)}   
    if language=="python":
     return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,'pod_name':pod_name,'pod_ip':pod_ip})
    else:
     return render(request, 'trigger_dispatch/code_detail_node.html', {'trigger': trigger,'pod_name':pod_name,'pod_ip':pod_ip})   

@login_required(login_url='authentication:login')
def install_dependencies(request, trigger_id):
    trigger = get_object_or_404(Trigger, pk=trigger_id)
    if request.method == 'POST':
        commands = request.POST.get('dependency', '')  
        print(commands)
        # Your code to deploy code to function goes here
        try:
            config.load_kube_config()  # Load Kubernetes config
            api = client.CoreV1Api()   # Create Kubernetes API client

            pods = api.list_namespaced_pod(namespace=request.user.username.lower(), label_selector=f"function_id={trigger.function.pk}")
            pod_name = pods.items[0].metadata.name 
            pod_ip = pods.items[0].status.pod_ip
            
            #  write the code to a file inside the pod
            exec_command = [
                    '/bin/bash',
                    '-c',
                    f"{commands}" 
                ]

                # Execute the command in the pod
            resp = stream(api.connect_get_namespaced_pod_exec, pod_name, request.user.username.lower(),
                                command=exec_command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)
               # Get logs from the pod
        

            response_data = {'status': 'success', 'message': 'Packages are getting Installed','resp':resp}
        except Exception as e:
            response_data = {'status': 'error', 'message': str(e)}

        return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,'response_data': response_data,'pod_name':pod_name,'pod_ip':pod_ip})
    else:
        # Render the template with the trigger details
      return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,'pod_name':pod_name,'pod_ip':pod_ip})
    

@login_required(login_url='authentication:login')
def delete_trigger(request, trigger_id):
    trigger = get_object_or_404(Trigger, pk=trigger_id)

    try:
        config.load_kube_config()  # Load Kubernetes config
        api = client.CoreV1Api()   # Create Kubernetes API client
        api_apps = AppsV1Api()  # Create Kubernetes AppsV1 API client

        pods = api.list_namespaced_pod(namespace=request.user.username.lower(), label_selector=f"function_id={trigger.function.pk}")
        if pods.items:
            pod = pods.items[0]

            # Extract pod details
            pod_name = pod.metadata.name
            pod_ip = pod.status.pod_ip
         

            deployment_name = f"{trigger.function.name.replace(' ', '-').lower()}"
            service_name = f"{trigger.function.name.replace(' ', '-').lower()}-service"
            print(deployment_name,service_name)
            # Delete the Deployment
            api_apps.delete_namespaced_deployment(name=deployment_name, namespace=request.user.username.lower())

            # Delete the Service
            api.delete_namespaced_service(name=service_name, namespace=request.user.username.lower())
                # delete its storage 
            trigger.delete_with_function();
            messages.success(request, "Trigger deleted and Resources Released Successfully! ")
            return redirect('trigger_registry:trigger_list')
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return render(request, 'trigger_dispatch/code_detail.html', {'response_data': response_data})
    

