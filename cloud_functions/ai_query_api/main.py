import functions_framework
from flask import jsonify, Response
import google.auth
import google.auth.transport.requests
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from utils import extract_prompt, get_config, get_business_directory

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

        # Get system prompt and business directory
        system_prompt = get_config()
        business_directory = get_business_directory()
        
        # Combine system prompt with business directory and user query
        full_prompt = f"""
{system_prompt}

BUSINESS DIRECTORY HTML:
```html
{business_directory}
```

USER QUERY: {prompt}

Remember to:
1. Search the business directory above for relevant matches
2. Return data in the exact format specified
3. Only include businesses found in the directory
"""

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
