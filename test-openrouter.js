const axios = require('axios');

const BASE_URL = process.env.TEST_URL || 'http://localhost:5000';

console.log(`🧪 Testing OpenRouter Integration at: ${BASE_URL}`);

// Test OpenRouter text generation
async function testOpenRouterTextGeneration() {
  try {
    console.log('\n1. Testing OpenRouter text generation...');
    const response = await axios.post(`${BASE_URL}/api/text`, {
      prompt: 'What is artificial intelligence?',
      max_tokens: 100,
      temperature: 0.7
    }, {
      timeout: 30000
    });
    
    console.log('✅ OpenRouter text generation response:', {
      success: response.data.success,
      hasText: !!response.data.data?.text,
      model: response.data.data?.model,
      textLength: response.data.data?.text?.length || 0,
      usage: response.data.data?.usage
    });
    
    if (response.data.data?.text) {
      console.log('📝 Generated text preview:', response.data.data.text.substring(0, 200) + '...');
    }
    
    return true;
  } catch (error) {
    console.error('❌ OpenRouter text generation failed:');
    console.error('Status:', error.response?.status);
    console.error('Error:', error.response?.data || error.message);
    return false;
  }
}

// Test health check
async function testHealthCheck() {
  try {
    console.log('\n2. Testing health check...');
    const response = await axios.get(`${BASE_URL}/`);
    console.log('✅ Health check passed:', {
      status: response.data.status,
      openrouterKey: response.data.api_keys_loaded?.openrouter,
      removebgKey: response.data.api_keys_loaded?.removebg,
      unwatermarkKey: response.data.api_keys_loaded?.unwatermark
    });
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return false;
  }
}

// Test error handling with invalid payload
async function testErrorHandling() {
  try {
    console.log('\n3. Testing error handling...');
    const response = await axios.post(`${BASE_URL}/api/text`, {
      prompt: '', // Empty prompt should trigger error
    });
    
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

// Run all tests
async function runTests() {
  console.log('🚀 Starting OpenRouter integration tests...\n');
  
  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'OpenRouter Text Generation', fn: testOpenRouterTextGeneration },
    { name: 'Error Handling', fn: testErrorHandling }
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
    console.log('🎉 All OpenRouter integration tests passed! Backend is ready.');
  } else {
    console.log('⚠️ Some tests failed. Check the error messages above.');
  }
  
  console.log('\n📋 Next Steps:');
  console.log('1. Make sure OPENROUTER_API_KEY is set in your .env file');
  console.log('2. Deploy to Railway with the updated environment variable');
  console.log('3. Test the deployed version with: TEST_URL=https://your-app.railway.app node test-openrouter.js');
}

// Export for programmatic use
module.exports = {
  testHealthCheck,
  testOpenRouterTextGeneration,
  testErrorHandling,
  runTests
};

// Run tests if called directly
if (require.main === module) {
  runTests().catch(console.error);
}