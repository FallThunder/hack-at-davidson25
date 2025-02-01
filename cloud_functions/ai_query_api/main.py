import functions_framework
from flask import jsonify, Response
import google.auth
import google.auth.transport.requests
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from utils import extract_prompt, get_config

PROJECT_ID = "hack-at-davidson25"
LOCATION = "us-east1"

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

        # Get system prompt from config
        system_prompt = get_config()
        
        # Combine system prompt with user query
        full_prompt = f"{system_prompt}\n\nUSER QUERY: {prompt}"

        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Create the model
        model = GenerativeModel("gemini-1.5-flash-002")
        
        # Generate content with the full prompt including system instructions
        response = model.generate_content(full_prompt)
        
        # Return the raw response text as JSON
        return Response(
            response.text,
            status=200,
            headers=headers
        )

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
            headers,
        )
