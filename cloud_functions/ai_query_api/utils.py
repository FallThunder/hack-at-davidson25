from typing import Dict, Any
import requests
import logging
import os
import json
import google.auth
import google.auth.transport.requests
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_config() -> Dict[str, Any]:
    """Get configuration from Cloud Storage bucket.
    
    Returns:
        Dict: Configuration dictionary
    """
    try:
        # Create storage client
        storage_client = storage.Client()
        
        # Get bucket and blob
        bucket = storage_client.bucket('pine-config')
        blob = bucket.blob('pine_config.txt')
        
        # Download and parse config
        config_str = blob.download_as_text()
        return json.loads(config_str)
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        # Return default config if unable to read from bucket
        return {
            "system_prompt": "You are Pine, a professional AI assistant specialized in helping people find the right businesses and services.",
            "model_settings": {
                "model": "gemini-1.5-flash-002",
                "temperature": 0.7,
                "max_tokens": 1024,
                "location": "us-east1"
            },
            "api_settings": {
                "project_id": "hack-at-davidson25",
                "endpoint": "https://us-east1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:streamGenerateContent"
            }
        }

def query_gemini(prompt: str, temperature: float = None, max_tokens: int = None) -> Dict[Any, Any]:
    """Query the Gemini API with a given prompt.
    
    Args:
        prompt (str): The text prompt to send to Gemini
        temperature (float, optional): Controls response randomness
        max_tokens (int, optional): Maximum response length
        
    Returns:
        Dict: The JSON response from the API
    """
    try:
        # Get configuration
        config = get_config()
        
        # Get credentials and create request object
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        
        # Refresh credentials
        credentials.refresh(auth_req)
        
        # Combine system prompt with user's question
        full_prompt = f"{config['system_prompt']}\n\nQuestion: {prompt}\nAnswer:"

        # Get model settings
        model_settings = config['model_settings']
        api_settings = config['api_settings']
        
        # Format endpoint URL
        url = api_settings['endpoint'].format(
            project_id=api_settings['project_id'],
            location=model_settings['location'],
            model=model_settings['model']
        )
        
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
                "temperature": temperature if temperature is not None else model_settings['temperature'],
                "maxOutputTokens": max_tokens if max_tokens is not None else model_settings['max_tokens']
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

def extract_prompt(request):
    """Extract prompt from request body, URL parameters, or path."""
    # First check request body for JSON
    if request.is_json:
        json_data = request.get_json()
        if json_data and 'prompt' in json_data:
            return json_data['prompt']
    
    # Then check form data
    if request.form and 'prompt' in request.form:
        return request.form['prompt']
    
    # Then check URL parameters
    if request.args and 'prompt' in request.args:
        return request.args['prompt']
    
    # Finally check path
    path = request.path
    if path and path.startswith('/'):
        path = path[1:]  # Remove leading slash
    if path:
        return path
    
    return None
