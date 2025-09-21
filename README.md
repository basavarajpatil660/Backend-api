# AI Free Set - Fullstack Chat Application

A complete fullstack application that connects to OpenRouter's Qwen 3 model, featuring a Node.js Express backend and a modern HTML/CSS/JS frontend.

## 🚀 Features

- **Backend**: Node.js + Express with OpenRouter API integration
- **Frontend**: Modern, responsive chat UI with real-time messaging
- **AI Model**: Qwen 3-32B via OpenRouter
- **Deployment Ready**: Backend for Railway/Render, Frontend for Netlify
- **Mobile Friendly**: Responsive design for all devices
- **Error Handling**: Comprehensive error handling and user feedback

## 📁 Project Structure

```
ai-free-set/
├── backend/
│   ├── server.js          # Express server with OpenRouter integration
│   ├── package.json       # Backend dependencies
│   ├── .env              # Environment variables (API key)
│   ├── .env.example      # Environment template
│   └── .gitignore        # Git ignore file
│
├── frontend/
│   ├── index.html        # Main HTML file
│   ├── style.css         # Responsive CSS styles
│   └── script.js         # Frontend JavaScript logic
│
└── README.md             # This file
```

## 🛠️ Backend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

The `.env` file is already configured with the provided API key:

```env
OPENROUTER_API_KEY=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
PORT=5000
```

### 3. Start the Backend Server

```bash
# Development mode (auto-restart)
npm run dev

# Production mode
npm start
```

Server will run on `http://localhost:5000`

### 4. Test Backend API

```bash
# Health check
curl http://localhost:5000/

# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Qwen 3!"}'
```

## 🎨 Frontend Setup

### Local Development

1. **Update API URL** in `frontend/script.js`:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'http://localhost:5000', // For local development
       // API_BASE_URL: 'https://your-backend-url.com', // For production
   };
   ```

2. **Serve the frontend** using any static server:
   ```bash
   # Using Python
   cd frontend
   python -m http.server 3000
   
   # Using Node.js http-server
   npx http-server frontend -p 3000
   
   # Using Live Server (VS Code extension)
   # Right-click index.html → "Open with Live Server"
   ```

3. **Open in browser**: `http://localhost:3000`

## 🚀 Deployment

### Backend Deployment (Railway)

1. **Connect Repository**:
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository
   - Select the backend folder as root

2. **Set Environment Variables**:
   ```
   OPENROUTER_API_KEY=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
   PORT=5000
   ```

3. **Deploy**: Railway will automatically detect and deploy your Node.js app

### Backend Deployment (Render)

1. **Create Web Service**:
   - Go to [Render](https://render.com)
   - Connect your GitHub repository
   - Choose "Web Service"

2. **Configuration**:
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Environment Variables**: Add `OPENROUTER_API_KEY`

3. **Deploy**: Render will build and deploy your backend

### Frontend Deployment (Netlify)

1. **Update API URL** in `frontend/script.js`:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'https://your-backend-url.railway.app', // Your deployed backend URL
   };
   ```

2. **Deploy to Netlify**:
   - Go to [Netlify](https://netlify.com)
   - Drag and drop the `frontend` folder to Netlify
   - Or connect your GitHub repository and set publish directory to `frontend`

3. **Custom Domain** (Optional):
   - Set up `aifreeset.netlify.app` or your custom domain
   - Update CORS settings in backend if needed

## 📡 API Documentation

### Endpoints

#### Health Check
- **GET** `/`
- **Response**: Server status and information

#### Chat Completion
- **POST** `/api/chat`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "message": "Your question here"
  }
  ```
- **Success Response**:
  ```json
  {
    "success": true,
    "response": "AI generated response",
    "model": "qwen/qwen3-32b",
    "timestamp": "2024-01-01T12:00:00.000Z"
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Error description",
    "details": "Additional context (optional)"
  }
  ```

## 🔧 Configuration

### CORS Settings

The backend is configured to accept requests from:
- `https://aifreeset.netlify.app`
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5500`

### OpenRouter Settings

- **Model**: `qwen/qwen3-32b`
- **API Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Headers**:
  - `Authorization`: Bearer token with provided API key
  - `HTTP-Referer`: `https://aifreeset.netlify.app`
  - `X-Title`: `AI Free Set`

## 🎯 Features

### Backend Features
- ✅ Express.js server with ES modules
- ✅ OpenRouter API integration
- ✅ Environment-based configuration
- ✅ CORS enabled for specific origins
- ✅ Comprehensive error handling
- ✅ Request timeout handling (30s)
- ✅ Input validation
- ✅ JSON-only responses

### Frontend Features
- ✅ Modern, responsive chat interface
- ✅ Real-time message display
- ✅ Typing indicator with animation
- ✅ Character count (2000 limit)
- ✅ Mobile-friendly design
- ✅ Error handling and user feedback
- ✅ Keyboard shortcuts (Enter to send)
- ✅ Auto-scroll to latest messages
- ✅ Message history preservation

## 🐛 Troubleshooting

### Common Issues

1. **CORS Error**:
   - Ensure your frontend URL is added to CORS origins in `server.js`
   - Check that you're using the correct backend URL in `script.js`

2. **API Key Issues**:
   - Verify the API key is correctly set in `.env`
   - Check that the key has sufficient credits
   - Ensure no extra spaces in the key

3. **Connection Issues**:
   - Verify backend is running and accessible
   - Check firewall settings
   - Ensure correct ports are used

4. **Deployment Issues**:
   - Check environment variables are set correctly
   - Verify build logs for errors
   - Ensure start command is correct

### Logs and Debugging

- Backend logs: Check server console for error messages
- Frontend logs: Open browser DevTools → Console
- Network issues: Check Network tab in DevTools

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**© 2024 AI Free Set. Powered by OpenRouter & Qwen 3.**