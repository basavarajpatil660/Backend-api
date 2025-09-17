import os
import json
import requests
import logging
import sys
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure detailed logging for production debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
app.logger.setLevel(logging.INFO)

# Configure CORS - only allow requests from your frontend
CORS(app, origins=['https://aifreeset.netlify.app'])

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'heic'}
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# API Keys from environment variables with proper validation
PIXELCUT_API_KEY = os.getenv('PIXELCUT_API_KEY', 'sk_2d205bd00cad484db6ce55ef0f936db2')
UNWATERMARK_API_KEY = os.getenv('UNWATERMARK_API_KEY', '7RNirCJcUpnFlQu1n-WfPFZoeaxtFQm1VWj5evrPgsg')
QWEN_API_KEY = os.getenv('QWEN_API_KEY', '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')

# Log API key status at startup (without exposing actual keys)
app.logger.info("=== API KEYS STATUS ===")
app.logger.info(f"Pixelcut API Key: {'✓ Loaded' if PIXELCUT_API_KEY else '✗ Missing'}")
app.logger.info(f"Unwatermark API Key: {'✓ Loaded' if UNWATERMARK_API_KEY else '✗ Missing'}")
app.logger.info(f"Qwen API Key: {'✓ Loaded' if QWEN_API_KEY else '✗ Missing'}")
app.logger.info("=========================")

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def validate_image_upload(request):
    """Validate uploaded image file with comprehensive logging"""
    app.logger.info("Starting file validation...")
    
    # Check if file is in request
    if 'image' not in request.files:
        app.logger.warning("No 'image' field in request files")
        return None, {'success': False, 'error': 'No image file provided'}
    
    file = request.files['image']
    
    # Check if file was selected
    if file.filename == '' or not file.filename:
        app.logger.warning("Empty filename provided")
        return None, {'success': False, 'error': 'No image file selected'}
    
    # Log file details
    filename = secure_filename(file.filename)
    app.logger.info(f"File received: {filename}")
    app.logger.info(f"Content-Type: {file.content_type}")
    
    # Validate file type
    if not allowed_file(filename):
        app.logger.warning(f"Invalid file type: {filename}")
        return None, {
            'success': False, 
            'error': 'Unsupported file type. Allowed: JPG, PNG, WEBP, HEIC'
        }
    
    # Check file size by reading content
    file.seek(0)
    file_content = file.read()
    file_size = len(file_content)
    
    app.logger.info(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
    
    if file_size > MAX_FILE_SIZE:
        app.logger.warning(f"File too large: {file_size} bytes")
        return None, {
            'success': False, 
            'error': 'File size exceeds 10MB limit'
        }
    
    if file_size == 0:
        app.logger.warning("Empty file received")
        return None, {
            'success': False, 
            'error': 'Empty file received'
        }
    
    # Reset file pointer and return file with content
    file.seek(0)
    app.logger.info("File validation successful")
    return file, None

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint with API status"""
    app.logger.info("Health check requested")
    return jsonify({
        'status': 'AiFreeSet backend running',
        'api_keys_loaded': {
            'pixelcut': bool(PIXELCUT_API_KEY),
            'unwatermark': bool(UNWATERMARK_API_KEY),
            'qwen': bool(QWEN_API_KEY)
        }
    })

@app.route('/api/upscale', methods=['POST'])
def upscale_image():
    """Upscale image using Pixelcut API with detailed logging"""
    app.logger.info("=== UPSCALE REQUEST STARTED ===")
    
    try:
        if not PIXELCUT_API_KEY:
            app.logger.error("Pixelcut API key not configured")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        file.seek(0)
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        app.logger.info(f"Processing upscale for: {filename}")
        
        files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
        headers = {'Authorization': f'Bearer {PIXELCUT_API_KEY}'}
        
        response = requests.post(
            'https://api.pixelcut.ai/v1/upscale',
            files=files,
            headers=headers,
            data={'scale': '2'},
            timeout=60
        )
        
        app.logger.info(f"Pixelcut upscale response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            output_url = result.get('output_url') or result.get('result_url') or result.get('url')
            if output_url:
                return jsonify({'success': True, 'output_url': output_url})
            else:
                return jsonify({'success': False, 'error': 'No output URL received'}), 500
        else:
            app.logger.error(f"Pixelcut API error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': f'Upscale failed: HTTP {response.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timeout'}), 500
    except Exception as e:
        app.logger.error(f"Upscale error: {str(e)}")
        return jsonify({'success': False, 'error': f'API request failed: {str(e)}'}), 500

@app.route('/api/unblur', methods=['POST'])
def unblur_image():
    """Enhance/sharpen image using Pixelcut API with detailed logging"""
    app.logger.info("=== UNBLUR REQUEST STARTED ===")
    
    try:
        if not PIXELCUT_API_KEY:
            app.logger.error("Pixelcut API key not configured")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        file.seek(0)
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        app.logger.info(f"Processing unblur for: {filename}")
        
        files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
        headers = {'Authorization': f'Bearer {PIXELCUT_API_KEY}'}
        
        response = requests.post(
            'https://api.pixelcut.ai/v1/enhance',
            files=files,
            headers=headers,
            timeout=60
        )
        
        app.logger.info(f"Pixelcut unblur response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            output_url = result.get('output_url') or result.get('result_url') or result.get('url')
            if output_url:
                return jsonify({'success': True, 'output_url': output_url})
            else:
                return jsonify({'success': False, 'error': 'No output URL received'}), 500
        else:
            app.logger.error(f"Pixelcut API error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': f'Unblur failed: HTTP {response.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timeout'}), 500
    except Exception as e:
        app.logger.error(f"Unblur error: {str(e)}")
        return jsonify({'success': False, 'error': f'API request failed: {str(e)}'}), 500

@app.route('/api/background-remove', methods=['POST'])
def remove_background():
    """Remove background using Pixelcut API with detailed logging"""
    app.logger.info("=== BACKGROUND REMOVE REQUEST STARTED ===")
    
    try:
        # Validate API key first
        if not PIXELCUT_API_KEY:
            app.logger.error("Pixelcut API key not configured")
            return jsonify({
                'success': False, 
                'error': 'API key not configured'
            }), 500
        
        # Validate file upload
        file, error = validate_image_upload(request)
        if error:
            app.logger.error(f"File validation failed: {error}")
            return jsonify(error), 400
        
        # Read file content into memory
        file.seek(0)
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        app.logger.info(f"Processing background removal for: {filename}")
        app.logger.info(f"File content loaded: {len(file_content)} bytes")
        
        # Prepare multipart form data
        files = {
            'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')
        }
        
        headers = {
            'Authorization': f'Bearer {PIXELCUT_API_KEY}'
        }
        
        app.logger.info("Making request to Pixelcut background removal API...")
        app.logger.info(f"Request URL: https://api.pixelcut.ai/v1/remove-background")
        app.logger.info(f"Headers: Authorization: Bearer [HIDDEN]")
        
        # Make request to Pixelcut API with proper error handling
        try:
            response = requests.post(
                'https://api.pixelcut.ai/v1/remove-background',
                files=files,
                headers=headers,
                timeout=60  # 60 second timeout
            )
            
            app.logger.info(f"Pixelcut API response status: {response.status_code}")
            app.logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    app.logger.info(f"Pixelcut API success. Response keys: {list(result.keys())}")
                    
                    # Extract output URL with multiple fallbacks
                    output_url = (
                        result.get('output_url') or 
                        result.get('result_url') or 
                        result.get('url') or 
                        result.get('image_url')
                    )
                    
                    if output_url:
                        app.logger.info(f"Background removal successful. Output URL: {output_url[:50]}...")
                        return jsonify({
                            'success': True,
                            'output_url': output_url
                        })
                    else:
                        app.logger.error(f"No output URL found in response: {result}")
                        return jsonify({
                            'success': False,
                            'error': 'No output URL received from API'
                        }), 500
                        
                except json.JSONDecodeError as e:
                    app.logger.error(f"Failed to parse JSON response: {e}")
                    app.logger.error(f"Raw response: {response.text[:500]}")
                    return jsonify({
                        'success': False,
                        'error': 'Invalid JSON response from API'
                    }), 500
                    
            else:
                error_text = response.text
                app.logger.error(f"Pixelcut API error {response.status_code}: {error_text}")
                return jsonify({
                    'success': False,
                    'error': f'Background removal failed: HTTP {response.status_code} - {error_text}'
                }), 500
                
        except requests.exceptions.Timeout:
            app.logger.error("Request timeout to Pixelcut API")
            return jsonify({
                'success': False,
                'error': 'Request timeout - API took too long to respond'
            }), 500
            
        except requests.exceptions.ConnectionError as e:
            app.logger.error(f"Connection error to Pixelcut API: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to connect to background removal API'
            }), 500
            
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Request exception: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Network error: {str(e)}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Unexpected error in background removal: {str(e)}")
        app.logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/watermark-remove', methods=['POST'])
def remove_watermark():
    """Remove watermark using Unwatermark.ai API with detailed logging"""
    app.logger.info("=== WATERMARK REMOVE REQUEST STARTED ===")
    
    try:
        if not UNWATERMARK_API_KEY:
            app.logger.error("Unwatermark API key not configured")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        file.seek(0)
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        app.logger.info(f"Processing watermark removal for: {filename}")
        
        files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
        headers = {'Authorization': f'Bearer {UNWATERMARK_API_KEY}'}
        
        response = requests.post(
            'https://api.unwatermark.ai/v1/remove',
            files=files,
            headers=headers,
            timeout=90  # Longer timeout for watermark removal
        )
        
        app.logger.info(f"Unwatermark API response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            output_url = result.get('output_url') or result.get('result_url') or result.get('url')
            if output_url:
                return jsonify({'success': True, 'output_url': output_url})
            else:
                return jsonify({'success': False, 'error': 'No output URL received'}), 500
        else:
            app.logger.error(f"Unwatermark API error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': f'Watermark removal failed: HTTP {response.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timeout'}), 500
    except Exception as e:
        app.logger.error(f"Watermark removal error: {str(e)}")
        return jsonify({'success': False, 'error': f'API request failed: {str(e)}'}), 500

@app.route('/api/ai-art', methods=['POST'])
def generate_ai_art():
    """Generate AI art using Qwen 3 API with detailed logging"""
    app.logger.info("=== AI ART GENERATION REQUEST STARTED ===")
    
    try:
        if not QWEN_API_KEY:
            app.logger.error("Qwen API key not configured")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            app.logger.warning("No prompt provided in request")
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            app.logger.warning("Empty prompt provided")
            return jsonify({'success': False, 'error': 'Prompt cannot be empty'}), 400
        
        app.logger.info(f"Generating AI art with prompt: {prompt[:100]}...")
        
        headers = {
            'Authorization': f'Bearer {QWEN_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'dall-e-3',
            'prompt': prompt,
            'size': '1024x1024',
            'n': 1
        }
        
        app.logger.info("Making request to OpenAI API...")
        
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers=headers,
            json=payload,
            timeout=120
        )
        
        app.logger.info(f"OpenAI API response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                output_url = result['data'][0]['url']
                app.logger.info("AI art generation successful")
                return jsonify({'success': True, 'output_url': output_url})
            else:
                app.logger.error(f"No image data in response: {result}")
                return jsonify({'success': False, 'error': 'No image generated'}), 500
        else:
            app.logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': f'AI generation failed: HTTP {response.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        app.logger.error("Request timeout to AI API")
        return jsonify({'success': False, 'error': 'Request timeout - AI generation took too long'}), 500
    except Exception as e:
        app.logger.error(f"AI art generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'API request failed: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File size exceeds 10MB limit'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)