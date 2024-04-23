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
import random
import matplotlib.pyplot as plt
from django.utils.timesince import timesince   
from django.contrib import messages                          
configuration.assert_hostname = False
from kubernetes.client import AppsV1Api
from kubernetes.client.rest import ApiException
from kubernetes.client import CustomObjectsApi


def get_pods_from_deployment(namespace, deployment_name):
    # Load kubeconfig file or use in-cluster configuration
    config.load_kube_config()

    # Create an instance of the Kubernetes API client
    api_instance = client.CoreV1Api()

    try:
        # Define label selector to match pods belonging to the deployment
        label_selector = f"name={deployment_name}"

        # List pods in the specified namespace with the specified label selector
        api_response = api_instance.list_namespaced_pod(namespace, label_selector=label_selector)

        # Extract and return the pod objects
        return api_response.items
    except Exception as e:
        print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
        return []
    

def select_random_pod(pods):
    running_pods = [pod for pod in pods if pod.status.phase == 'Running']
    if running_pods:
        return random.choice(running_pods)
    else:
        return None

@login_required(login_url='authentication:login')
def dispatch_test_trigger(request, trigger_id,thread_id=None):
    trigger = get_object_or_404(Trigger, pk=trigger_id)
    if request.method == 'POST':
        code = request.POST.get('code', '')  
        parameters_str = request.POST.get('parameters', '')  
        user_namespace = request.user.username.lower()
        start_time = time.time()

        try:
            config.load_kube_config()  # Load Kubernetes config
            api = client.CoreV1Api()   # Create Kubernetes API client
            api_apps = AppsV1Api() 

            pods=get_pods_from_deployment("default","deployment")
            # for pod in pods:
            #     print(pod.metadata.name)
            # Select the pod with the least CPU usage from the first 100 pods
            # pod_with_least_cpu_usage = select_pod_with_least_cpu_usage(pods)
            assigned_pod = select_random_pod(pods)
            # print(assigned_pod.metadata.name)
            selected_pod=assigned_pod.metadata.name
            print("Thread ID:"+str(thread_id)+"got pod"+str(selected_pod))
          
            # dispatch code
            exec_command = [
                '/bin/sh',
                '-c',
                f"mkdir -p /home/{user_namespace} && echo '{code}' > /home/{user_namespace}/file.py" 
            ]


            # Execute the command in the pod
            resp="NULL"
            resp = stream(api.connect_get_namespaced_pod_exec,selected_pod, "default",
                                command=exec_command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)
            

            parameters_list = parameters_str.split(',')
            command = f"python3 /home/{user_namespace}/file.py {' '.join(parameters_list)}"
            # print(command)

            command = ["/bin/sh", "-c",command]

          
            resp = stream(api.connect_get_namespaced_pod_exec, selected_pod, "default",
                                command=command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)

            end_time = time.time()
            request_time=end_time-start_time
                # Write elapsed time to a file
            
            response_data = {'status': 'success', 'message': 'Code deployed successfully','response':resp,'request_time':request_time}
            # print(response_data)
        except Exception as e:
            response_data = {'status': 'error', 'message': str(e)}

        # response_data = {'status': 'success', 'message': 'Code test ran successfully','response':resp}
        return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,'response_data': response_data})
    else:
        # Render the template with the trigger details
       return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger})


@login_required(login_url='authentication:login')
def code_detail(request, trigger_id):
    trigger = get_object_or_404(Trigger, pk=trigger_id)
    language=trigger.function.language

    try:
        config.load_kube_config()  # Load Kubernetes config
        api = client.CoreV1Api()   # Create Kubernetes API client

        
    except Exception as e:
            response_data = {'status': 'error', 'message': str(e)}   
    if language=="python":
     return render(request, 'trigger_dispatch/code_detail.html', {'trigger': trigger,})
    else:
     return render(request, 'trigger_dispatch/code_detail_node.html', {'trigger': trigger,})   
    
#Load testing
def load_test(request,trigger_id,num_requests,thread_id):
    response_times = []
    request.method = 'POST'
    request.POST = {'code': 'print("Hello, world!")', 'parameters': ''}
    for i in range(1, num_requests + 1):
        start_time = time.time()
        response = dispatch_test_trigger(request,trigger_id,thread_id)
        end_time = time.time()
        response_time = end_time - start_time
        response_times.append(response_time)
        # print(f'Request {i}: Response Time: {response_time}')
    return response_times 

def send_req_and_plot(request, trigger_id):
    num_users = 15  # Number of concurrent users
    num_requests_per_user = 40  # Number of requests per user
    max_requests = 100  # Maximum number of requests
    avg_response_times = []
    avg_response_time_with_x_clients=[]

    # Define a function to execute load_test for each user concurrently
    def execute_load_test(trigger_id, num_requests,thread_id):
        response_times = load_test(request, trigger_id, num_requests,thread_id) 
        avg_response_time = sum(response_times) / num_requests  #per thread res time we got
        avg_response_times.append(avg_response_time) # 4 since 4 threads
        # print(f"avg_response_times {avg_response_times}")
        # print(f'Number of Requests: {num_requests}, Average Response Time: {avg_response_time}')


    for users in range(2,num_users,2):
        print(f"Load test for {users} parallel clients")
        threads = []

        # Create and start threads for each user
        for thread_id in range(users):
            t = threading.Thread(target=execute_load_test, args=(trigger_id, num_requests_per_user,thread_id))
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()
        
        avg_response_time_with_x_client= sum(avg_response_times) / users
        avg_response_time_with_x_clients.append(avg_response_time_with_x_client)
    print(avg_response_time_with_x_clients)
    plt.plot([users for users in range(2, num_users + 1, 2)], avg_response_time_with_x_clients)

  
    plt.xlabel('Number of parallel Clients')
    plt.ylabel('Average Response Time (seconds)')
    plt.title('Average Response Time vs x client(20 requests)')
    plt.savefig('response_time_plot.png')  
    plt.clf()
    return redirect('trigger_dispatch:code_detail', trigger_id=trigger_id)



