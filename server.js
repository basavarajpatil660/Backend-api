const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
const helmet = require('helmet');
const compression = require('compression');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Security and optimization middleware
app.use(helmet());
app.use(compression());

// Configure CORS - only allow requests from your frontend
app.use(cors({
  origin: ['https://aifreeset.netlify.app'],
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/heic'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Unsupported file type. Allowed: JPG, PNG, WEBP, HEIC'), false);
    }
  }
});

// API Keys from environment variables
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const REMOVEBG_API_KEY = process.env.REMOVEBG_API_KEY;
const UNWATERMARK_API_KEY = process.env.UNWATERMARK_API_KEY;

// Logging configuration
const logApiKeyStatus = () => {
  console.log('=== API KEYS STATUS ===');
  console.log(`OpenRouter API Key: ${OPENROUTER_API_KEY ? '✓ Loaded' : '✗ Missing'}`);
  console.log(`Remove.bg API Key: ${REMOVEBG_API_KEY ? '✓ Loaded' : '✗ Missing'}`);
  console.log(`Unwatermark API Key: ${UNWATERMARK_API_KEY ? '✓ Loaded' : '✗ Missing'}`);
  console.log('=========================');
};

logApiKeyStatus();

// Helper function to create axios instance with retry logic
const createAxiosWithRetry = (timeout = 90000) => {
  const instance = axios.create({
    timeout: timeout,
    validateStatus: (status) => status < 500 // Only retry on 5xx errors
  });

  // Add request interceptor for logging
  instance.interceptors.request.use(
    (config) => {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Add response interceptor for logging
  instance.interceptors.response.use(
    (response) => {
      console.log(`API Response: ${response.status} from ${response.config?.url}`);
      return response;
    },
    (error) => {
      console.error(`API Error: ${error.response?.status || 'No status'} from ${error.config?.url}`);
      return Promise.reject(error);
    }
  );

  return instance;
};

// Helper function for API calls with retry logic
const makeApiRequestWithRetry = async (apiCall, maxRetries = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`API attempt ${attempt}/${maxRetries}`);
      const result = await apiCall();
      return result;
    } catch (error) {
      console.error(`Attempt ${attempt} failed:`, error.message);
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff
      const delay = Math.pow(2, attempt - 1) * 1000;
      console.log(`Retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};

// Helper function to validate file upload
const validateFileUpload = (req) => {
  if (!req.file) {
    return { error: 'No image file provided' };
  }

  if (!req.file.buffer || req.file.buffer.length === 0) {
    return { error: 'Empty file received' };
  }

  console.log(`File received: ${req.file.originalname}, Size: ${req.file.size} bytes`);
  return null;
};

// Helper function to create dummy response for fallback
const createDummyResponse = (type) => {
  const dummyResponses = {
    text: {
      success: true,
      source: 'dummy',
      data: {
        text: 'This is a dummy response. The AI text generation service is temporarily unavailable.',
        model: 'qwen/qwq-32b:free'
      }
    },
    'background-remove': {
      success: true,
      source: 'dummy',
      data: {
        result_url: 'https://via.placeholder.com/512x512.png?text=Background+Removed+Placeholder'
      }
    },
    'watermark-remove': {
      success: true,
      source: 'dummy',
      data: {
        result_url: 'https://via.placeholder.com/512x512.png?text=Watermark+Removed+Placeholder'
      }
    }
  };

  return dummyResponses[type] || {
    success: false,
    error: 'Service temporarily unavailable'
  };
};

// Health check endpoint
app.get('/', (req, res) => {
  console.log('Health check requested');
  res.json({
    status: 'AiFreeSet Node.js backend running on Render',
    server_url: 'https://backend-api-jumi.onrender.com',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    port: PORT,
    api_keys_loaded: {
      openrouter: !!OPENROUTER_API_KEY,
      removebg: !!REMOVEBG_API_KEY,
      unwatermark: !!UNWATERMARK_API_KEY
    },
    endpoints: [
      'GET /',
      'POST /api/text',
      'POST /api/background-remove',
      'POST /api/watermark-remove'
    ]
  });
});

// Text generation endpoint using OpenRouter with Qwen
app.post('/api/text', async (req, res) => {
  console.log('=== TEXT GENERATION REQUEST STARTED ===');
  
  try {
    const { prompt, max_tokens = 2000, temperature = 0.7 } = req.body;
    
    if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Prompt is required and must be a non-empty string'
      });
    }

    if (!OPENROUTER_API_KEY) {
      console.error('OpenRouter API key not configured');
      return res.status(500).json({
        success: false,
        error: 'OpenRouter API key not configured'
      });
    }

    const apiCall = async () => {
      const axiosInstance = createAxiosWithRetry(120000);
      
      const response = await axiosInstance.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: 'qwen/qwq-32b:free',
          messages: [
            {
              role: 'user',
              content: prompt.trim()
            }
          ],
          max_tokens: parseInt(max_tokens),
          temperature: parseFloat(temperature)
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'User-Agent': 'AiFreeSet-Backend/2.0'
          }
        }
      );

      console.log('OpenRouter API response status:', response.status);
      console.log('OpenRouter API response data:', JSON.stringify(response.data, null, 2));

      if (response.status === 200 && response.data) {
        const result = response.data;
        
        if (result.choices && result.choices.length > 0) {
          const choice = result.choices[0];
          const text = choice.message?.content;
          
          if (text) {
            return {
              success: true,
              data: {
                text: text.trim(),
                model: result.model || 'qwen/qwq-32b:free',
                usage: result.usage
              }
            };
          }
        }
        
        console.error('No text content found in OpenRouter response:', result);
        throw new Error('No text content found in OpenRouter response');
      } else {
        console.error(`OpenRouter API error: HTTP ${response.status}`, response.data);
        throw new Error(`OpenRouter API error: HTTP ${response.status}`);
      }
    };

    const result = await makeApiRequestWithRetry(apiCall);
    res.json(result);

  } catch (error) {
    console.error('Text generation error:', error.message);
    console.error('Full error details:', error.response?.data || error);
    
    // Return 500 status for API failures as requested
    res.status(500).json({
      success: false,
      error: 'Text generation service temporarily unavailable'
    });
  }
});

// Background removal endpoint using remove.bg
app.post('/api/background-remove', upload.single('image'), async (req, res) => {
  console.log('=== BACKGROUND REMOVAL REQUEST STARTED ===');
  
  try {
    const validationError = validateFileUpload(req);
    if (validationError) {
      return res.status(400).json({
        success: false,
        error: validationError.error
      });
    }

    if (!REMOVEBG_API_KEY) {
      console.error('Remove.bg API key not configured');
      return res.json(createDummyResponse('background-remove'));
    }

    const apiCall = async () => {
      const formData = new FormData();
      formData.append('image_file', req.file.buffer, {
        filename: req.file.originalname,
        contentType: req.file.mimetype
      });
      formData.append('size', 'auto');

      const axiosInstance = createAxiosWithRetry(120000);
      
      const response = await axiosInstance.post(
        'https://api.remove.bg/v1.0/removebg',
        formData,
        {
          headers: {
            'X-Api-Key': REMOVEBG_API_KEY,
            'User-Agent': 'AiFreeSet-Backend/2.0',
            ...formData.getHeaders()
          },
          responseType: 'arraybuffer'
        }
      );

      if (response.status === 200) {
        // Convert response to base64
        const base64Image = Buffer.from(response.data).toString('base64');
        const imageDataUrl = `data:image/png;base64,${base64Image}`;
        
        return {
          success: true,
          data: {
            result_url: imageDataUrl
          }
        };
      } else {
        throw new Error(`Remove.bg API error: HTTP ${response.status}`);
      }
    };

    const result = await makeApiRequestWithRetry(apiCall);
    res.json(result);

  } catch (error) {
    console.error('Background removal error:', error.message);
    res.json(createDummyResponse('background-remove'));
  }
});

// Watermark removal endpoint using unwatermark.ai
app.post('/api/watermark-remove', upload.single('image'), async (req, res) => {
  console.log('=== WATERMARK REMOVAL REQUEST STARTED ===');
  
  try {
    const validationError = validateFileUpload(req);
    if (validationError) {
      return res.status(400).json({
        success: false,
        error: validationError.error
      });
    }

    if (!UNWATERMARK_API_KEY) {
      console.error('Unwatermark API key not configured');
      return res.json(createDummyResponse('watermark-remove'));
    }

    const apiCall = async () => {
      const formData = new FormData();
      formData.append('image', req.file.buffer, {
        filename: req.file.originalname,
        contentType: req.file.mimetype
      });

      const axiosInstance = createAxiosWithRetry(180000); // 3 minutes for watermark removal
      
      const response = await axiosInstance.post(
        'https://api.unwatermark.ai/v1/remove',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${UNWATERMARK_API_KEY}`,
            'User-Agent': 'AiFreeSet-Backend/2.0',
            ...formData.getHeaders()
          }
        }
      );

      console.log('Unwatermark API response status:', response.status);
      console.log('Unwatermark API response data:', JSON.stringify(response.data, null, 2));

      if (response.status === 200 && response.data) {
        const result = response.data;
        
        // Dynamically detect the correct field for the result URL
        const possibleUrlFields = [
          'output_url', 'result_url', 'url', 'image_url', 
          'processed_url', 'processed_image', 'download_url',
          'data.url', 'data.output_url', 'data.result_url'
        ];
        
        let resultUrl = null;
        
        for (const field of possibleUrlFields) {
          if (field.includes('.')) {
            // Handle nested fields like 'data.url'
            const parts = field.split('.');
            let value = result;
            for (const part of parts) {
              value = value?.[part];
            }
            if (value) {
              resultUrl = value;
              console.log(`Found result URL in field: ${field}`);
              break;
            }
          } else {
            // Handle direct fields
            if (result[field]) {
              resultUrl = result[field];
              console.log(`Found result URL in field: ${field}`);
              break;
            }
          }
        }
        
        if (resultUrl) {
          return {
            success: true,
            data: {
              result_url: resultUrl
            }
          };
        } else {
          console.error('No result URL found in any expected field. Full response:', result);
          throw new Error('No result URL found in API response');
        }
      } else {
        throw new Error(`Unwatermark API error: HTTP ${response.status}`);
      }
    };

    const result = await makeApiRequestWithRetry(apiCall);
    res.json(result);

  } catch (error) {
    console.error('Watermark removal error:', error.message);
    res.json(createDummyResponse('watermark-remove'));
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        error: 'File size exceeds 10MB limit'
      });
    }
  }
  
  console.error('Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 AiFreeSet Express backend running on Render`);
  console.log(`🌐 Server URL: https://backend-api-jumi.onrender.com`);
  console.log(`📡 Port: ${PORT}`);
  console.log(`🏗️ Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📅 Started at: ${new Date().toISOString()}`);
  console.log(`💻 Node version: ${process.version}`);
  logApiKeyStatus();
  
  // Additional Render-specific logging
  console.log('\n=== RENDER DEPLOYMENT INFO ===');
  console.log('Platform: Render Cloud');
  console.log('Runtime: Node.js');
  console.log('Available endpoints:');
  console.log('  - GET /');
  console.log('  - POST /api/text');
  console.log('  - POST /api/background-remove');
  console.log('  - POST /api/watermark-remove');
  console.log('================================\n');
});

module.exports = app;