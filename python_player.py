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
    if message == "exit chat":
        response = requests.get(url + f'chat/{chat_id}/end', params={'guess': input("Guess(\"ai\" or \"human\"): ").strip().lower()})
        response.raise_for_status()
        print(response.json())
        print("Chat session ended.")
        break
    response = requests.post(url + f'chat/{chat_id}/message', json={'message': message})
    response.raise_for_status()
    data = response.json()
    print(f"Server: {data['response']}")
    