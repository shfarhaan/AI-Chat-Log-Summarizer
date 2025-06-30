# backend/chatbot.py
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def clean_response(text: str) -> str:
    """Clean the AI response from unwanted HTML tags and formatting"""
    if not text:
        return "I apologize, but I couldn't generate a response."
    
    # Remove common problematic HTML tags
    text = re.sub(r'</?div[^>]*>', '', text)
    text = re.sub(r'</?span[^>]*>', '', text)
    text = re.sub(r'</?p[^>]*>', '', text)
    
    # Remove any remaining HTML tags (optional - be careful with this)
    # text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    text = text.strip()
    
    return text if text else "I apologize, but I couldn't generate a proper response."

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
            top_k=top_k,
            max_output_tokens=1024,
        )
        
        # Add instruction to prevent HTML formatting
        enhanced_prompt = f"""Please respond naturally without any HTML tags or special formatting. Just plain text.

User: {prompt}"""
        
        response = model.generate_content(
            enhanced_prompt,
            generation_config=generation_config
        )
        
        # Clean the response text
        cleaned_response = clean_response(response.text)
        return cleaned_response
        
    except Exception as e:
        return f"Error: {str(e)}"