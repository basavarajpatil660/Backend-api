#!/usr/bin/env python3
"""
Test script to verify the two critical fixes:
1. method_whitelist -> allowed_methods in urllib3 Retry
2. create_dummy_response function implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_create_retry_session():
    """Test that create_retry_session uses allowed_methods instead of method_whitelist"""
    try:
        from app import create_retry_session
        session = create_retry_session()
        print("✅ create_retry_session() works - urllib3 Retry fix successful")
        return True
    except Exception as e:
        print(f"❌ create_retry_session() failed: {e}")
        return False

def test_create_dummy_response():
    """Test that create_dummy_response function exists and returns correct format"""
    try:
        from app import create_dummy_response
        
        # Test all endpoint types
        endpoints = ['background-remove', 'upscale', 'unblur', 'watermark-remove', 'ai-art']
        
        for endpoint in endpoints:
            response = create_dummy_response(endpoint)
            
            # Verify response structure
            assert response['success'] == True
            assert response['source'] == 'dummy'
            assert 'error' in response
            assert 'data' in response
            assert 'processed_image' in response['data']
            assert 'result' in response['data']
            
            print(f"✅ create_dummy_response('{endpoint}') works correctly")
        
        return True
    except Exception as e:
        print(f"❌ create_dummy_response() failed: {e}")
        return False

def test_dummy_response_format():
    """Test that dummy responses match the required format"""
    try:
        from app import create_dummy_response
        
        response = create_dummy_response('background-remove', 'Test message')
        
        expected_keys = ['success', 'source', 'error', 'data']
        for key in expected_keys:
            assert key in response, f"Missing key: {key}"
        
        assert response['success'] == True
        assert response['source'] == 'dummy'
        assert response['error'] == 'Test message'
        assert 'processed_image' in response['data']
        
        print("✅ Dummy response format matches requirements")
        return True
    except Exception as e:
        print(f"❌ Dummy response format test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Flask app fixes...")
    print("=" * 50)
    
    tests = [
        test_create_retry_session,
        test_create_dummy_response, 
        test_dummy_response_format
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All fixes working correctly!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)