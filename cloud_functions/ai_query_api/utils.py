from typing import Dict, Any
import requests
import logging
import os
import google.auth
import google.auth.transport.requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System prompt that sets the context for the AI
SYSTEM_PROMPT = """You are a helpful AI assistant that can answer questions on any topic. Please provide clear, accurate, and helpful responses.

PERSONALITY GUIDELINES:
1. Be friendly and enthusiastic
2. Be direct and concise
3. Focus on providing accurate information
4. Use a conversational tone
5. Be helpful and encouraging

CRITICAL RULES:
1. NEVER add explanations about how you work
2. NEVER apologize or express uncertainty
3. Always provide factual, helpful information
4. Stay focused on the user's question"""

def query_gemini(prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> Dict[Any, Any]:
    """Query the Gemini API with a given prompt.
    
    Args:
        prompt (str): The text prompt to send to Gemini
        temperature (float): Controls response randomness
        max_tokens (int): Maximum response length
        
    Returns:
        Dict: The JSON response from the API
    """
    try:
        # Get credentials and create request object
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        
        # Refresh credentials
        credentials.refresh(auth_req)
        
        # Combine system prompt with user's question
        full_prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {prompt}\nAnswer:"

        # API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Request headers with authorization
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {credentials.token}'
        }
        
        # Request payload
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        # Create authorized session
        authed_session = google.auth.transport.requests.AuthorizedSession(credentials)
        
        # Make the API request
        response = authed_session.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
        
    except Exception as e:
        logger.error(f"Error making request to Gemini API: {e}")
        raise

def extract_response_text(response: Dict[Any, Any]) -> str:
    """Extract the text response from Gemini API's JSON response.
    
    Args:
        response (Dict): The JSON response from Gemini API
        
    Returns:
        str: The extracted text response
    """
    try:
        return response['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting response text: {e}")
        return "Sorry, I couldn't process that response."

def get_cors_headers(for_preflight: bool = False) -> Dict[str, str]:
    """Get CORS headers for the response.
    
    Args:
        for_preflight (bool): Whether this is a preflight request
        
    Returns:
        Dict[str, str]: CORS headers
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Prompt, Authorization'
    }
    
    if for_preflight:
        headers['Access-Control-Max-Age'] = '3600'
    
    return headers

def extract_prompt(request) -> str:
    """Extract prompt from request.
    
    Checks headers, JSON body, and URL parameters in that order.
    
    Args:
        request: The Flask request object
        
    Returns:
        str: The prompt if found, None otherwise
    """
    # First check URL path (everything after the base URL)
    path = request.path
    if path and path.startswith('/'):
        path = path[1:]  # Remove leading slash
    if path:
        return path
        
    # Then check header
    prompt = request.headers.get('X-Prompt')
    if prompt:
        return prompt
    
    # Then check JSON body
    request_json = request.get_json(silent=True)
    if request_json and 'prompt' in request_json:
        return request_json['prompt']
    
    # Finally check URL parameters
    prompt = request.args.get('prompt')
    if prompt:
        return prompt
        
    return None
