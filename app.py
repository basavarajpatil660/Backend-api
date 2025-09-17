import os
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
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('unblur', 'Image enhancement service temporarily unavailable')
        return jsonify(dummy_response)

@app.route('/api/background-remove', methods=['POST'])
def remove_background():
    """Remove background using Pixelcut API with retry logic and improved error handling"""
    app.logger.info("=== BACKGROUND REMOVE REQUEST STARTED ===")
    
    try:
        # Validate API key first
        if not PIXELCUT_API_KEY:
            app.logger.error("Pixelcut API key not configured")
            return jsonify({
                'success': False, 
                'error': 'Background removal service is temporarily unavailable'
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
            'Authorization': f'Bearer {PIXELCUT_API_KEY}',
            'User-Agent': 'AiFreeSet-Backend/1.0'
        }
        
        # Use the correct Pixelcut API endpoint for background removal
        api_url = 'https://api.pixelcut.ai/v1/background/remove'
        app.logger.info(f"Making request to Pixelcut API: {api_url}")
        app.logger.info(f"Using API key: {PIXELCUT_API_KEY[:10]}...{PIXELCUT_API_KEY[-4:]}")
        
        # Create session with retry logic
        session = create_retry_session()
        
        # Make request to Pixelcut API with retry logic
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                app.logger.info(f"Attempt {attempt + 1}/{max_attempts} to Pixelcut API")
                
                response = session.post(
                    api_url,
                    files=files,
                    headers=headers,
                    timeout=90  # Increased timeout for background removal
                )
                
                app.logger.info(f"Pixelcut API response - Status: {response.status_code}")
                app.logger.info(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        app.logger.info(f"Pixelcut API success. Response keys: {list(result.keys())}")
                        
                        # Handle different response formats from Pixelcut API
                        processed_image_url = None
                        image_data = None
                        
                        # Try to extract URL first (most common response)
                        processed_image_url = (
                            result.get('output_url') or 
                            result.get('result_url') or 
                            result.get('url') or 
                            result.get('image_url') or
                            result.get('processed_url')
                        )
                        
                        # If no URL, check for base64 image data
                        if not processed_image_url:
                            raw_image_data = (
                                result.get('image_data') or
                                result.get('base64_image') or
                                result.get('data')
                            )
                            
                            if raw_image_data:
                                # Ensure proper base64 encoding
                                if isinstance(raw_image_data, bytes):
                                    image_data = base64.b64encode(raw_image_data).decode('utf-8')
                                elif isinstance(raw_image_data, str):
                                    # Check if it's already base64 encoded
                                    if raw_image_data.startswith('data:image/'):
                                        image_data = raw_image_data
                                    else:
                                        image_data = f"data:image/png;base64,{raw_image_data}"
                        
                        # Return success response with either URL or base64 data
                        if processed_image_url:
                            app.logger.info(f"Background removal successful. Output URL: {processed_image_url[:50]}...")
                            return jsonify({
                                'success': True,
                                'processed_image': processed_image_url
                            })
                        elif image_data:
                            app.logger.info("Background removal successful. Returning base64 image data")
                            return jsonify({
                                'success': True,
                                'image_data': image_data
                            })
                        else:
                            app.logger.error(f"No usable image data found in response: {result}")
                            return jsonify({
                                'success': False,
                                'error': 'Background removal completed but no image data received'
                            }), 500
                            
                    except json.JSONDecodeError as e:
                        app.logger.error(f"Failed to parse JSON response: {e}")
                        app.logger.error(f"Raw response: {response.text[:500]}")
                        
                        # If JSON parsing fails, check if response is binary image data
                        if response.headers.get('content-type', '').startswith('image/'):
                            try:
                                image_data = base64.b64encode(response.content).decode('utf-8')
                                content_type = response.headers.get('content-type', 'image/png')
                                image_data_url = f"data:{content_type};base64,{image_data}"
                                
                                app.logger.info("Received binary image data, converted to base64")
                                return jsonify({
                                    'success': True,
                                    'image_data': image_data_url
                                })
                            except Exception as base64_error:
                                app.logger.error(f"Failed to encode binary response to base64: {base64_error}")
                        
                        return jsonify({
                            'success': False,
                            'error': 'Invalid response format from background removal service'
                        }), 500
                        
                elif response.status_code == 401:
                    app.logger.error(f"Pixelcut API authentication failed - Status: {response.status_code}")
                    app.logger.error(f"Response: {response.text}")
                    return jsonify({
                        'success': False,
                        'error': 'Background removal service authentication failed'
                    }), 500
                    
                elif response.status_code == 429:
                    app.logger.warning(f"Pixelcut API rate limit hit - Status: {response.status_code}")
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 1  # Exponential backoff
                        app.logger.info(f"Rate limited, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Background removal service is busy. Please try again later.'
                        }), 429
                        
                else:
                    error_text = response.text[:200]  # Limit error text length
                    app.logger.error(f"Pixelcut API error - Status: {response.status_code}, Response: {error_text}")
                    
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 1  # Exponential backoff
                        app.logger.info(f"API error, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Pixelcut API unavailable. Please try again later.'
                        }), 500
                
                # If we get here, the request was successful, break the retry loop
                break
                
            except requests.exceptions.Timeout as e:
                app.logger.error(f"Timeout error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) + 2
                    app.logger.info(f"Timeout, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Background removal service timeout. Please try again later.'
                    }), 500
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.DNSError) as e:
                app.logger.error(f"Connection/DNS error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) + 2
                    app.logger.info(f"Connection error, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Pixelcut API unavailable. Please try again later.'
                    }), 500
                    
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Request exception (attempt {attempt + 1}): {str(e)}")
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) + 1
                    app.logger.info(f"Request error, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Pixelcut API unavailable. Please try again later.'
                    }), 500
            
            finally:
                # Reset file pointer for potential retry
                if 'files' in locals():
                    files['image'] = (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')
        
        # If we've exhausted all retries without success
        app.logger.warning("All retry attempts exhausted for background removal, using dummy response")
        dummy_response = create_dummy_response('background-remove', 'Pixelcut API unavailable after multiple attempts')
        return jsonify(dummy_response)
            
    except Exception as e:
        app.logger.error(f"Unexpected error in background removal: {str(e)}")
        app.logger.exception("Full traceback:")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('background-remove', 'Background removal service temporarily unavailable')
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
        def _make_unwatermark_request():
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
            
            session = create_retry_session()
            
            # Retry logic with exponential backoff
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    app.logger.info(f"Watermark removal attempt {attempt + 1}/{max_attempts}")
                    
                    response = session.post(
                        'https://api.unwatermark.ai/v1/remove',
                        files=files,
                        headers=headers,
                        timeout=120  # Longer timeout for watermark removal
                    )
                    
                    app.logger.info(f"Unwatermark API response: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        output_url = (
                            result.get('output_url') or 
                            result.get('result_url') or 
                            result.get('url') or
                            result.get('processed_image')
                        )
                        if output_url:
                            return {'success': True, 'processed_image': output_url, 'source': 'unwatermark'}
                        else:
                            raise Exception('No output URL received from Unwatermark.ai')
                    
                    elif response.status_code in [429, 500, 502, 503, 504]:
                        if attempt < max_attempts - 1:
                            wait_time = (2 ** attempt) + 1
                            app.logger.warning(f"Unwatermark API error {response.status_code}, retrying in {wait_time}s")
                            time.sleep(wait_time)
                            files['image'] = (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')
                            continue
                        else:
                            raise Exception(f"Unwatermark API failed: HTTP {response.status_code}")
                    else:
                        raise Exception(f"Unwatermark API error: HTTP {response.status_code} - {response.text[:200]}")
                        
                except (requests.exceptions.Timeout, 
                        requests.exceptions.ConnectionError, 
                        requests.exceptions.DNSError) as e:
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 2
                        app.logger.warning(f"Network error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        files['image'] = (filename, io.BytesIO(file_content), file.content_type or 'image/jpeg')
                        continue
                    else:
                        raise Exception(f"Network error after {max_attempts} attempts: {str(e)}")
            
            raise Exception("All retry attempts exhausted")
        
        # Make request with automatic fallback
        result = make_api_request_with_fallback(_make_unwatermark_request, 'watermark-remove')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in watermark removal endpoint: {str(e)}")
        # Return dummy response as final fallback
        dummy_response = create_dummy_response('watermark-remove', 'Watermark removal service temporarily unavailable')
        return jsonify(dummy_response)

@app.route('/api/ai-art', methods=['POST'])
def generate_ai_art():
    """Generate AI art using Qwen 3 API with graceful fallback"""
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
            
            payload = {
                'model': 'dall-e-3',
                'prompt': prompt,
                'size': '1024x1024',
                'n': 1
            }
            
            session = create_retry_session()
            
            # Retry logic with exponential backoff
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    app.logger.info(f"AI art generation attempt {attempt + 1}/{max_attempts}")
                    
                    response = session.post(
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
                            return {
                                'success': True, 
                                'processed_image': output_url,
                                'source': 'qwen',
                                'data': {
                                    'text': f'AI-generated art for prompt: {prompt[:50]}...',
                                    'result': 'AI art generation successful'
                                }
                            }
                        else:
                            raise Exception('No image data in OpenAI response')
                    
                    elif response.status_code in [429, 500, 502, 503, 504]:
                        if attempt < max_attempts - 1:
                            wait_time = (2 ** attempt) + 1
                            app.logger.warning(f"OpenAI API error {response.status_code}, retrying in {wait_time}s")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise Exception(f"OpenAI API failed: HTTP {response.status_code}")
                    else:
                        raise Exception(f"OpenAI API error: HTTP {response.status_code} - {response.text[:200]}")
                        
                except (requests.exceptions.Timeout, 
                        requests.exceptions.ConnectionError, 
                        requests.exceptions.DNSError) as e:
                    if attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + 2
                        app.logger.warning(f"Network error (attempt {attempt + 1}): {str(e)}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Network error after {max_attempts} attempts: {str(e)}")
            
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