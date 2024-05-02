import requests

# URL of the endpoint associated with the "Deploy" button
deploy_url = 'http://127.0.0.1:8000/dispatch-trigger/13'

# Sample code to be deployed
code = 'print("Hello, world!")'

# Data to be sent in the POST request
data = {
    'code': code,
    # Include any other necessary data here if required
}

# Send POST request to simulate pressing the "Deploy" button
response = requests.post(deploy_url, data=data)
print(response)

# Check the response
if response.status_code == 200:
    print("Deployment successful!")
    # Optionally, you can parse and print any response data returned by the server
    print(response.text)
else:
    print("Deployment failed. Status code:", response.status_code)
