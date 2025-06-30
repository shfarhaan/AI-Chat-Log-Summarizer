import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def get_ai_response(
    prompt: str,
    temperature: float = 0.7, # Default: moderate randomness
    top_p: float = 0.9,      # Default: good diversity
    top_k: int = 40          # Default: considers a decent pool of tokens
)-> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# # Example usage:
# prompt_text = "Tell me a fun fact."
# response_text = get_ai_response(prompt_text)
# print(response_text)