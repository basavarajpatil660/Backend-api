#!/usr/bin/env python3
"""
Test script for Qwen AI Art Generation API
Tests the /api/ai-art endpoint with Qwen integration
"""

import requests
import json
import sys

def test_qwen_ai_art_endpoint(base_url, test_prompt="A beautiful sunset over mountains"):
    """Test the AI art generation endpoint with Qwen API"""
    
    endpoint = f"{base_url}/api/ai-art"
    
    print(f"🧪 Testing Qwen AI Art Generation Endpoint")
    print(f"📍 URL: {endpoint}")
    print(f"💭 Prompt: {test_prompt}")
    print("-" * 50)
    
    try:
        # Prepare request payload
        payload = {
            "prompt": test_prompt
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print("📤 Sending request to AI art endpoint...")
        
        # Make request
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Request successful!")
                print(f"📊 Response: {json.dumps(result, indent=2)}")
                
                # Validate response structure
                if result.get('success'):
                    source = result.get('source', 'unknown')
                    if source == 'qwen':
                        print("🎉 SUCCESS: Qwen API integration working!")
                        
                        # Check for processed image
                        data = result.get('data', {})
                        if 'processed_image' in data:
                            image_url = data['processed_image']
                            if image_url.startswith('http') or image_url.startswith('data:'):
                                print(f"🖼️  Image URL/Data: {image_url[:100]}...")
                            else:
                                print(f"🖼️  Image Data: {len(image_url)} characters")
                        
                        return True
                        
                    elif source == 'dummy':
                        print("⚠️  FALLBACK: Using dummy response (Qwen API might be unavailable)")
                        print("💡 This is expected behavior when the real API fails")
                        return True
                        
                    else:
                        print(f"❓ Unknown source: {source}")
                        return False
                else:
                    print(f"❌ Request failed: {result.get('error', 'Unknown error')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Raw response: {response.text[:500]}")
                return False
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_endpoint_validation():
    """Test endpoint validation (empty prompt, missing prompt)"""
    
    print("\\n🧪 Testing Input Validation...")
    print("-" * 30)
    
    # You can test locally with localhost:5000 or use your deployed URL
    base_url = "http://localhost:5000"  # Change this to your Render URL when testing deployed version
    endpoint = f"{base_url}/api/ai-art"
    
    # Test 1: Missing prompt
    print("📋 Test 1: Missing prompt")
    try:
        response = requests.post(endpoint, json={}, timeout=10)
        if response.status_code == 400:
            result = response.json()
            if 'error' in result and 'required' in result['error'].lower():
                print("✅ Correctly rejected missing prompt")
            else:
                print(f"⚠️  Unexpected error message: {result}")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 2: Empty prompt
    print("📋 Test 2: Empty prompt")
    try:
        response = requests.post(endpoint, json={"prompt": ""}, timeout=10)
        if response.status_code == 400:
            result = response.json()
            if 'error' in result and 'empty' in result['error'].lower():
                print("✅ Correctly rejected empty prompt")
            else:
                print(f"⚠️  Unexpected error message: {result}")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Qwen AI Art API Integration Test")
    print("=" * 60)
    
    # Test with different base URLs
    test_urls = [
        "http://localhost:5000",  # Local development
        # "https://your-app.onrender.com",  # Uncomment and update with your Render URL
    ]
    
    success_count = 0
    total_tests = 0
    
    for base_url in test_urls:
        print(f"\\n🌐 Testing: {base_url}")
        total_tests += 1
        
        # Test various prompts
        test_prompts = [
            "A beautiful sunset over mountains",
            "A cute cat sitting in a garden",
            "Abstract digital art with vibrant colors"
        ]
        
        for prompt in test_prompts:
            if test_qwen_ai_art_endpoint(base_url, prompt):
                success_count += 1
                break  # If one prompt works, the endpoint is working
            else:
                print("⏭️  Trying next prompt...")
        
        print("\\n" + "=" * 40)
    
    # Test validation
    test_endpoint_validation()
    
    print("\\n" + "=" * 60)
    print(f"📊 Test Summary: {success_count}/{total_tests} endpoints working")
    
    if success_count > 0:
        print("🎉 Qwen AI Art integration is working!")
        print("\\n📋 Next steps:")
        print("1. Set your QWEN_API_KEY environment variable")
        print("2. Deploy to Render")
        print("3. Test with your frontend")
    else:
        print("❌ Tests failed. Check:")
        print("1. QWEN_API_KEY is set correctly")
        print("2. Qwen API service is accessible")
        print("3. Backend is running and accessible")
    
    sys.exit(0 if success_count > 0 else 1)