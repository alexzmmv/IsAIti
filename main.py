import os
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
import uuid
from google import genai
from google.genai import types


# Load API key from .env file
load_dotenv(".env")
# FastAPI app instance
app = FastAPI()

# In-memory storage for chat sessions
chat_sessions = {}

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

MODEL=genai.Client(api_key=os.getenv("GEMINI_API_KEY")).models
INSTRUCTIONS=os.getenv("INSTRUCTIONS")

@app.post("/chat/new")
async def create_chat():
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())
    random.seed(chat_id)
    isAi=random.choice([True, False])
    chat_sessions[chat_id] = {
        "type": "ai" if isAi else "ai",
        "history": []
    }
    return {"chat_id": chat_id, "message": "Chat session created"}

@app.post("/chat/{chat_id}/message", response_model=ChatResponse)
async def send_message(chat_id: str, request: ChatRequest):
    """Send a message to an existing chat session"""
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if(chat_sessions[chat_id]["type"] == "ai"):
        try:
            # Get the chat session
            session = chat_sessions[chat_id]

            # Store user message in history
            user_message = Message(role="user", content=request.message)
            session["history"].append(user_message)

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
            raise HTTPException(status_code=500, detail=str(e))
    else:
        #TODO make the human version with tcp conection to a client
        raise HTTPException(status_code=404, detail="Human variant not supported yet")


@app.get("/chat/{chat_id}/history")
async def get_chat_history(chat_id: str):
    """Get the history of a chat session"""
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return {"chat_id": chat_id, "history": chat_sessions[chat_id]["history"]}
