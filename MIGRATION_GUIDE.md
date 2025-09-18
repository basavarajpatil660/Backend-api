# Flask to Node.js Migration Guide

## 📋 Migration Summary

Successfully migrated AiFreeSet backend from **Flask (Python)** to **Express.js (Node.js)** with significant improvements and new integrations.

## 🔄 Key Changes

### 1. Framework Migration
- **From**: Flask (Python) with gunicorn
- **To**: Express.js (Node.js) with native performance

### 2. API Integrations Updated

#### Qwen 3 Integration ✅
- **Updated**: Full Qwen 3 API integration
- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **New Endpoints**:
  - `POST /api/text` - Text generation (chat completion)
  - `POST /api/image` - Image generation (text-to-image)
- **Improvements**: Better error handling, response parsing

#### Background Removal ✅
- **From**: Pixelcut API (problematic on Railway)
- **To**: Remove.bg API (more reliable)
- **Endpoint**: `POST /api/background-remove`
- **Benefits**: Better reliability, wider support

#### Watermark Removal ✅
- **Enhanced**: Dynamic field detection
- **Endpoint**: `POST /api/watermark-remove`
- **Improvement**: Automatically detects correct response field names

### 3. Technical Improvements

#### Error Handling
- **Before**: Basic try/catch with simple fallbacks
- **After**: Comprehensive retry logic with exponential backoff
- **Added**: Smart fallback responses maintain frontend functionality

#### File Upload
- **Before**: werkzeug file handling
- **After**: multer with memory storage
- **Improved**: Better validation and security

#### API Client
- **Before**: requests library with basic retry
- **After**: axios with comprehensive retry strategy
- **Enhanced**: Connection pooling, timeout handling

#### Security
- **Before**: flask-cors basic protection
- **After**: helmet security headers + cors
- **Added**: Compression, request limits

## 📁 File Structure Changes

### New Files Created
```
├── server.js              # Main Express application
├── package.json           # Node.js dependencies
├── .env.example           # Environment variables template
├── test.js               # Comprehensive test suite
├── README_NODEJS.md      # Node.js documentation
├── RAILWAY_DEPLOYMENT.md # Deployment guide
├── install.bat           # Windows installation script
├── start.bat             # Windows start script
└── MIGRATION_GUIDE.md    # This file
```

### Original Files (can be archived)
```
├── app.py                # Original Flask application
├── requirements.txt      # Python dependencies
├── test_*.py            # Python test files
└── *.md                 # Original documentation
```

## 🔧 Environment Variables Changes

### Flask (.env)
```env
PIXELCUT_API_KEY=...
UNWATERMARK_API_KEY=...
QWEN_API_KEY=...
PORT=5000
```

### Node.js (.env)
```env
QWEN_API_KEY=...
REMOVEBG_API_KEY=...      # NEW: Replace Pixelcut
UNWATERMARK_API_KEY=...
NODE_ENV=production       # NEW: Environment setting
PORT=5000
```

## 🚀 Deployment Changes

### Before (Flask)
```bash
# Install
pip install -r requirements.txt

# Run
python app.py
# or
gunicorn app:app
```

### After (Node.js)
```bash
# Install
npm install

# Run
npm start              # Production
npm run dev           # Development with nodemon
```

### Railway Deployment
- **Automatic Detection**: Railway auto-detects Node.js
- **Build Command**: `npm install` 
- **Start Command**: `npm start`
- **Environment**: Set variables in Railway dashboard

## 🔌 API Endpoint Comparison

### Health Check
- **Endpoint**: `GET /` (unchanged)
- **Response**: Enhanced with API key status

### Text Generation (NEW)
```javascript
// NEW ENDPOINT
POST /api/text
{
  "prompt": "Your text here",
  "max_tokens": 2000,
  "temperature": 0.7
}
```

### Image Generation (UPDATED)
```javascript
// UPDATED: Was /api/ai-art, now /api/image
POST /api/image
{
  "prompt": "A beautiful sunset",
  "size": "1024*1024",
  "style": "<auto>"
}
```

### Background Removal (UPDATED)
```javascript
// UPDATED: New remove.bg integration
POST /api/background-remove
Content-Type: multipart/form-data
```

### Watermark Removal (ENHANCED)
```javascript
// ENHANCED: Better response parsing
POST /api/watermark-remove
Content-Type: multipart/form-data
```

## 🧪 Testing Improvements

### Flask Testing
- Basic curl commands
- Manual testing required

### Node.js Testing
- **Comprehensive test suite**: `test.js`
- **Automated testing**: `npm test`
- **Multiple test scenarios**: All endpoints covered
- **Deployment testing**: Test remote deployments

## 🔄 Migration Steps

### 1. Archive Flask Files (Optional)
```bash
mkdir archive
mv app.py requirements.txt test_*.py archive/
```

### 2. Install Node.js Dependencies
```bash
npm install
```

### 3. Update Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Test Locally
```bash
npm run dev    # Start development server
npm test       # Run test suite
```

### 5. Deploy to Railway
1. Push code to GitHub
2. Connect repository to Railway
3. Set environment variables
4. Deploy automatically

### 6. Update Frontend
Update frontend to use new API endpoints:
- Change `/api/ai-art` → `/api/image`
- Add support for new `/api/text` endpoint
- Verify CORS origin configuration

## ⚡ Performance Benefits

### Response Times
- **Faster startup**: Node.js starts quicker than Python
- **Better concurrency**: Event-loop handles multiple requests efficiently
- **Reduced memory**: Lower memory footprint

### Reliability
- **Retry logic**: Exponential backoff for failed requests
- **Fallback responses**: Never break frontend functionality  
- **Better error handling**: Comprehensive error catching

### Development Experience
- **Hot reload**: nodemon for development
- **Modern syntax**: ES6+ features
- **Better tooling**: npm ecosystem

## 🚨 Breaking Changes

### API Changes
1. **Endpoint rename**: `/api/ai-art` → `/api/image`
2. **New endpoint**: `/api/text` for text generation
3. **Background removal**: Now uses remove.bg instead of Pixelcut

### Response Format Changes
- **Consistent structure**: All responses follow same format
- **Source indicator**: `source: 'api'` vs `source: 'dummy'`
- **Enhanced error messages**: More descriptive error responses

### Environment Variables
- **New required**: `REMOVEBG_API_KEY`
- **Removed**: `PIXELCUT_API_KEY` 
- **Added**: `NODE_ENV`

## ✅ Migration Validation

### Checklist
- [ ] All dependencies installed (`npm install`)
- [ ] Environment variables configured
- [ ] Local testing passed (`npm test`)
- [ ] Deployed to Railway successfully
- [ ] All endpoints responding correctly
- [ ] Frontend updated with new endpoints
- [ ] Error handling tested
- [ ] Fallback responses working

### Test Commands
```bash
# Local testing
npm test

# Remote testing
TEST_URL=https://your-app.railway.app node test.js

# Health check
curl https://your-app.railway.app/
```

## 🎯 Benefits Achieved

1. **✅ Qwen 3 Integration**: Full text and image generation
2. **✅ Reliable Background Removal**: remove.bg instead of Pixelcut
3. **✅ Enhanced Error Handling**: Comprehensive retry and fallback logic
4. **✅ Better Performance**: Node.js efficiency and modern architecture
5. **✅ Improved Security**: Helmet, proper CORS, validation
6. **✅ Development Experience**: Better tooling, testing, documentation
7. **✅ Railway Compatibility**: Optimized for Railway deployment

## 🚀 Next Steps

1. **Monitor Production**: Watch Railway logs and metrics
2. **Frontend Integration**: Update frontend to use new endpoints
3. **API Key Management**: Ensure all keys are properly configured
4. **Performance Testing**: Monitor response times and error rates
5. **Documentation**: Share new API docs with frontend team

Your Flask to Node.js migration is complete! The new backend is more robust, performant, and ready for production deployment on Railway. 🎉