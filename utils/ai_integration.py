import google.generativeai as genai
import os

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_ai_response(prompt):
    """
    Generate a response using Google Gemini API.
    Returns the text response or a fallback message if API is not configured.
    """
    if not API_KEY:
        return "AI Mode is currently offline. Please configure the GEMINI_API_KEY in your environment to correctly use this feature. For now, I can only search your local notes."
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error contacting AI service: {str(e)}"

def summarize_text(text):
    """
    Summarize the given text using Gemini.
    """
    if not API_KEY:
        return "Summary unavailable (API Key missing)."
        
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Please provide a concise summary of the following study notes:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"
