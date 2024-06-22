import requests
import json

url = 'http://127.0.0.1:5000/top-products'
headers = {'Content-Type': 'application/json'}
payload = {
    'industries': ['tech', 'fashion', 'food']
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())