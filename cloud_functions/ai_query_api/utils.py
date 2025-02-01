from typing import Dict, Any
import requests
import logging
import os
import json
from io import BytesIO
import google.auth
import google.auth.transport.requests
from google.cloud import storage
from vertexai.preview.generative_models import Image

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
        return """Please inform the user that Pine (your name) is currently offline and unable to process their request.
        """

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
        full_prompt = f"{config}\n\nUSER QUERY: {prompt}"

        # Get model settings
        model_settings = {
            "model": "gemini-1.5-flash-002",
            "temperature": temperature if temperature is not None else 0.7,
            "max_tokens": max_tokens if max_tokens is not None else 1024,
            "location": "us-east1"
        }
        api_settings = {
            "project_id": "hack-at-davidson25",
            "endpoint": "https://us-east1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:streamGenerateContent"
        }
        
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
                "temperature": model_settings['temperature'],
                "maxOutputTokens": model_settings['max_tokens']
            }
        }
        
        # Create authorized session
        authed_session = google.auth.transport.requests.AuthorizedSession(credentials)
        
        # Make the API request
        response = authed_session.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response
        api_response = response.json()
        
        # Extract and parse the text response
        response_text = api_response['candidates'][0]['content']['parts'][0]['text']
        try:
            # Try to parse the response as JSON
            business_data = json.loads(response_text)
            return business_data
        except json.JSONDecodeError:
            # If response is not valid JSON, return an error message
            return {
                "error": "Response was not in valid JSON format",
                "raw_response": response_text
            }
        
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
    """Get business directory data from both JSON and HTML sources in Cloud Storage bucket.
    
    Returns:
        str: Combined business directory data containing both JSON and HTML
    """
    try:
        # Create storage client
        storage_client = storage.Client()
        
        # Get bucket
        bucket = storage_client.bucket('pine-config')
        
        # Get both blobs
        commerce_blob = bucket.blob('lkncommerce-rolodex.json')
        business_blob = bucket.blob('lknbusiness-rolodex.html')
        
        # Get both contents
        commerce_data = commerce_blob.download_as_text()
        business_data = business_blob.download_as_text()
        
        # Combine both data sources
        combined_data = f"""
COMMERCE DIRECTORY (JSON):
{commerce_data}

BUSINESS DIRECTORY (HTML):
{business_data}
"""
        return combined_data
        
    except Exception as e:
        logger.error(f"Error reading business directory: {e}")
        # Return empty data if unable to read from bucket
        return "[]"

def process_business_card(model, image_url: str) -> Dict[str, Any]:
    """Process a business card image using Gemini.
    
    Args:
        model: The Gemini model instance
        image_url: URL of the business card image
        
    Returns:
        Dict[str, Any]: Extracted information from the business card
    """
    try:
        # Download image
        response = requests.get(image_url)
        if response.status_code != 200:
            logger.error(f"Failed to download image from {image_url}")
            return None
            
        # Load image for Gemini
        image_bytes = BytesIO(response.content)
        image = Image.load_from_bytes(image_bytes.read())
        
        # Create prompt for business card analysis
        image_prompt = """
        Analyze this business card image and extract the following information in JSON format:
        {
            "full_name": "Name from card",
            "title": "Title/Role if present",
            "company": "Company name",
            "contact": {
                "phone": "Phone number if present",
                "email": "Email if present",
                "website": "Website if present",
                "address": "Address if present"
            },
            "additional_details": {
                "services": ["Service 1", "Service 2"],
                "specialties": ["Specialty 1", "Specialty 2"],
                "other": "Any other relevant information"
            }
        }
        """
        
        # Generate content with image
        response = model.generate_content([image_prompt, image])
        
        # Parse response as JSON
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.error("Failed to parse card info as JSON")
            return {"raw_text": response.text}
            
    except Exception as e:
        logger.error(f"Error processing business card: {str(e)}")
        return None

def process_business_results(model, businesses_data: str) -> Dict[str, Any]:
    """Process business results and enhance with card details.
    
    Args:
        model: The Gemini model instance
        businesses_data: JSON string of business results
        
    Returns:
        Dict[str, Any]: Enhanced business data with card details
    """
    try:
        businesses = json.loads(businesses_data)
        
        # If it's a specific business query
        if businesses.get("query_type") == "specific":
            business_details = businesses["business_details"]
            if business_details.get("image_url"):
                card_info = process_business_card(model, business_details["image_url"])
                if card_info:
                    business_details["card_details"] = card_info
        
        # If it's a general search
        elif businesses.get("businesses"):
            for business in businesses["businesses"]:
                if business.get("image_url"):
                    card_info = process_business_card(model, business["image_url"])
                    if card_info:
                        business["card_details"] = card_info
        
        return businesses
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse businesses data: {str(e)}")
        return None
