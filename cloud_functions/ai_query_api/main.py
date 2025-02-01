import functions_framework
from flask import jsonify
import google.auth
import google.auth.transport.requests
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from utils import extract_prompt

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
    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        prompt = extract_prompt(request)
        if not prompt:
            return (jsonify({"error": "No prompt provided"}), 400, headers)

        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Create the model
        model = GenerativeModel("gemini-1.5-flash-002")
        
        # Generate content
        response = model.generate_content(prompt)
        
        return (jsonify({"response": response.text}), 200, headers)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return (
            jsonify({"error": f"Failed to process request: {str(e)}"}),
            500,
            headers,
        )
