import os
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
import uuid
from google import genai
from google.genai import types
import socket
import time
from contextlib import asynccontextmanager


# Model definitions
class Message(BaseModel):
    role: str  # "user" or "model"
    content: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    chat_id: str
    response: str
    history: List[Message]


# In-memory storage for chat sessions
chat_sessions = {}
MODEL = genai.Client(api_key=os.getenv("GEMINI_API_KEY")).models
INSTRUCTIONS = os.getenv("INSTRUCTIONS")
sock = None
connection = None
client_address = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(".env")
    while True:
        try:
            accept_connections()
            break
        except Exception as e:
            print(f"Error accepting connections: {e}")
            time.sleep(2)  # Wait for 5 seconds before retrying
    yield
    close_connection()
    

def close_connection():
    connection.close()
    print("Connection closed")


def accept_connections():
    print("Starting TCP server")
    
    ip=input("Enter the IP address of the tcp server: ")
    if ip=="exit" :
        os._exit(0)
    port=int(input("Enter the port number of the server: "))
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    server_address = (ip, port)
    print(f"Starting up on {server_address[0]} port {server_address[1]}")
    sock.bind(server_address)
    print("Starting TCP server")
    print("Waiting for a connection...")
    sock.listen(1)
    global connection, client_address
    connection, client_address = sock.accept()
    print("Connection established to the human client")

# FastAPI app instance
app = FastAPI(lifespan=lifespan)



@app.post("/chat/new")
async def create_chat():
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())
    random.seed(chat_id)
    isAi=random.choice([True, False])
    chat_sessions[chat_id] = {
        "type": "ai" if isAi else "human",
        "history": [],
        "isTerminated": False
    }
    if(not isAi):
        connection.sendall("\nA new chat session has been created\n".encode())
    return {"chat_id": chat_id, "message": "Chat session created"}

@app.post("/chat/{chat_id}/message", response_model=ChatResponse)
async def send_message(chat_id: str, request: ChatRequest):
    """Send a message to an existing chat session"""
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    if chat_sessions[chat_id]["isTerminated"]:
        raise HTTPException(status_code=400, detail="Chat session is terminated")
    
    # Get the chat session
    session = chat_sessions[chat_id]
    # Store user message in history
    user_message = Message(role="user", content=request.message)
    session["history"].append(user_message)
    if chat_sessions[chat_id]["type"] == "ai":
        # Calculate delay based on message length and a random factor
        message_length = len(request.message)
        random_delay = random.uniform(0.7, 2)
        delay = message_length * 0.06 + random_delay
        time.sleep(delay)
        try:
            
            # Prepare the conversation history for the model
            conversation_history = "\n".join([f"{msg.role}: {msg.content}" for msg in session["history"]])
            # Get response from Gemini
            response = MODEL.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=INSTRUCTIONS
                ),
                contents=conversation_history,
            )

            # Store model response in history
            model_message = Message(role="model", content=response.text)
            session["history"].append(model_message)

            return {
                "chat_id": chat_id,
                "response": response.text,
                "history": session["history"]
            }
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal server error")
    else:
        connection.sendall(request.message.encode())
        data = connection.recv(1024)
        response = data.decode()
        model_message = Message(role="model", content=response)
        session["history"].append(model_message)
        return {
            "chat_id": chat_id,
            "response": response,
            "history": session["history"]
        }

@app.get("/chat/{chat_id}/history")
async def get_chat_history(chat_id: str):
    """Get the history of a chat session"""
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return {"chat_id": chat_id, "history": chat_sessions[chat_id]["history"], "isTerminated": chat_sessions[chat_id]["isTerminated"]}

@app.get("/chat/{chat_id}/end")
async def end_chat_session(chat_id: str, guess: str):
    """End a chat session"""
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")        
    is_corect = False
    chat_sessions[chat_id]["isTerminated"] = True
    if(chat_sessions[chat_id]["type"] == "human"):
        connection.sendall("\nChat session ended\n".encode())
    if(guess == chat_sessions[chat_id]["type"]):
        is_corect = True
    

    return {"chat_id": chat_id, "message": "Chat session ended", "is_corect": is_corect}