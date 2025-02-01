from typing import Dict, Any
import requests
import logging
import os
import json
import google.auth
import google.auth.transport.requests
from google.cloud import storage
from google.cloud import secretmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_config() -> str:
    """Get configuration from Cloud Storage bucket.
    
    Returns:
        str: Configuration text containing system prompt
    """
    try:
        # Create storage client
        storage_client = storage.Client()
        
        # Get bucket and blob
        bucket = storage_client.bucket('pine-config')
        blob = bucket.blob('pine_config.txt')
        
        # Download config as text
        return blob.download_as_text()
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        # Return default config if unable to read from bucket
        return """Please inform the user that Pine (your name) is currently offline and unable to process their request."""

def get_api_key() -> str:
    """Get Gemini API key from Secret Manager.
    
    Returns:
        str: API key for Gemini
    """
    try:
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name
        name = f"projects/hack-at-davidson25/secrets/flash-8b-api-key/versions/latest"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Error getting API key: {e}")
        raise

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
        # Get configuration and API key
        config = get_config()
        api_key = get_api_key()
        business_directory = get_business_directory()
        
        # Combine system prompt with business directory and user's question
        full_prompt = f"""{config}

BUSINESS DIRECTORY DATA:
{business_directory}

USER QUERY: {prompt}

Remember to:
1. Search the business directory above for relevant matches
2. Return data in the exact format specified
3. Only include businesses found in the directory"""

        # API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Request headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Request payload
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": temperature if temperature is not None else 0.7,
                "maxOutputTokens": max_tokens if max_tokens is not None else 1024,
                "topK": 40,
                "topP": 0.8
            }
        }
        
        # Make the API request
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=payload
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response
        api_response = response.json()
        
        # Extract and parse the text response
        return api_response['candidates'][0]['content']['parts'][0]['text']
        
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

def get_business_directory() -> str:
    """Get business directory data from both CSV and HTML sources in Cloud Storage bucket.
    
    Returns:
        str: Combined business directory data containing both CSV and HTML
    """
    try:
        # Create storage client
        storage_client = storage.Client()
        
        # Get bucket
        bucket = storage_client.bucket('pine-config')
        
        # Get both blobs
        commerce_blob = bucket.blob('lkncommerce-rolodex.csv')
        business_blob = bucket.blob('lknbusiness-rolodex.html')
        
        # Get both contents
        commerce_data = commerce_blob.download_as_text()
        business_data = business_blob.download_as_text()
        
        # Combine both data sources
        combined_data = f"""
COMMERCE DIRECTORY (CSV):
{commerce_data}

BUSINESS DIRECTORY (HTML):
{business_data}
"""
        return combined_data
        
    except Exception as e:
        logger.error(f"Error reading business directory: {e}")
        # Return empty data if unable to read from bucket
        return ""
