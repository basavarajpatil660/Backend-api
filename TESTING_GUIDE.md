# 🧪 AiFreeSet Backend Testing Guide

## API Testing Commands for Deployed Backend

### Health Check
```bash
curl -X GET https://backend-api-jumi.onrender.com/
```
**Expected Response:**
```json
{
  "status": "AiFreeSet backend running",
  "api_keys_loaded": {
    "pixelcut": true,
    "unwatermark": true,
    "qwen": true
  }
}
```

## Image Processing Endpoints

### 1. Background Remove (Focus Endpoint)
```bash
curl -X POST \
  -F "image=@/path/to/your/image.jpg" \
  https://backend-api-jumi.onrender.com/api/background-remove
```

### 2. Image Upscale
```bash
curl -X POST \
  -F "image=@/path/to/your/image.jpg" \
  https://backend-api-jumi.onrender.com/api/upscale
```

### 3. Image Unblur
```bash
curl -X POST \
  -F "image=@/path/to/your/image.jpg" \
  https://backend-api-jumi.onrender.com/api/unblur
```

### 4. Watermark Remove
```bash
curl -X POST \
  -F "image=@/path/to/your/image.jpg" \
  https://backend-api-jumi.onrender.com/api/watermark-remove
```

### 5. AI Art Generation
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful landscape with mountains and sunset"}' \
  https://backend-api-jumi.onrender.com/api/ai-art
```

## Expected Response Formats

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
  "error": "Detailed error message"
}
```

## File Validation Tests

### Test Invalid File Type
```bash
curl -X POST \
  -F "image=@document.pdf" \
  https://backend-api-jumi.onrender.com/api/background-remove
```
**Expected:** `{"success": false, "error": "Unsupported file type. Allowed: JPG, PNG, WEBP, HEIC"}`

### Test Large File (>10MB)
```bash
curl -X POST \
  -F "image=@large-image.jpg" \
  https://backend-api-jumi.onrender.com/api/background-remove
```
**Expected:** `{"success": false, "error": "File size exceeds 10MB limit"}`

### Test Empty Request
```bash
curl -X POST \
  https://backend-api-jumi.onrender.com/api/background-remove
```
**Expected:** `{"success": false, "error": "No image file provided"}`

## Debugging Commands

### Check Logs (Render Dashboard)
1. Go to your Render dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for detailed logging output

### Test with Verbose Output
```bash
curl -v -X POST \
  -F "image=@test.jpg" \
  https://backend-api-jumi.onrender.com/api/background-remove
```

## Common Error Scenarios and Solutions

### 1. HTTP 500 Error
- **Cause:** API key issues or external API failures
- **Check:** Environment variables in Render dashboard
- **Solution:** Verify API keys are set correctly

### 2. HTTP 400 Error
- **Cause:** File validation failure
- **Check:** File type, size, and format
- **Solution:** Use supported formats (JPG, PNG, WEBP, HEIC) under 10MB

### 3. HTTP 413 Error
- **Cause:** File too large
- **Solution:** Reduce file size to under 10MB

### 4. Timeout Errors
- **Cause:** External API taking too long
- **Check:** Render logs for timeout messages
- **Solution:** Try again or check API service status

## Local Testing (if running locally)

Replace `https://backend-api-jumi.onrender.com` with `http://localhost:5000` in all commands above.

Example:
```bash
curl -X POST \
  -F "image=@test.jpg" \
  http://localhost:5000/api/background-remove
```