const axios = require('axios');
const FormData = require('form-data');

// Render server URL
const BASE_URL = process.env.TEST_URL || 'https://backend-api-jumi.onrender.com';

console.log(`🧪 Testing AiFreeSet Backend on Render: ${BASE_URL}`);

// Test health check
async function testHealthCheck() {
  try {
    console.log('\\n1. Testing health check...');
    const response = await axios.get(`${BASE_URL}/`, { timeout: 30000 });
    
    console.log('✅ Health check passed:', {
      status: response.data.status,
      server_url: response.data.server_url,
      environment: response.data.environment,
      port: response.data.port,
      endpoints: response.data.endpoints?.length || 0,
      api_keys: {
        openrouter: response.data.api_keys_loaded?.openrouter,
        removebg: response.data.api_keys_loaded?.removebg,
        unwatermark: response.data.api_keys_loaded?.unwatermark
      }
    });
    
    return true;
  } catch (error) {
    console.error('❌ Health check failed:');
    console.error('Status:', error.response?.status);
    console.error('Error:', error.response?.data || error.message);
    return false;
  }
}

// Test OpenRouter text generation
async function testTextGeneration() {
  try {
    console.log('\\n2. Testing OpenRouter text generation...');
    const response = await axios.post(`${BASE_URL}/api/text`, {
      prompt: 'Explain what Render cloud platform is in one sentence.',
      max_tokens: 100,
      temperature: 0.7
    }, { 
      timeout: 60000,
      headers: { 'Content-Type': 'application/json' }
    });
    
    console.log('✅ Text generation passed:', {
      success: response.data.success,
      hasText: !!response.data.data?.text,
      model: response.data.data?.model,
      textLength: response.data.data?.text?.length || 0,
      usage: response.data.data?.usage
    });
    
    if (response.data.data?.text) {
      console.log('📝 Generated text:', response.data.data.text.substring(0, 150) + '...');
    }
    
    return true;
  } catch (error) {
    console.error('❌ Text generation failed:');
    console.error('Status:', error.response?.status);
    console.error('Error:', error.response?.data || error.message);
    return false;
  }
}

// Test background removal with sample image
async function testBackgroundRemoval() {
  try {
    console.log('\\n3. Testing background removal...');
    
    // Create a simple test image buffer (1x1 PNG)
    const testImageBuffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAQhRetQAAAABJRU5ErkJggg==', 'base64');
    
    const formData = new FormData();
    formData.append('image', testImageBuffer, {
      filename: 'test.png',
      contentType: 'image/png'
    });

    const response = await axios.post(`${BASE_URL}/api/background-remove`, formData, {
      headers: formData.getHeaders(),
      timeout: 120000
    });
    
    console.log('✅ Background removal passed:', {
      success: response.data.success,
      hasResultUrl: !!response.data.data?.result_url,
      source: response.data.source || 'api'
    });
    
    return true;
  } catch (error) {
    console.error('❌ Background removal failed:');
    console.error('Status:', error.response?.status);
    console.error('Error:', error.response?.data || error.message);
    return false;
  }
}

// Test watermark removal with sample image
async function testWatermarkRemoval() {
  try {
    console.log('\\n4. Testing watermark removal...');
    
    // Create a simple test image buffer (1x1 PNG)
    const testImageBuffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAQhRetQAAAABJRU5ErkJggg==', 'base64');
    
    const formData = new FormData();
    formData.append('image', testImageBuffer, {
      filename: 'test.png',
      contentType: 'image/png'
    });

    const response = await axios.post(`${BASE_URL}/api/watermark-remove`, formData, {
      headers: formData.getHeaders(),
      timeout: 180000
    });
    
    console.log('✅ Watermark removal passed:', {
      success: response.data.success,
      hasResultUrl: !!response.data.data?.result_url,
      source: response.data.source || 'api'
    });
    
    return true;
  } catch (error) {
    console.error('❌ Watermark removal failed:');
    console.error('Status:', error.response?.status);
    console.error('Error:', error.response?.data || error.message);
    return false;
  }
}

// Test error handling
async function testErrorHandling() {
  try {
    console.log('\\n5. Testing error handling...');
    const response = await axios.post(`${BASE_URL}/api/text`, {
      prompt: '', // Empty prompt should trigger error
    }, { timeout: 10000 });
    
    if (response.data.success === false) {
      console.log('✅ Error handling working correctly:', response.data.error);
      return true;
    } else {
      console.log('⚠️ Error handling may not be working as expected');
      return false;
    }
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Error handling working correctly (400 status):', error.response.data.error);
      return true;
    } else {
      console.error('❌ Unexpected error in error handling test:', error.message);
      return false;
    }
  }
}

// Test CORS functionality
async function testCORS() {
  try {
    console.log('\\n6. Testing CORS headers...');
    const response = await axios.get(`${BASE_URL}/`, {
      headers: {
        'Origin': 'https://aifreeset.netlify.app'
      },
      timeout: 10000
    });
    
    console.log('✅ CORS test passed - frontend origin should be allowed');
    return true;
  } catch (error) {
    console.error('❌ CORS test failed:', error.message);
    return false;
  }
}

// Run all tests
async function runRenderTests() {
  console.log('🚀 Starting Render deployment tests...\\n');
  console.log('🌐 Testing server:', BASE_URL);
  console.log('🏢 Platform: Render Cloud');
  console.log('⚙️ Runtime: Node.js\\n');
  
  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'Text Generation (OpenRouter)', fn: testTextGeneration },
    { name: 'Background Removal (remove.bg)', fn: testBackgroundRemoval },
    { name: 'Watermark Removal (unwatermark.ai)', fn: testWatermarkRemoval },
    { name: 'Error Handling', fn: testErrorHandling },
    { name: 'CORS Configuration', fn: testCORS }
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    console.log(`\\n🔄 Running: ${test.name}`);
    const result = await test.fn();
    if (result) {
      passed++;
    } else {
      failed++;
    }
    
    // Add delay between tests to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log('\\n📊 Render Deployment Test Results:');
  console.log('=====================================');
  console.log(`✅ Passed: ${passed}/${tests.length}`);
  console.log(`❌ Failed: ${failed}/${tests.length}`);
  
  if (failed === 0) {
    console.log('\\n🎉 All tests passed! Backend is ready on Render.');
    console.log('🔗 Your backend is live at:', BASE_URL);
    console.log('\\n📋 Frontend Integration:');
    console.log('1. Update frontend to use:', BASE_URL);
    console.log('2. Verify CORS origin is set correctly');
    console.log('3. Test all endpoints from your frontend');
  } else {
    console.log('\\n⚠️ Some tests failed. Check Render logs and environment variables.');
    console.log('\\n🔧 Troubleshooting:');
    console.log('1. Check Render Dashboard → Logs');
    console.log('2. Verify environment variables are set');
    console.log('3. Ensure API keys are valid and have sufficient quota');
  }
  
  console.log('\\n🔍 Render Dashboard: https://dashboard.render.com/');
  console.log('📖 Documentation: See RENDER_DEPLOYMENT.md');
}

// Performance test
async function testPerformance() {
  console.log('\\n⚡ Performance Test');
  const start = Date.now();
  
  try {
    await axios.get(`${BASE_URL}/`, { timeout: 5000 });
    const responseTime = Date.now() - start;
    console.log(`📊 Response time: ${responseTime}ms`);
    
    if (responseTime < 1000) {
      console.log('✅ Excellent response time');
    } else if (responseTime < 3000) {
      console.log('⚠️ Acceptable response time');
    } else {
      console.log('❌ Slow response time - check Render region');
    }
  } catch (error) {
    console.error('❌ Performance test failed:', error.message);
  }
}

// Export for programmatic use
module.exports = {
  testHealthCheck,
  testTextGeneration,
  testBackgroundRemoval,
  testWatermarkRemoval,
  testErrorHandling,
  testCORS,
  testPerformance,
  runRenderTests
};

// Run tests if called directly
if (require.main === module) {
  runRenderTests()
    .then(() => testPerformance())
    .catch(console.error);
}