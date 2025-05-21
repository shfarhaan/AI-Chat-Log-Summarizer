from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.chatbot import get_ai_response
from backend.summarizer import generate_summary

app = FastAPI()

chat_log_path = "backend/data/chat.txt"

class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
def chat_endpoint(payload: ChatRequest):
    user_msg = f"User: {payload.user_input}"
    ai_msg = f"AI: {get_ai_response(payload.user_input)}"
    
    with open(chat_log_path, "a") as f:
        f.write(user_msg + "\n")
        f.write(ai_msg + "\n")

    return {"ai_response": ai_msg[4:]}

@app.get("/summarize")
def summarize_endpoint():
    return generate_summary(chat_log_path)
