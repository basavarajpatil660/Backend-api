import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS - only allow requests from your frontend
CORS(app, origins=['https://aifreeset.netlify.app'])

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'heic'}
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# API Keys from environment variables
PIXELCUT_API_KEY = os.getenv('PIXELCUT_API_KEY', 'sk_2d205bd00cad484db6ce55ef0f936db2')
UNWATERMARK_API_KEY = os.getenv('UNWATERMARK_API_KEY', '7RNirCJcUpnFlQu1n-WfPFZoeaxtFQm1VWj5evrPgsg')
QWEN_API_KEY = os.getenv('QWEN_API_KEY', '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')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_stream):
    """Check if file size is within limits"""
    file_stream.seek(0, 2)  # Seek to end
    size = file_stream.tell()
    file_stream.seek(0)  # Seek back to beginning
    return size <= MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_stream):
    """Check if file size is within limits"""
    file_stream.seek(0, 2)  # Seek to end
    size = file_stream.tell()
    file_stream.seek(0)  # Seek back to beginning
    return size <= MAX_FILE_SIZE

def validate_image_upload(request):
    """Validate uploaded image file"""
    if 'image' not in request.files:
        return None, {'success': False, 'error': 'No image file provided'}
    
    file = request.files['image']
    if file.filename == '':
        return None, {'success': False, 'error': 'No image file selected'}
    
    if not allowed_file(file.filename):
        return None, {'success': False, 'error': 'Invalid file type. Allowed: JPG, PNG, WEBP, HEIC'}
    
    if not validate_file_size(file.stream):
        return None, {'success': False, 'error': 'File size exceeds 10MB limit'}
    
    return file, None

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'AiFreeSet backend running'
    })

@app.route('/api/upscale', methods=['POST'])
def upscale_image():
    """Upscale image using Pixelcut API"""
    try:
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        # Prepare the request to Pixelcut API
        files = {'image': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': f'Bearer {PIXELCUT_API_KEY}'}
        
        # Make request to Pixelcut upscale endpoint
        response = requests.post(
            'https://api.pixelcut.ai/v1/upscale',
            files=files,
            headers=headers,
            data={'scale': '2'}  # 2x upscale by default
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'output_url': result.get('output_url', result.get('result_url'))
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Pixelcut API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'API request failed: {str(e)}'
        }), 500

@app.route('/api/unblur', methods=['POST'])
def unblur_image():
    """Enhance/sharpen image using Pixelcut API"""
    try:
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        # Prepare the request to Pixelcut API
        files = {'image': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': f'Bearer {PIXELCUT_API_KEY}'}
        
        # Make request to Pixelcut enhance endpoint
        response = requests.post(
            'https://api.pixelcut.ai/v1/enhance',
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'output_url': result.get('output_url', result.get('result_url'))
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Pixelcut API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'API request failed: {str(e)}'
        }), 500

@app.route('/api/background-remove', methods=['POST'])
def remove_background():
    """Remove background using Pixelcut API"""
    try:
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        # Prepare the request to Pixelcut API
        files = {'image': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': f'Bearer {PIXELCUT_API_KEY}'}
        
        # Make request to Pixelcut background removal endpoint
        response = requests.post(
            'https://api.pixelcut.ai/v1/remove-background',
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'output_url': result.get('output_url', result.get('result_url'))
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Pixelcut API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'API request failed: {str(e)}'
        }), 500

@app.route('/api/watermark-remove', methods=['POST'])
def remove_watermark():
    """Remove watermark using Unwatermark.ai API"""
    try:
        file, error = validate_image_upload(request)
        if error:
            return jsonify(error), 400
        
        # Prepare the request to Unwatermark.ai API
        files = {'image': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': f'Bearer {UNWATERMARK_API_KEY}'}
        
        # Make request to Unwatermark.ai API
        response = requests.post(
            'https://api.unwatermark.ai/v1/remove',
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'output_url': result.get('output_url', result.get('result_url'))
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Unwatermark API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'API request failed: {str(e)}'
        }), 500

@app.route('/api/ai-art', methods=['POST'])
def generate_ai_art():
    """Generate AI art using Qwen 3 API"""
    app.logger.info("=== AI ART GENERATION REQUEST STARTED ===")
    
    try:
        # Validate API key
        if not QWEN_API_KEY:
            app.logger.error("Qwen API key not found")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            app.logger.warning("No prompt provided in request")
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            app.logger.warning("Empty prompt provided")
            return jsonify({
                'success': False,
                'error': 'Prompt cannot be empty'
            }), 400
        
        app.logger.info(f"Generating AI art with prompt: {prompt[:100]}...")
        
        # Try OpenAI-compatible endpoint
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
        
        # Make request with timeout
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers=headers,
            json=payload,
            timeout=120  # 2 minute timeout for image generation
        )
        
        app.logger.info(f"OpenAI API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            app.logger.info(f"OpenAI API success. Response keys: {list(result.keys())}")
            
            if 'data' in result and len(result['data']) > 0:
                output_url = result['data'][0]['url']
                return jsonify({
                    'success': True,
                    'output_url': output_url
                })
            else:
                app.logger.error(f"No image data in response: {result}")
                return jsonify({
                    'success': False,
                    'error': 'No image generated'
                }), 500
        else:
            error_text = response.text
            app.logger.error(f"OpenAI API error {response.status_code}: {error_text}")
            return jsonify({
                'success': False,
                'error': f'AI API error: {response.status_code} - {error_text}'
            }), 500
            
    except requests.exceptions.Timeout:
        app.logger.error("Request timeout to AI API")
        return jsonify({
            'success': False,
            'error': 'Request timeout - AI generation took too long'
        }), 500
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Network error: {str(e)}'
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in AI art generation: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API request failed: {str(e)}'
        }), 500

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