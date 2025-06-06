# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import get_ai_response
from summarizer import generate_summary
import os

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running. Try POST /chat or GET /summarize"}

# Enable CORS for frontend interaction (Streamlit runs on a different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Limit this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_LOG_PATH = os.path.join("backend", "data", "chat.txt")
os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)

class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
def chat_endpoint(payload: ChatRequest):
    user_msg = f"User: {payload.user_input}"
    ai_msg_text = get_ai_response(payload.user_input)
    ai_msg = f"AI: {ai_msg_text}"

    with open(CHAT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(user_msg + "\n")
        f.write(ai_msg + "\n")

    return {"ai_response": ai_msg_text}

@app.get("/summarize")
def summarize_endpoint():
    return generate_summary(CHAT_LOG_PATH)
