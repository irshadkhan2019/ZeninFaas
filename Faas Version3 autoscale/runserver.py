# run_servers.py
import multiprocessing
import os

def run_server(port):
    os.system(f'python manage.py runserver 127.0.0.1:{port}')

if __name__ == '__main__':
    # Define the ports for each server
    ports = [8000, 8001, 8002, 8003]

    # Start a separate process for each server
    processes = []
    for port in ports:
        process = multiprocessing.Process(target=run_server, args=(port,))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()
