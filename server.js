import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware - Configure CORS for specific frontend
app.use(cors({
  origin: [
    'https://aifreeset.netlify.app',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5500' // For local development
  ],
  credentials: true
}));
app.use(express.json());

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'OpenRouter Backend API is running',
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;

    // Validate input
    if (!message || typeof message !== 'string' || message.trim() === '') {
      return res.status(400).json({
        error: 'Message is required and must be a non-empty string'
      });
    }

    // Check if API key is configured
    if (!process.env.OPENROUTER_API_KEY) {
      return res.status(500).json({
        error: 'OpenRouter API key not configured'
      });
    }

    // Prepare request to OpenRouter API
    const openRouterResponse = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'qwen/qwen3-32b',
        messages: [
          {
            role: 'user',
            content: message.trim()
          }
        ]
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://aifreeset.netlify.app',
          'X-Title': 'AI Free Set'
        },
        timeout: 30000 // 30 seconds timeout
      }
    );

    // Extract the AI response
    const aiResponse = openRouterResponse.data.choices[0]?.message?.content;
    
    if (!aiResponse) {
      return res.status(500).json({
        error: 'No response received from AI model'
      });
    }

    // Return successful response
    res.json({
      success: true,
      response: aiResponse,
      model: 'qwen/qwen3-32b',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Chat API Error:', error.message);
    
    // Handle different types of errors
    if (error.response) {
      // OpenRouter API returned an error
      const status = error.response.status;
      const errorMessage = error.response.data?.error?.message || 'OpenRouter API error';
      
      return res.status(status >= 400 && status < 500 ? status : 500).json({
        error: errorMessage,
        details: status === 401 ? 'Invalid API key' : undefined
      });
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      return res.status(504).json({
        error: 'Request timeout - AI model took too long to respond'
      });
    } else if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      // Network error
      return res.status(503).json({
        error: 'Unable to connect to OpenRouter API'
      });
    } else {
      // Generic server error
      return res.status(500).json({
        error: 'Internal server error occurred'
      });
    }
  }
});

// Handle 404 for unknown routes
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    available_endpoints: [
      'GET /',
      'POST /api/chat'
    ]
  });
});

// Global error handler
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}`);
  console.log(`💬 Chat endpoint: http://localhost:${PORT}/api/chat`);
  console.log(`🔑 API Key configured: ${process.env.OPENROUTER_API_KEY ? '✅' : '❌'}`);
});