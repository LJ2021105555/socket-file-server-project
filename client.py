import requests

url = 'http://127.0.0.1:8000'
data = 'Hello, this is a test request!'
response = requests.post(url, data=data)
print(response.text)
