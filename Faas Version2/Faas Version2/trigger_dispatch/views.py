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
from kubernetes.client import AppsV1Api
from kubernetes.client.rest import ApiException
import matplotlib.pyplot as plt
import psutil
import uuid



def wait_for_pod_ready(api, pod_name, namespace, timeout_seconds=60):
    start_time = time.time()
    timeout = start_time + timeout_seconds
    time.sleep(2)
    while time.time() < timeout:
        try:
            pods = api.list_namespaced_pod(namespace=namespace, label_selector=f"app={pod_name}")
            pod=pods.items[0]
            print(pod.status.phase)
            if pod.status.phase == "Running":
                print("Pod is running and ready.")
                return True
            else:
                print("Pod is still initializing...")
        except ApiException as e:
            if e.status == 404:
                print("Pod not found. It may still be initializing...")
            else:
                print(f"Error reading pod: {e}")
        time.sleep(1)

    print("Timeout reached while waiting for the pod to be ready.")
    return False


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

             # Create a unique pod name based on the current timestamp
            random_uuid = uuid.uuid4()
            pod_name = f"{trigger.function.name.replace(' ', '-').lower()}-{int(time.time())}-{random_uuid}"
            print("Thread ID:"+str(thread_id)+"got pod"+str(pod_name))
            
            deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": str(pod_name),
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": str(pod_name),
                        }
                    },
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": str(pod_name),
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": str(pod_name),
                                    # "image": str(trigger.function.language),
                                    "image": "python:3.9.0-alpine",
                                    "ports": [
                                        {
                                            "containerPort": 8080,
                                        }
                                    ],
                                    "command": [ "/bin/sh", "-c" ],
                                    "args": [ f"while true; do sleep 30; done;" ],
                                
                                }
                            ]
                        }
                    }
                }
            }

            api_apps.create_namespaced_deployment(namespace=user_namespace, body=deployment_manifest)

            if wait_for_pod_ready(api, pod_name,user_namespace):
                print("Pod is ready.")
            else:
                print("Pod failed to become ready within the specified timeout.")
            # dispatch code
            pods = api.list_namespaced_pod(namespace=user_namespace, label_selector=f"app={pod_name}")
            pod_name_full = pods.items[0].metadata.name 
            exec_command = [
                    '/bin/sh',
                    '-c',
                    f"echo '{code}' > /home/file.py" 
                ]

            #     # Execute the command in the pod
            resp="NULL"
            resp = stream(api.connect_get_namespaced_pod_exec, str(pod_name_full), user_namespace,
                                command=exec_command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)
            

            parameters_list = parameters_str.split(',')
            command = f"python3 /home/file.py {' '.join(parameters_list)}"
            # print(command)

            command = ["/bin/sh", "-c",command]

          
            resp = stream(api.connect_get_namespaced_pod_exec, str(pod_name_full), user_namespace,
                                command=command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False)
            print(resp)

            end_time = time.time()
            request_time=end_time-start_time
            # api.delete_namespaced_pod(name=pod_name, namespace=request.user.username.lower())
            api_apps.delete_namespaced_deployment(name=pod_name_full, namespace=user_namespace)
            response_data = {'status': 'success', 'message': 'Code deployed successfully','response':resp,'request_time':request_time}
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

# Load testing
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
    return response_times 


def get_cpu_utilization():
    return psutil.cpu_percent(interval=1)

def send_req_and_plot(request, trigger_id):
    num_users = 100 # Number of concurrent users
    num_requests_per_user = 1  # Number of requests per user
    avg_response_times = []
    avg_response_time_with_x_clients=[]
    throughput_values=[]
    throughput_with_x_clients=[]
    cpu_utilization_values = []

    # Define a function to execute load_test for each user concurrently
    def execute_load_test(trigger_id, num_requests,thread_id):
        response_times = load_test(request, trigger_id, num_requests,thread_id) 
        avg_response_time = sum(response_times) / num_requests  #per thread res time we got
        avg_response_times.append(avg_response_time) # 4 since 4 threads
        throughput = num_requests / avg_response_time
        throughput_values.append(throughput)

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
        throughput_with_x_client=sum(throughput_values)/users
        throughput_with_x_clients.append(throughput_with_x_client)
        cpu_utilization = get_cpu_utilization()
        cpu_utilization_values.append(cpu_utilization)
        print(throughput_with_x_clients)
        print(avg_response_time_with_x_clients)
        print(cpu_utilization_values)

    print(cpu_utilization_values)
    print(throughput_with_x_clients)
    print(avg_response_time_with_x_clients)
    # Plot the results(response time)
    plt.plot([users for users in range(2, num_users, 2)], avg_response_time_with_x_clients, label='Response Time')
    plt.xlabel('Number of parallel Clients')
    plt.ylabel('Response time')
    plt.title('Average Response Time vs Number of clients')
    # Save the plot to a file
    plt.legend()
    plt.savefig('response_time_plot.png')  
    plt.clf()

    # Plot Througput
    plt.plot([users for users in range(2, num_users , 2)], throughput_with_x_clients, label='Throughput')
    plt.xlabel('Number of parallel Clients')
    plt.ylabel('Throughput')
    plt.title('Average Throughput vs Number of clients')
    # Save the plot to a file
    plt.legend()
    plt.savefig('throughput_plot.png')  
    plt.clf()
    # plot Cpu util

    plt.plot([users for users in range(2, num_users , 2)], cpu_utilization_values, label='CPU Utilization')
    plt.xlabel('Number of parallel Clients')
    plt.ylabel('Cpu utilization')
    plt.title('Cpu utilization vs Number of clients')
    # Save the plot to a file
    plt.legend()
    plt.savefig('cpu_util_plot.png')  
    plt.clf()
    return redirect('trigger_dispatch:code_detail', trigger_id=trigger_id)



