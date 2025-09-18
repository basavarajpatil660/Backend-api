# AiFreeSet Node.js Backend

A modern Express.js backend for the AiFreeSet platform, providing AI-powered image processing and text generation capabilities.

## 🚀 Features

- **Qwen 3 Text Generation** - AI-powered text completion and chat
- **Qwen 3 Image Generation** - AI art creation from text prompts  
- **Background Removal** - Remove image backgrounds using remove.bg API
- **Watermark Removal** - Remove watermarks using unwatermark.ai API
- **Robust Error Handling** - Automatic retries with exponential backoff
- **Fallback Responses** - Dummy responses when APIs are unavailable
- **Security** - CORS protection, file validation, helmet security headers
- **Performance** - Compression, request optimization

## 📋 API Endpoints

### Health Check
```
GET /
```
Returns server status and API key availability.

### Text Generation
```
POST /api/text
Content-Type: application/json

{
  "prompt": "Your text prompt here",
  "max_tokens": 2000,
  "temperature": 0.7
}
```

### Image Generation  
```
POST /api/image
Content-Type: application/json

{
  "prompt": "A beautiful sunset over mountains",
  "size": "1024*1024",
  "style": "<auto>"
}
```

### Background Removal
```
POST /api/background-remove
Content-Type: multipart/form-data

Form data:
- image: [File] (JPG, PNG, WEBP, HEIC - max 10MB)
```

### Watermark Removal
```
POST /api/watermark-remove  
Content-Type: multipart/form-data

Form data:
- image: [File] (JPG, PNG, WEBP, HEIC - max 10MB)
```

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 16.0.0 or higher
- npm or yarn package manager

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   QWEN_API_KEY=your_qwen_api_key_here
   REMOVEBG_API_KEY=your_removebg_api_key_here  
   UNWATERMARK_API_KEY=your_unwatermark_api_key_here
   PORT=5000
   ```

3. **Start the server:**
   ```bash
   # Development
   npm run dev
   
   # Production
   npm start
   ```

## 🔑 API Keys Setup

### Qwen 3 API Key
1. Visit [Alibaba Cloud DashScope](https://dashscope.aliyuncs.com/)
2. Create an account and get your API key
3. Add to `.env` as `QWEN_API_KEY`

### Remove.bg API Key
1. Visit [remove.bg](https://www.remove.bg/api)
2. Sign up and get a free API key
3. Add to `.env` as `REMOVEBG_API_KEY`

### Unwatermark.ai API Key
1. Visit [unwatermark.ai](https://unwatermark.ai/)
2. Sign up and get your API key
3. Add to `.env` as `UNWATERMARK_API_KEY`

## 🧪 Testing

Run the comprehensive test suite:
```bash
npm test
```

Test individual endpoints:
```bash
# Test locally
node test.js

# Test deployed version
TEST_URL=https://your-backend-url.com node test.js
```

## 🚀 Deployment

### Railway
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Render
1. Connect repository
2. Set build command: `npm install`
3. Set start command: `npm start`
4. Add environment variables

### Heroku
```bash
heroku create your-app-name
heroku config:set QWEN_API_KEY=your_key
heroku config:set REMOVEBG_API_KEY=your_key
heroku config:set UNWATERMARK_API_KEY=your_key
git push heroku main
```

## 📊 Response Format

All endpoints return JSON in this format:

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Endpoint-specific data
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message description"
}
```

**Fallback Response (when APIs are down):**
```json
{
  "success": true,
  "source": "dummy",
  "data": {
    // Placeholder data
  }
}
```

## 🔒 Security Features

- **CORS Protection** - Only allows requests from `https://aifreeset.netlify.app`
- **File Validation** - Validates file types and size limits
- **Helmet Security** - Adds security headers
- **Environment Variables** - API keys never exposed in code
- **Request Limits** - 10MB file upload limit

## 🎯 Key Improvements over Flask Version

1. **Better Error Handling** - Comprehensive try/catch with proper fallbacks
2. **Dynamic Field Detection** - Automatically detects correct API response fields
3. **Retry Logic** - Exponential backoff for failed requests
4. **Modern Dependencies** - Latest Express.js and middleware
5. **Comprehensive Testing** - Built-in test suite
6. **Better Logging** - Detailed request/response logging
7. **Remove.bg Integration** - Replaces problematic Pixelcut API

## 📈 Performance Optimizations

- **Compression** - Gzip compression for responses
- **Connection Pooling** - Axios with keep-alive
- **Memory Efficiency** - Multer memory storage
- **Timeout Handling** - Proper timeout configuration
- **Retry Strategy** - Smart retry with backoff

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 5000
npx kill-port 5000
```

**API key errors:**
- Check `.env` file exists and has correct format
- Verify API keys are valid and have sufficient quota
- Check server logs for detailed error messages

**CORS errors:**
- Ensure frontend origin matches exactly: `https://aifreeset.netlify.app`
- Check browser console for specific CORS messages

**File upload errors:**
- Verify file is under 10MB
- Check file type is supported (JPG, PNG, WEBP, HEIC)
- Ensure proper form-data format

## 📝 Development Notes

- All API calls have automatic retry logic with exponential backoff
- Fallback dummy responses ensure frontend never breaks
- Comprehensive logging helps with debugging
- Environment-based configuration for different deployment stages
- Modern ES6+ syntax with proper error handling

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for detailed error messages
3. Test with the included test suite
4. Verify API keys and quotas