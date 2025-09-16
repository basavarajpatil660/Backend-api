# AiFreeSet Backend API

A Flask-based backend API for the AiFreeSet website, providing AI-powered image processing services.

## 🚀 Features

### API Integrations
- **Pixelcut API**: Image upscaling (2x), unblurring/enhancement, and background removal
- **Unwatermark.ai**: Watermark removal from images
- **Qwen 3 AI**: AI art generation from text prompts

### Security & Validation
- File type validation (JPG, PNG, WEBP, HEIC only)
- 10MB file size limit
- CORS configured for https://aifreeset.netlify.app only
- Environment-based API key management
- Comprehensive error handling with consistent JSON responses

## 📋 API Endpoints

### Health Check
#### `GET /`
Health check endpoint
- **Output**: `{"status": "AiFreeSet backend running"}`

### Image Processing Endpoints

#### `POST /api/upscale`
Upscale images using Pixelcut API (2x upscale by default)
- **Input**: Form data with `image` file
- **Output**: `{"success": true, "output_url": "https://..."}`

#### `POST /api/unblur`
Enhance/sharpen blurry images using Pixelcut API
- **Input**: Form data with `image` file
- **Output**: `{"success": true, "output_url": "https://..."}`

#### `POST /api/background-remove`
Remove background from images using Pixelcut API
- **Input**: Form data with `image` file
- **Output**: `{"success": true, "output_url": "https://..."}`

#### `POST /api/watermark-remove`
Remove watermarks from images using Unwatermark.ai
- **Input**: Form data with `image` file
- **Output**: `{"success": true, "output_url": "https://..."}`

#### `POST /api/ai-art`
Generate AI art from text prompts using Qwen 3
- **Input**: JSON `{"prompt": "your text prompt"}`
- **Output**: `{"success": true, "output_url": "https://..."}`

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Local Development

1. **Navigate to the project directory:**
   ```bash
   cd "e:\web dev backend"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional):**
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env with your actual API keys if different from defaults
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

### Environment Variables

The application uses the following environment variables with fallback defaults:

```env
PIXELCUT_API_KEY=sk_2d205bd00cad484db6ce55ef0f936db2
UNWATERMARK_API_KEY=7RNirCJcUpnFlQu1n-WfPFZoeaxtFQm1VWj5evrPgsg
QWEN_API_KEY=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
PORT=5000
```

## 🚀 Deployment

### Heroku Deployment

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create a new Heroku app:**
   ```bash
   heroku create aifreeset-backend
   ```

3. **Set environment variables on Heroku:**
   ```bash
   heroku config:set PIXELCUT_API_KEY=sk_2d205bd00cad484db6ce55ef0f936db2
   heroku config:set UNWATERMARK_API_KEY=7RNirCJcUpnFlQu1n-WfPFZoeaxtFQm1VWj5evrPgsg
   heroku config:set QWEN_API_KEY=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
   ```

4. **Deploy:**
   ```bash
   git init
   git add .
   git commit -m "Initial AiFreeSet backend deployment"
   git push heroku main
   ```

### Render Deployment

1. **Connect your repository** to Render
2. **Create a new Web Service** with the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
3. **Add environment variables** in the Render dashboard:
   - `PIXELCUT_API_KEY`: sk_2d205bd00cad484db6ce55ef0f936db2
   - `UNWATERMARK_API_KEY`: 7RNirCJcUpnFlQu1n-WfPFZoeaxtFQm1VWj5evrPgsg
   - `QWEN_API_KEY`: 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

### Other Platforms

The application is ready for deployment on:
- **Railway**: Use the Procfile for automatic deployment
- **DigitalOcean App Platform**: Configure with the provided requirements.txt
- **Google Cloud Run**: Deploy using Docker or buildpacks
- **AWS Elastic Beanstalk**: Upload as a ZIP with all files

## 🔧 Manual Testing Commands for Deployed Backend

### Test Health Check
```bash
curl https://backend-api-jumi.onrender.com/
# Expected: {"status": "AiFreeSet backend running"}
```

### Test Image Processing Endpoints

#### Upscale Image
```bash
curl -X POST \
  -F "image=@path/to/your/image.jpg" \
  https://backend-api-jumi.onrender.com/api/upscale
```

#### Unblur Image
```bash
curl -X POST \
  -F "image=@path/to/your/blurry-image.jpg" \
  https://backend-api-jumi.onrender.com/api/unblur
```

#### Remove Background
```bash
curl -X POST \
  -F "image=@path/to/your/image.jpg" \
  https://backend-api-jumi.onrender.com/api/background-remove
```

#### Remove Watermark
```bash
curl -X POST \
  -F "image=@path/to/watermarked-image.jpg" \
  https://backend-api-jumi.onrender.com/api/watermark-remove
```

#### Generate AI Art
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset over mountains, digital art"}' \
  https://backend-api-jumi.onrender.com/api/ai-art
```

### Expected Success Response Format
```json
{
  "success": true,
  "output_url": "https://processed-image-url.com/image.png"
}
```

### Expected Error Response Format
```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

## 📁 Project Structure

```
e:\web dev backend\
├── app.py              # Main Flask application with all API endpoints
├── requirements.txt    # Python dependencies (flask, flask-cors, requests, gunicorn)
├── Procfile           # Deployment configuration (web: gunicorn app:app)
├── .env.example       # Environment variables template with API keys
├── .gitignore         # Git ignore file
└── README.md          # This documentation
```

## 🔧 Configuration

### CORS Settings
CORS is configured to accept requests **only** from:
- `https://aifreeset.netlify.app` (your production frontend)

### File Upload Limits
- **Maximum file size**: 10MB (enforced at Flask level)
- **Allowed formats**: JPG, JPEG, PNG, WEBP, HEIC only

### API Keys
All API keys are loaded from environment variables with the provided keys as fallbacks:
- **Pixelcut API**: `PIXELCUT_API_KEY`
- **Unwatermark.ai**: `UNWATERMARK_API_KEY` 
- **Qwen 3 AI**: `QWEN_API_KEY`

## 🛡️ Security Features

- **Input validation** for all file uploads
- **File type and size restrictions** enforced
- **Environment-based API key management**
- **CORS protection** (only your frontend allowed)
- **Comprehensive error handling** with try/catch blocks
- **Consistent JSON responses** for all endpoints

## 📝 API Response Format

### Success Response
```json
{
  "success": true,
  "output_url": "https://processed-image-url.com/image.png"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

### Health Check Response
```json
{
  "status": "AiFreeSet backend running"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Import/Dependency errors**: 
   ```bash
   pip install -r requirements.txt
   ```

2. **Port already in use**: 
   - Change the PORT environment variable
   - Kill the process: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`

3. **File upload errors**: 
   - Ensure file is under 10MB
   - Check file format (JPG, PNG, WEBP, HEIC only)
   - Verify Content-Type is set correctly

4. **API key errors**: 
   - Check environment variables are set correctly
   - Verify API keys have sufficient credits/quota
   - Ensure keys haven't expired

5. **CORS errors**: 
   - Verify requests are coming from `https://aifreeset.netlify.app`
   - Check browser console for specific CORS messages

### Debug Mode
The application runs in debug mode during local development (`debug=True`), providing detailed error messages in the console.

### Deployment Issues
- **Heroku**: Check logs with `heroku logs --tail`
- **Render**: Monitor logs in the Render dashboard
- **Environment variables**: Ensure all required variables are set in production

## 📞 Support

For issues:
1. Check console output for detailed error messages
2. Verify API keys are valid and have credits
3. Ensure file uploads meet requirements (size/format)
4. Check that dependencies are properly installed
5. Verify CORS settings if experiencing frontend connectivity issues

---

**🎉 Ready for Production!**

Your AiFreeSet backend is now ready for deployment. The API will handle all image processing requests from your frontend at `https://aifreeset.netlify.app` with proper security, validation, and error handling.