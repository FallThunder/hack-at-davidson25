import google.generativeai as genai
from PIL import Image
import os
import json
import functions_framework
from dotenv import load_dotenv
import requests
import tempfile
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv('GENAI_API_KEY'))

def download_image(image_url):
    """Download image from URL and save to temporary file.
    
    Args:
        image_url (str): URL of the image to download
        
    Returns:
        str: Path to the downloaded image file
    """
    try:
        # Validate URL
        parsed = urlparse(image_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL provided")
            
        # Download image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Create temporary file
        suffix = os.path.splitext(parsed.path)[1] or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            return temp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to download image: {str(e)}")

def upload_image(image_source):
    """Upload an image to Gemini from either a local path or URL.
    
    Args:
        image_source (str): Local file path or URL of the image
        
    Returns:
        file: Uploaded file object
    """
    try:
        # Check if image_source is a URL
        parsed = urlparse(image_source)
        if parsed.scheme and parsed.netloc:
            # Download image from URL first
            image_path = download_image(image_source)
        else:
            # Use local path
            image_path = image_source
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file '{image_path}' not found.")
        
        # Upload to Gemini
        file = genai.upload_file(image_path, mime_type='image/jpeg')
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        
        # Clean up temporary file if it was downloaded
        if parsed.scheme and parsed.netloc:
            os.unlink(image_path)
            
        return file
        
    except Exception as e:
        raise Exception(f"Failed to upload image: {str(e)}")

def generate_content(image_source, prompt):
    """Generate content based on the image and prompt.
    
    Args:
        image_source (str): Local file path or URL of the image
        prompt (str): Prompt for the model
        
    Returns:
        str: Generated content
    """
    try:
        # Upload the image
        file = upload_image(image_source)

        # Create the model
        model = genai.GenerativeModel(model_name='gemini-1.5-flash-8b')

        # Add instruction for clean JSON format
        full_prompt = (
            f"{prompt} "
            "Return ONLY a clean JSON string without any markdown formatting, code blocks, or special characters. "
            "The response should be a single line, directly parseable as JSON. "
            "For any fields where information is not found, use null instead of omitting the field. "
            "Always include all fields in the response: business_name, owner_name, phone_number, email, address, and any_other_details."
        )

        # Generate content
        result = model.generate_content([full_prompt, file])
        return result.text
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

@functions_framework.http
def handle_request(request):
    """HTTP Cloud Function."""
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        request_json = request.get_json()
        if not request_json or 'prompt' not in request_json or 'image_url' not in request_json:
            return ('Please provide both prompt and image_url in the request body', 400, headers)

        prompt = request_json['prompt']
        image_url = request_json['image_url']
        response = generate_content(image_url, prompt)

        # Clean any potential leftover special characters or whitespace
        response = response.strip()
        if response.startswith('```') and response.endswith('```'):
            response = response[3:-3]
        if response.startswith('json'):
            response = response[4:]
        response = response.strip()

        # Ensure we have a valid JSON string
        try:
            json.loads(response)  # Validate JSON
        except json.JSONDecodeError:
            response = json.dumps({
                "business_name": None,
                "owner_name": None,
                "phone_number": None,
                "email": None,
                "address": None,
                "any_other_details": None
            })

        return (json.dumps({'response': response}), 200, headers)

    except Exception as e:
        return (f'Error: {str(e)}', 500, headers)

if __name__ == "__main__":
    # For local testing
    image_url = "https://example.com/test.jpg"  # Replace with a real image URL for testing
    prompt = "Describe the contents of this image."
    response = generate_content(image_url, prompt)
    print(f"Test Response: {response}")
