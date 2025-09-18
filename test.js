const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const BASE_URL = process.env.TEST_URL || 'http://localhost:5000';

console.log(`🧪 Testing AiFreeSet Backend at: ${BASE_URL}`);

// Test health check
async function testHealthCheck() {
  try {
    console.log('\n1. Testing health check...');
    const response = await axios.get(`${BASE_URL}/`);
    console.log('✅ Health check passed:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return false;
  }
}

// Test text generation
async function testTextGeneration() {
  try {
    console.log('\n2. Testing text generation...');
    const response = await axios.post(`${BASE_URL}/api/text`, {
      prompt: 'Write a short poem about artificial intelligence',
      max_tokens: 100,
      temperature: 0.7
    });
    console.log('✅ Text generation passed:', {
      success: response.data.success,
      textLength: response.data.data?.text?.length || 0,
      source: response.data.source || 'api'
    });
    return true;
  } catch (error) {
    console.error('❌ Text generation failed:', error.message);
    return false;
  }
}

// Test image generation
async function testImageGeneration() {
  try {
    console.log('\n3. Testing image generation...');
    const response = await axios.post(`${BASE_URL}/api/image`, {
      prompt: 'A beautiful sunset over mountains',
      size: '1024*1024'
    });
    console.log('✅ Image generation passed:', {
      success: response.data.success,
      hasImageUrl: !!response.data.data?.image_url,
      source: response.data.source || 'api'
    });
    return true;
  } catch (error) {
    console.error('❌ Image generation failed:', error.message);
    return false;
  }
}

// Test background removal (requires test image)
async function testBackgroundRemoval() {
  try {
    console.log('\n4. Testing background removal...');
    
    // Create a simple test image buffer (1x1 PNG)
    const testImageBuffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAQhRetQAAAABJRU5ErkJggg==', 'base64');
    
    const formData = new FormData();
    formData.append('image', testImageBuffer, {
      filename: 'test.png',
      contentType: 'image/png'
    });

    const response = await axios.post(`${BASE_URL}/api/background-remove`, formData, {
      headers: formData.getHeaders()
    });
    
    console.log('✅ Background removal passed:', {
      success: response.data.success,
      hasResultUrl: !!response.data.data?.result_url,
      source: response.data.source || 'api'
    });
    return true;
  } catch (error) {
    console.error('❌ Background removal failed:', error.message);
    return false;
  }
}

// Test watermark removal (requires test image)
async function testWatermarkRemoval() {
  try {
    console.log('\n5. Testing watermark removal...');
    
    // Create a simple test image buffer (1x1 PNG)
    const testImageBuffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAQhRetQAAAABJRU5ErkJggg==', 'base64');
    
    const formData = new FormData();
    formData.append('image', testImageBuffer, {
      filename: 'test.png',
      contentType: 'image/png'
    });

    const response = await axios.post(`${BASE_URL}/api/watermark-remove`, formData, {
      headers: formData.getHeaders()
    });
    
    console.log('✅ Watermark removal passed:', {
      success: response.data.success,
      hasResultUrl: !!response.data.data?.result_url,
      source: response.data.source || 'api'
    });
    return true;
  } catch (error) {
    console.error('❌ Watermark removal failed:', error.message);
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting comprehensive backend tests...\n');
  
  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'Text Generation', fn: testTextGeneration },
    { name: 'Image Generation', fn: testImageGeneration },
    { name: 'Background Removal', fn: testBackgroundRemoval },
    { name: 'Watermark Removal', fn: testWatermarkRemoval }
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    const result = await test.fn();
    if (result) {
      passed++;
    } else {
      failed++;
    }
    
    // Add delay between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n📊 Test Results Summary:');
  console.log(`✅ Passed: ${passed}/${tests.length}`);
  console.log(`❌ Failed: ${failed}/${tests.length}`);
  
  if (failed === 0) {
    console.log('🎉 All tests passed! Backend is ready for deployment.');
  } else {
    console.log('⚠️  Some tests failed. Check the error messages above.');
  }
}

// Export for programmatic use
module.exports = {
  testHealthCheck,
  testTextGeneration,
  testImageGeneration,
  testBackgroundRemoval,
  testWatermarkRemoval,
  runAllTests
};

// Run tests if called directly
if (require.main === module) {
  runAllTests().catch(console.error);
}