import requests
import json

url = 'http://localhost:8000/'

message_data = {
    'message': 'exit chat'
}

try:
    response = requests.post(url + 'chat/8ab9d54a-6409-48a1-ab82-34bce3c7da9c/message', json=message_data)
    response.raise_for_status()  # Raise an error for bad status codes
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError:
    print("The response is not in JSON format.")