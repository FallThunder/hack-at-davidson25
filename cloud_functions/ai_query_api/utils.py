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
import html2text
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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
                    "temperature": temperature if temperature is not None else 0.3,
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
            text_response = response["candidates"][0]["content"]["parts"][0]["text"]
            # Ensure the response is valid JSON
            try:
                json_response = json.loads(text_response)
                # Validate that best_match exists and is properly formatted
                if "best_match" not in json_response:
                    json_response["best_match"] = {
                        "business_link": None,
                        "card_link": None,
                        "reason": "No best match could be determined"
                    }
                return json.dumps(json_response)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response")
                return json.dumps({
                    "matched_businesses": [],
                    "match_count": 0,
                    "best_match": {
                        "business_link": None,
                        "card_link": None,
                        "reason": "Error processing response"
                    }
                })
        return response
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting response text: {e}")
        return json.dumps({
            "matched_businesses": [],
            "match_count": 0,
            "best_match": {
                "business_link": None,
                "card_link": None,
                "reason": "Error processing response"
            }
        })

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

def get_website_content(url: str) -> str:
    """Safely fetch and extract content from a business website.
    
    Args:
        url (str): The business website URL
        
    Returns:
        str: Extracted text content from the website, or empty string if failed
    """
    try:
        logger.info(f"🌐 Attempting to fetch content from: {url}")
        
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            logger.warning(f"❌ Invalid URL format: {url}")
            return ""
            
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
            
        # Fetch content with timeout
        logger.info(f"📥 Fetching HTML content from {url}")
        try:
            response = requests.get(url, timeout=15, verify=True, headers=headers)
            response.raise_for_status()
            html_content = response.text
            logger.info(f"✅ Successfully fetched {len(html_content)} bytes from {url}")
        except requests.exceptions.SSLError:
            # Try again without SSL verification if SSL fails
            logger.warning(f"⚠️ SSL verification failed for {url}, retrying without verification")
            response = requests.get(url, timeout=15, verify=False, headers=headers)
            response.raise_for_status()
            html_content = response.text
            logger.info(f"✅ Successfully fetched {len(html_content)} bytes from {url} (without SSL verification)")
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        script_count = len(soup(["script", "style"]))
        for script in soup(["script", "style"]):
            script.decompose()
        logger.info(f"🧹 Removed {script_count} script/style elements")
            
        # Convert HTML to plain text
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        text_content = h.handle(str(soup))
        
        # Clean and truncate the text
        clean_text = ' '.join(text_content.split())[:2000]  # Limit to first 2000 chars
        logger.info(f"📝 Extracted {len(clean_text)} characters of clean text from {url}")
        return clean_text
        
    except requests.Timeout:
        logger.error(f"⏰ Timeout while fetching content from {url}")
        return ""
    except requests.RequestException as e:
        logger.error(f"❌ Error fetching website content from {url}: {e}")
        return ""
    except Exception as e:
        logger.error(f"❌ Unexpected error processing content from {url}: {e}")
        return ""

def generate_search_params(query: str) -> Dict[str, Any]:
    """Generate search parameters based on user query.
    
    Args:
        query (str): User's search query
        
    Returns:
        Dict[str, Any]: Search results with matched businesses
    """
    try:
        logger.info(f"🔍 Processing query: {query}")
        
        # Get system prompt
        system_prompt = get_config()
        
        # Get businesses data
        businesses_html = get_businesses_data()
        if not businesses_html:
            return {"error": "Unable to load business data"}
            
        # Create full prompt
        full_prompt = f"{system_prompt}\n\nBusiness Directory HTML:\n{businesses_html}\n\nUser Query: {query}"
        
        # Query Gemini for initial business matching
        logger.info("🤖 Querying Gemini for initial business matching")
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
            
            logger.info(f"📊 Initial matches found: {len(raw_result.get('matched_businesses', []))} businesses")
            
            # Structure the final response
            final_results = {
                "matched_businesses": [],
                "match_count": 0,
                "best_match": raw_result.get("best_match", {})
            }
            
            # Process each business
            website_contents = {}
            successful_fetches = 0
            for business in raw_result.get("matched_businesses", []):
                if "card_link" in business:
                    # Process the business card
                    logger.info(f"💼 Processing business card for: {business.get('business_link', 'Unknown Business')}")
                    business_info = process_business_card(business["card_link"])
                    
                    # Fetch website content if available
                    website_content = ""
                    if business.get("business_link"):
                        logger.info(f"🌐 Fetching website content for potential match: {business['business_link']}")
                        website_content = get_website_content(business["business_link"])
                        if website_content:
                            logger.info(f"✅ Successfully fetched website content ({len(website_content)} chars)")
                            website_contents[business["business_link"]] = website_content
                            successful_fetches += 1
                        else:
                            logger.warning(f"⚠️ No website content available for {business['business_link']}")
                    
                    # Add to final results with all required fields
                    final_results["matched_businesses"].append({
                        "business_info": business_info,
                        "homepage_link": business.get("business_link"),
                        "card_link": business["card_link"]
                    })
            
            # If we have enough website contents, use them to refine the best match
            if website_contents and successful_fetches >= 1:
                logger.info(f"🔄 Analyzing website content for {len(website_contents)} businesses")
                # Create a prompt for website content analysis
                website_analysis_prompt = f"""Based on the user query: "{query}"
                And the following website contents for each business:
                {json.dumps(website_contents, indent=2)}
                
                Analyze which business best matches the query. Consider:
                1. Relevance of services/products to the query
                2. Depth of information available
                3. Specific expertise mentioned
                4. Current activity/availability of the business
                
                Return only a JSON with the best matching business link and a reason why."""
                
                # Query Gemini for website analysis
                logger.info("🤖 Querying Gemini for website content analysis")
                website_analysis = query_gemini(website_analysis_prompt, temperature=0.2)
                if isinstance(website_analysis, dict) and "error" not in website_analysis:
                    analysis_text = extract_response_text(website_analysis)
                    try:
                        analysis_result = json.loads(analysis_text)
                        if "business_link" in analysis_result:
                            logger.info(f"✨ Website analysis selected best match: {analysis_result['business_link']}")
                            logger.info(f"📝 Selection reason: {analysis_result.get('reason', 'No reason provided')}")
                            # Update the best match based on website analysis
                            for business in raw_result.get("matched_businesses", []):
                                if business.get("business_link") == analysis_result["business_link"]:
                                    final_results["best_match"] = {
                                        "business_link": business["business_link"],
                                        "card_link": business["card_link"],
                                        "business_name": business_info.get("business_name"),
                                        "reason": analysis_result.get("reason", "Best match based on website content analysis")
                                    }
                                    break
                    except json.JSONDecodeError:
                        logger.error("❌ Failed to parse website analysis result")
                else:
                    logger.warning("⚠️ Website analysis failed or returned error")
            else:
                logger.info("ℹ️ Using business card information for best match selection")
                # Create a prompt for business card analysis
                card_analysis_prompt = f"""Based on the user query: "{query}"
                And the following business information:
                {json.dumps([b["business_info"] for b in final_results["matched_businesses"]], indent=2)}
                
                Analyze which business best matches the query based on their business card information. Consider:
                1. Business name and description
                2. Services mentioned
                3. Professional focus
                4. Contact information completeness
                
                Return only a JSON with the best matching business card link and a reason why."""
                
                # Query Gemini for card analysis
                logger.info("🤖 Querying Gemini for business card analysis")
                card_analysis = query_gemini(card_analysis_prompt, temperature=0.2)
                if isinstance(card_analysis, dict) and "error" not in card_analysis:
                    analysis_text = extract_response_text(card_analysis)
                    try:
                        analysis_result = json.loads(analysis_text)
                        if "card_link" in analysis_result:
                            logger.info(f"✨ Business card analysis selected best match")
                            logger.info(f"📝 Selection reason: {analysis_result.get('reason', 'No reason provided')}")
                            # Update the best match based on card analysis
                            for business in final_results["matched_businesses"]:
                                if business["card_link"] == analysis_result["card_link"]:
                                    final_results["best_match"] = {
                                        "business_link": business.get("homepage_link"),
                                        "card_link": business["card_link"],
                                        "business_name": business["business_info"].get("business_name"),
                                        "reason": analysis_result.get("reason", "Best match based on business card information")
                                    }
                                    break
                    except json.JSONDecodeError:
                        logger.error("❌ Failed to parse card analysis result")
            
            final_results["match_count"] = len(final_results["matched_businesses"])
            logger.info(f"✅ Final results: {final_results['match_count']} businesses, best match determined: {'best_match' in final_results}")
            return final_results
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            return {"error": "Unable to parse AI response"}
    except Exception as e:
        logger.error(f"Error generating search parameters: {e}")
        return {"error": str(e)}
