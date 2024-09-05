from sseclient import SSEClient
import requests

response = requests.get('http://127.0.0.1:5000/admin/listen', stream=True)
print(response.headers)

messages = SSEClient('http://127.0.0.1:5000/admin/listen') 

for msg in messages:
    print(msg)