import requests
import json

url = 'http://localhost:8000/'

message_data = {
    'message': ''
}

def create_chat():
    response = requests.post(url + 'chat/new')
    response.raise_for_status()
    return response.json().get('chat_id')

chat_id = create_chat()
while True:
    message = input("Message: ")
    response = requests.post(url + f'chat/{chat_id}/message', json={'message': message})
    response.raise_for_status()
    data = response.json()
    print(f"Server: {data['response']}")
    if message == "exit chat":
        break