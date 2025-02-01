import functions_framework
from flask import jsonify, Response, request
import json
from utils import (
    extract_prompt,
    get_config,
    get_business_directory,
    query_gemini
)

def handle_query(prompt, system_prompt, business_directory, headers):
    """Handle business directory queries."""
    try:
        # Query Gemini API
        response = query_gemini(prompt)
        
        return Response(
            json.dumps(response),
            status=200,
            headers=headers,
            mimetype='application/json'
        )
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers,
            mimetype='application/json'
        )

@functions_framework.http
def ai_query_assistant(request):
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }

    try:
        # Check if it's a POST request
        if request.method != "POST":
            return (
                jsonify({
                    "error": "Only POST requests are supported",
                    "example": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "body": {"prompt": "Your question here"}
                    }
                }),
                405,
                headers
            )

        prompt = extract_prompt(request)
        if not prompt:
            return (
                jsonify({
                    "error": "No prompt provided",
                    "example": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "body": {"prompt": "Your question here"}
                    }
                }),
                400,
                headers
            )

        # Get system prompt and business directory
        system_prompt = get_config()
        business_directory = get_business_directory()
        
        return handle_query(prompt, system_prompt, business_directory, headers)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return (
            jsonify({
                "error": f"Failed to process request: {str(e)}",
                "example": {
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "body": {"prompt": "Your question here"}
                }
            }),
            500,
            headers
        )
