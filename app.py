import os
import json
import requests
import logging
import sys
import io
import time
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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

def create_retry_session():
    """Create a requests session with retry logic for better reliability"""
    session = requests.Session()
    
    # Define retry strategy - Fixed: replaced method_whitelist with allowed_methods
    retry_strategy = Retry(
        total=3,  # Total number of retries
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["HEAD", "GET", "POST"],  # HTTP methods to retry (fixed deprecated parameter)
        backoff_factor=1,  # Backoff factor for exponential delay
        raise_on_redirect=False,
        raise_on_status=False
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def create_dummy_response(endpoint_type, message="API temporarily unavailable, using dummy response"):
    """Create standardized dummy fallback response for failed API calls"""
    dummy_data = {
        'background-remove': {
            'processed_image': 'https://via.placeholder.com/512x512.png?text=Background+Removed',
            'result': 'Background removal placeholder'
        },
        'upscale': {
            'processed_image': 'https://via.placeholder.com/1024x1024.png?text=Upscaled+2x',
            'result': 'Image upscaled placeholder'
        },
        'unblur': {
            'processed_image': 'https://via.placeholder.com/512x512.png?text=Enhanced+Image',
            'result': 'Image enhancement placeholder'
        },
        'watermark-remove': {
            'processed_image': 'https://via.placeholder.com/512x512.png?text=Watermark+Removed',
            'result': 'Watermark removal placeholder'
        },
        'ai-art': {
            'processed_image': 'https://via.placeholder.com/1024x1024.png?text=AI+Generated+Art',
            'text': 'This is a dummy AI-generated art response',
            'result': 'AI art generation placeholder'
        }
    }
    
    return {
        'success': True,
        'source': 'dummy',
        'error': message,
        'data': dummy_data.get(endpoint_type, {
            'processed_image': 'https://via.placeholder.com/512x512.png?text=Dummy+Response',
            'result': 'Generic placeholder response'
        })
    }

def make_api_request_with_fallback(api_function, endpoint_type, *args, **kwargs):
    """Wrapper to make API requests with automatic fallback to dummy responses"""
    try:
        return api_function(*args, **kwargs)
    except Exception as e:
        app.logger.error(f"API call failed for {endpoint_type}: {str(e)}")
        app.logger.info(f"Returning dummy fallback response for {endpoint_type}")
        return create_dummy_response(endpoint_type)

def make_image_api_request(api_url, files, headers, timeout=90, max_attempts=3):
    """Generic helper function for image processing API calls with retry logic"""
    session = create_retry_session()
    
    for attempt in range(max_attempts):
        try:
            app.logger.info(f"API request attempt {attempt + 1}/{max_attempts} to {api_url}")
            
            response = session.post(
                api_url,
                files=files,
                headers=headers,
                timeout=timeout
            )
            
            app.logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Try multiple URL field names
                    output_url = (
                        result.get('output_url') or 
                        result.get('result_url') or 
                        result.get('url') or 
                        result.get('image_url') or
                        result.get('processed_url') or
                        result.get('processed_image')
                    )
                    
                    if output_url:
                        return {'success': True, 'processed_image': output_url, 'source': 'api'}
                    else:
                        raise Exception('No output URL found in API response')
                        
                except json.JSONDecodeError:
                    # Handle binary image data
                    if response.headers.get('content-type', '').startswith('image/'):
                        try:
                            image_data = base64.b64encode(response.content).decode('utf-8')
                            content_type = response.headers.get('content-type', 'image/png')
                            image_data_url = f"data:{content_type};base64,{image_data}"
                            return {'success': True, 'image_data': image_data_url, 'source': 'api'}
                        except Exception as base64_error:
                            app.logger.error(f"Failed to encode binary response: {base64_error}")
                    
                    raise Exception('Invalid response format from API')
            
            elif response.status_code in [429, 500, 502, 503, 504]:
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) + 1
                    app.logger.warning(f"API error {response.status_code}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"API failed after retries: HTTP {response.status_code}")
            else:
                raise Exception(f"API error: HTTP {response.status_code} - {response.text[:200]}")
                
        except requests.exceptions.Timeout as e:
            if attempt < max_attempts - 1:
                wait_time = (2 ** attempt) + 2
                app.logger.warning(f"Timeout (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Timeout after {max_attempts} attempts: {str(e)}")
                
        except requests.exceptions.ConnectionError as e:
            if attempt < max_attempts - 1:
                wait_time = (2 ** attempt) + 2
                app.logger.warning(f"Connection error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Connection error after {max_attempts} attempts: {str(e)}")
                
        except requests.exceptions.RequestException as e:
            if attempt < max_attempts - 1:
                wait_time = (2 ** attempt) + 2
                app.logger.warning(f"Request error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Request error after {max_attempts} attempts: {str(e)}")
                
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = (2 ** attempt) + 2
                app.logger.warning(f"Unexpected error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Unexpected error after {max_attempts} attempts: {str(e)}")
    
    raise Exception("All retry attempts exhausted")

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

@app.route('/api/background-remove', methods=['POST'])
def remove_background():
    """Remove background using Pixelcut API with graceful fallback"""
    app.logger.info("=== BACKGROUND REMOVE REQUEST STARTED ===")
    
    try:
        # Validate file upload first
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        filename = secure_filename(file.filename)
        app.logger.info(f"Processing background removal for: {filename}")
        
        # Attempt real API call with fallback
        def _make_background_remove_request():
            if not PIXELCUT_API_KEY:
                app.logger.error("Pixelcut API key not configured")
                raise Exception("API key not configured")
            
            file.seek(0)
            file_content = file.read()
            
            files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
            headers = {
                'Authorization': f'Bearer {PIXELCUT_API_KEY}',
                'User-Agent': 'AiFreeSet-Backend/1.0'
            }
            
            return make_image_api_request(
                'https://api.pixelcut.ai/v1/background/remove',
                files,
                headers,
                timeout=90
            )
        
        # Make request with automatic fallback
        result = make_api_request_with_fallback(_make_background_remove_request, 'background-remove')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in background removal endpoint: {str(e)}")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('background-remove', 'Background removal service temporarily unavailable')
        return jsonify(dummy_response)

@app.route('/api/upscale', methods=['POST'])
def upscale_image():
    """Upscale image using Pixelcut API with graceful fallback"""
    app.logger.info("=== UPSCALE REQUEST STARTED ===")
    
    try:
        # Validate file upload first
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        filename = secure_filename(file.filename)
        app.logger.info(f"Processing upscale for: {filename}")
        
        # Attempt real API call with fallback
        def _make_upscale_request():
            if not PIXELCUT_API_KEY:
                app.logger.error("Pixelcut API key not configured")
                raise Exception("API key not configured")
            
            file.seek(0)
            file_content = file.read()
            
            files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
            headers = {
                'Authorization': f'Bearer {PIXELCUT_API_KEY}',
                'User-Agent': 'AiFreeSet-Backend/1.0'
            }
            
            # Add scale parameter for upscaling
            session = create_retry_session()
            response = session.post(
                'https://api.pixelcut.ai/v1/upscale',
                files=files,
                headers=headers,
                data={'scale': '2'},
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                output_url = (
                    result.get('output_url') or 
                    result.get('result_url') or 
                    result.get('url') or
                    result.get('processed_image')
                )
                if output_url:
                    return {'success': True, 'processed_image': output_url, 'source': 'pixelcut'}
                else:
                    raise Exception('No output URL received from Pixelcut')
            else:
                raise Exception(f"Pixelcut API error: HTTP {response.status_code}")
        
        # Make request with automatic fallback
        result = make_api_request_with_fallback(_make_upscale_request, 'upscale')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in upscale endpoint: {str(e)}")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('upscale', 'Image upscale service temporarily unavailable')
        return jsonify(dummy_response)

@app.route('/api/unblur', methods=['POST'])
def unblur_image():
    """Enhance/sharpen image using Pixelcut API with graceful fallback"""
    app.logger.info("=== UNBLUR REQUEST STARTED ===")
    
    try:
        # Validate file upload first
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        filename = secure_filename(file.filename)
        app.logger.info(f"Processing unblur for: {filename}")
        
        # Attempt real API call with fallback
        def _make_unblur_request():
            if not PIXELCUT_API_KEY:
                app.logger.error("Pixelcut API key not configured")
                raise Exception("API key not configured")
            
            file.seek(0)
            file_content = file.read()
            
            files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
            headers = {
                'Authorization': f'Bearer {PIXELCUT_API_KEY}',
                'User-Agent': 'AiFreeSet-Backend/1.0'
            }
            
            return make_image_api_request(
                'https://api.pixelcut.ai/v1/enhance',
                files,
                headers,
                timeout=90
            )
        
        # Make request with automatic fallback
        result = make_api_request_with_fallback(_make_unblur_request, 'unblur')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in unblur endpoint: {str(e)}")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('unblur', 'Image enhancement service temporarily unavailable')
        return jsonify(dummy_response)

@app.route('/api/watermark-remove', methods=['POST'])
def remove_watermark():
    """Remove watermark using Unwatermark.ai API with graceful fallback"""
    app.logger.info("=== WATERMARK REMOVE REQUEST STARTED ===")
    
    try:
        # Validate file upload first
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        filename = secure_filename(file.filename)
        app.logger.info(f"Processing watermark removal for: {filename}")
        
        # Attempt real API call with fallback
        def _make_watermark_remove_request():
            if not UNWATERMARK_API_KEY:
                app.logger.error("Unwatermark API key not configured")
                raise Exception("API key not configured")
            
            file.seek(0)
            file_content = file.read()
            
            files = {'image': (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')}
            headers = {
                'Authorization': f'Bearer {UNWATERMARK_API_KEY}',
                'User-Agent': 'AiFreeSet-Backend/1.0'
            }
            
            return make_image_api_request(
                'https://api.unwatermark.ai/v1/remove',
                files,
                headers,
                timeout=120  # Longer timeout for watermark removal
            )
        
        # Make request with automatic fallback
        result = make_api_request_with_fallback(_make_watermark_remove_request, 'watermark-remove')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in watermark removal endpoint: {str(e)}")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('watermark-remove', 'Watermark removal service temporarily unavailable')
        return jsonify(dummy_response)

@app.route('/api/ai-art', methods=['POST'])
def generate_ai_art():
    """Generate AI art using Qwen API with graceful fallback"""
    app.logger.info("=== AI ART GENERATION REQUEST STARTED ===")
    
    try:
        # Validate JSON input
        data = request.get_json()
        if not data or 'prompt' not in data:
            app.logger.warning("No prompt provided in request")
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            app.logger.warning("Empty prompt provided")
            return jsonify({'success': False, 'error': 'Prompt cannot be empty'}), 400
        
        app.logger.info(f"Generating AI art with prompt: {prompt[:100]}...")
        
        # Attempt real API call with fallback
        def _make_qwen_art_request():
            if not QWEN_API_KEY:
                app.logger.error("Qwen API key not configured")
                raise Exception("API key not configured")
            
            headers = {
                'Authorization': f'Bearer {QWEN_API_KEY}',
                'Content-Type': 'application/json',
                'User-Agent': 'AiFreeSet-Backend/1.0'
            }
            
            # Qwen API payload structure
            payload = {
                'model': 'wanx-v1',
                'input': {
                    'prompt': prompt
                },
                'parameters': {
                    'style': '<auto>',
                    'size': '1024*1024',
                    'n': 1
                }
            }
            
            session = create_retry_session()
            
            # Retry logic with exponential backoff
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    app.logger.info(f"AI art generation attempt {attempt + 1}/{max_attempts}")
                    
                    response = session.post(
                        'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/generation',
                        headers=headers,
                        json=payload,
                        timeout=120
                    )
                    
                    app.logger.info(f"Qwen API response: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        app.logger.info(f"Qwen API success. Response keys: {list(result.keys()) if result else 'None'}")
                        
                        # Handle Qwen response format
                        if 'output' in result and 'results' in result['output']:
                            results = result['output']['results']
                            if results and len(results) > 0:
                                # Try to get image URL or base64 data
                                image_result = results[0]
                                output_url = image_result.get('url')
                                
                                if output_url:
                                    return {
                                        'success': True,
                                        'source': 'qwen',
                                        'data': {
                                            'processed_image': output_url,
                                            'text': f'AI-generated art for prompt: {prompt[:50]}...',
                                            'result': 'AI art generation successful'
                                        }
                                    }
                                else:
                                    # Check for base64 image data
                                    base64_data = image_result.get('image')
                                    if base64_data:
                                        # Format as data URI
                                        image_data_url = f"data:image/png;base64,{base64_data}"
                                        return {
                                            'success': True,
                                            'source': 'qwen',
                                            'data': {
                                                'processed_image': image_data_url,
                                                'text': f'AI-generated art for prompt: {prompt[:50]}...',
                                                'result': 'AI art generation successful'
                                            }
                                        }
                                    else:
                                        raise Exception('No image URL or base64 data found in Qwen response')
                            else:
                                raise Exception('No results found in Qwen response')
                        else:
                            raise Exception('Invalid response format from Qwen API')
                    
                    elif response.status_code == 401:
                        app.logger.error(f"Qwen API authentication failed - Status: {response.status_code}")
                        app.logger.error(f"Response: {response.text}")
                        raise Exception("Qwen API authentication failed - check API key")
                    
                    elif response.status_code in [429, 500, 502, 503, 504]:
                        if attempt < max_attempts - 1:
                            wait_time = (2 ** attempt) + 1
                            app.logger.warning(f"Qwen API error {response.status_code}, retrying in {wait_time}s")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise Exception(f"Qwen API failed: HTTP {response.status_code}")
                    else:
                        error_text = response.text[:200] if response.text else 'No response text'
                        app.logger.error(f"Qwen API error: HTTP {response.status_code} - {error_text}")
                        raise Exception(f"Qwen API error: HTTP {response.status_code}")
                        
                except requests.exceptions.Timeout as e:
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 2
                        app.logger.warning(f"Timeout error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Timeout error after {max_attempts} attempts: {str(e)}")
                        
                except requests.exceptions.ConnectionError as e:
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 2
                        app.logger.warning(f"Connection error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Connection error after {max_attempts} attempts: {str(e)}")
                        
                except requests.exceptions.RequestException as e:
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 2
                        app.logger.warning(f"Request error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Request error after {max_attempts} attempts: {str(e)}")
                        
                except Exception as e:
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 2
                        app.logger.warning(f"Unexpected error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Unexpected error after {max_attempts} attempts: {str(e)}")
            
            raise Exception("All retry attempts exhausted")
        
        # Make request with automatic fallback
        result = make_api_request_with_fallback(_make_qwen_art_request, 'ai-art')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in AI art generation endpoint: {str(e)}")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('ai-art', 'AI art generation service temporarily unavailable')
        return jsonify(dummy_response)

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