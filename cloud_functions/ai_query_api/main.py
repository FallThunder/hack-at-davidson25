import functions_framework
from flask import jsonify
import json
from typing import Dict, Any
import logging
from utils import generate_search_params, query_gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def ai_query_assistant(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
    """
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET and POST requests from any origin with the Content-Type
        # header and caches preflight response for 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {
        "Access-Control-Allow-Origin": "*"
    }
    
    try:
        query = None
        
        # Handle POST request with JSON body
        if request.method == "POST" and request.is_json:
            request_json = request.get_json()
            if request_json:
                query = request_json.get('query') or request_json.get('prompt')
        
        # Handle GET request with query parameter
        if not query:
            query = request.args.get("query") or request.args.get("prompt")
            
        if not query:
            return (jsonify({"error": "No query/prompt parameter provided"}), 400, headers)
            
        # Generate search parameters and process business cards using the function from utils.py
        search_results = generate_search_params(query)
        
        if "error" in search_results:
            return (jsonify({"error": search_results["error"]}), 500, headers)
            
        return (jsonify(search_results), 200, headers)
        
    except Exception as e:
        logger.error(f"Error in ai_query_assistant: {e}")
        return (jsonify({"error": str(e)}), 500, headers)
