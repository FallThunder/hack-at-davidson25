from typing import Dict, Any
import requests
import logging
import os
import json
import google.auth
import google.auth.transport.requests
from google.cloud import storage
from google.cloud import secretmanager
from google.oauth2 import id_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_businesses_data() -> str:
    """Get businesses data from Cloud Storage.
    
    Returns:
        str: Line 171 of the HTML content containing all business data.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket('pine-config')
    blob = bucket.blob('lknbusiness-rolodex.html')
    
    try:
        # Download HTML as text and split into lines
        html_lines = blob.download_as_text().splitlines()
        
        # Return line 171 if it exists
        if len(html_lines) >= 171:
            # Clean up the HTML line to prevent JSON parsing issues
            html_line = html_lines[170]  # 0-based index for line 171
            # Remove any unescaped quotes and normalize whitespace
            html_line = html_line.replace('\\"', '"').replace('"', '\\"').strip()
            return html_line
        logger.error("Business data file does not contain enough lines")
        return ""
    except Exception as e:
        logger.error(f"Error reading businesses data: {e}")
        return ""

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
        return None

def query_gemini(prompt: str, temperature: float = None, max_tokens: int = None) -> Dict[Any, Any]:
    """Query Gemini API with prompt.
    
    Args:
        prompt (str): Prompt text
        temperature (float, optional): Sampling temperature. Defaults to None.
        max_tokens (int, optional): Max tokens to generate. Defaults to None.
        
    Returns:
        Dict[Any, Any]: API response
    """
    try:
        # Get API key
        api_key = get_api_key()
        if not api_key:
            raise Exception("Unable to get API key")
            
        # Get businesses data
        businesses_html = get_businesses_data()
        
        # Make API request
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json={
                "contents": [{"parts":[{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature if temperature is not None else 0.1,
                    "maxOutputTokens": max_tokens if max_tokens is not None else 2048,
                    "topP": 0.8,
                    "topK": 40
                }
            }
        )
        
        # Check for quota exceeded
        if response.status_code == 429:
            logger.error("Gemini API quota exceeded")
            return {
                "error": "Service is temporarily unavailable due to high demand. Please try again in a few minutes."
            }
            
        # Check for other errors
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return {"error": f"API request failed: {response.text}"}
            
        return response.json()
        
    except Exception as e:
        logger.error(f"Error querying Gemini: {e}")
        return {"error": str(e)}

def extract_response_text(response: Dict[Any, Any]) -> str:
    """Extract the text response from Gemini API's JSON response.
    
    Args:
        response (Dict): The JSON response from Gemini API
        
    Returns:
        str: The extracted text response
    """
    try:
        if "candidates" in response:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        return response
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
        'Access-Control-Allow-Methods': 'GET, POST',
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

def get_id_token() -> str:
    """Get ID token for authenticating with other Cloud Functions.
    
    Returns:
        str: ID token for authentication
    """
    try:
        # Get credentials and target audience
        creds, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        
        # Refresh credentials and get ID token
        creds.refresh(auth_req)
        
        # Get ID token with the correct audience (image processing function URL)
        id_token = google.oauth2.id_token.fetch_id_token(
            auth_req, 
            "https://us-east1-hack-at-davidson25.cloudfunctions.net/image_processing"
        )
        return id_token
    except Exception as e:
        logger.error(f"Error getting ID token: {e}")
        return None

def process_business_card(card_url: str) -> Dict[str, Any]:
    """Process a business card image using the image processing API.
    
    Args:
        card_url (str): URL of the business card image
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted business information
    """
    try:
        # Standard prompt for all business cards
        STANDARD_PROMPT = "Extract all information from this business card and return it in a JSON format with exactly these keys: business_name, owner_name, phone_number, email, address, any_other_details. If any field is not found, set it to null."
        
        # Get authentication token
        id_token = get_id_token()
        if not id_token:
            raise Exception("Failed to get authentication token")
        
        # Call image processing API with authentication
        response = requests.post(
            "https://us-east1-hack-at-davidson25.cloudfunctions.net/image_processing",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {id_token}"
            },
            json={
                "prompt": STANDARD_PROMPT,
                "image_url": card_url
            },
            timeout=25  # Set timeout to less than the function's 30s timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        # Parse the response JSON and ensure it has the required structure
        extracted_info = json.loads(response.json().get("response", "{}"))
        
        # Ensure all required fields exist
        required_fields = ["business_name", "owner_name", "phone_number", "email", "address", "any_other_details"]
        for field in required_fields:
            if field not in extracted_info:
                extracted_info[field] = None
                
        return extracted_info
        
    except Exception as e:
        logger.error(f"Error processing business card: {e}")
        return {
            "business_name": None,
            "owner_name": None,
            "phone_number": None,
            "email": None,
            "address": None,
            "any_other_details": None
        }

def generate_search_params(query: str) -> Dict[str, Any]:
    """Generate search parameters based on user query.
    
    Args:
        query (str): User's search query
        
    Returns:
        Dict[str, Any]: Search results with matched businesses
    """
    try:
        # Get system prompt
        system_prompt = get_config()
        
        # Get businesses data
        businesses_html = get_businesses_data()
        if not businesses_html:
            return {"error": "Unable to load business data"}
            
        # Create full prompt
        full_prompt = f"{system_prompt}\n\nBusiness Directory HTML:\n{businesses_html}\n\nUser Query: {query}"
        
        # Query Gemini
        response = query_gemini(full_prompt)
        
        # Check for errors
        if isinstance(response, dict) and "error" in response:
            return response
            
        # Extract text from Gemini response
        response_text = extract_response_text(response)
        
        # Parse the response
        try:
            if isinstance(response_text, str):
                raw_result = json.loads(response_text)
            elif isinstance(response_text, dict):
                raw_result = response_text
            else:
                logger.error(f"Unexpected response type: {type(response_text)}")
                return {"error": "Unexpected response format from AI model"}
            
            # Structure the final response
            final_results = {
                "matched_businesses": [],
                "match_count": 0
            }
            
            # Process each business
            for business in raw_result.get("matched_businesses", []):
                if "card_link" in business:
                    # Process the business card
                    business_info = process_business_card(business["card_link"])
                    
                    # Add to final results with all required fields
                    final_results["matched_businesses"].append({
                        "business_info": business_info,
                        "homepage_link": business.get("business_link"),
                        "card_link": business["card_link"]
                    })
            
            final_results["match_count"] = len(final_results["matched_businesses"])
            return final_results
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            return {"error": "Unable to parse AI response"}
    except Exception as e:
        logger.error(f"Error generating search parameters: {e}")
        return {"error": str(e)}
