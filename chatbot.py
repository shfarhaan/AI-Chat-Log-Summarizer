# backend/chatbot.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def get_ai_response(
    prompt: str,
    temperature: float = 0.7,  # Controls randomness (0.0-1.0)
    top_p: float = 0.9,        # Nucleus sampling (0.0-1.0)
    top_k: int = 40            # Top-k sampling (1-100+)
) -> str:
    try:
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
            # max_output_tokens=1024,  # Optional: limit response length
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"