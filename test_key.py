import requests

result = requests.get("http://localhost:5000/new_api_key", params={'device_name': 'win'})
print(result.json())