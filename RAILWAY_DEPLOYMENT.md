# Railway Deployment Guide for AiFreeSet Node.js Backend

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository
Make sure your repository contains:
- `server.js` (main application file)
- `package.json` (dependencies and scripts)
- `.env.example` (environment variable template)

### 2. Deploy to Railway

1. **Visit Railway**: Go to [railway.app](https://railway.app)
2. **Sign Up/Login**: Use GitHub, Google, or email
3. **New Project**: Click "New Project"
4. **Deploy from GitHub**: Select "Deploy from GitHub repo"
5. **Select Repository**: Choose your backend repository
6. **Auto-Deploy**: Railway will automatically detect Node.js and deploy

### 3. Configure Environment Variables

In Railway dashboard:
1. Go to your project
2. Click "Variables" tab
3. Add these variables:

```
QWEN_API_KEY=your_qwen_api_key_here
REMOVEBG_API_KEY=your_removebg_api_key_here
UNWATERMARK_API_KEY=your_unwatermark_api_key_here
NODE_ENV=production
```

### 4. Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Click "Domains"
3. Add your custom domain or use the provided Railway domain

### 5. Monitor Deployment

1. Check "Deployments" tab for build status
2. View "Logs" tab for runtime logs
3. Test your endpoints using the provided URL

## 🔧 Railway Configuration

Railway automatically detects Node.js projects and uses these defaults:
- **Build Command**: `npm install`
- **Start Command**: `npm start`
- **Port**: Automatically assigned (Railway sets `PORT` env var)

### Custom Configuration (if needed)

Create `railway.toml` in your project root:
```toml
[build]
command = "npm install"

[deploy]
startCommand = "npm start"
restartPolicyType = "always"

[env]
NODE_ENV = "production"
```

## 🧪 Testing Your Deployment

1. **Health Check**: 
   ```
   GET https://your-app.railway.app/
   ```

2. **Test Endpoints**:
   ```bash
   # Replace YOUR_DOMAIN with your Railway URL
   curl https://your-app.railway.app/api/text \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello AI!"}'
   ```

3. **Run Test Suite**:
   ```bash
   TEST_URL=https://your-app.railway.app node test.js
   ```

## 🔄 Automatic Deployments

Railway automatically redeploys when you push to your main branch:
1. Make changes to your code
2. Commit and push to GitHub
3. Railway detects changes and redeploys
4. Monitor deployment in Railway dashboard

## 📊 Monitoring & Logs

### View Logs
1. Railway Dashboard → Your Project
2. Click "Logs" tab
3. Monitor real-time application logs

### Performance Metrics
1. Railway Dashboard → "Metrics" tab
2. View CPU, Memory, Network usage
3. Monitor response times

## 🐛 Troubleshooting

### Common Issues

**Build Fails:**
- Check `package.json` syntax
- Verify all dependencies are listed
- Check Railway build logs

**App Crashes:**
- Check environment variables are set
- Monitor runtime logs
- Verify API keys are valid

**API Not Responding:**
- Check the Railway-provided URL
- Verify CORS settings allow your frontend domain
- Test with curl or Postman

**Timeout Errors:**
- Railway has 30-second request timeout by default
- Optimize API calls and add proper error handling

### Debug Commands

```bash
# Check deployment status
curl https://your-app.railway.app/

# Test with verbose output
curl -v https://your-app.railway.app/api/text \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit API keys to git
2. **CORS**: Verify CORS origin matches your frontend domain exactly
3. **Rate Limiting**: Consider adding rate limiting for production
4. **HTTPS**: Railway provides HTTPS automatically
5. **Monitoring**: Set up alerts for errors and downtime

## 📈 Scaling & Performance

Railway automatically handles:
- **Auto-scaling**: Based on CPU/memory usage
- **Load Balancing**: Across multiple instances
- **CDN**: Global content delivery
- **Database**: Shared PostgreSQL if needed

## 💰 Pricing

- **Hobby Plan**: $5/month with 512MB RAM, 1GB disk
- **Pro Plan**: $20/month with 8GB RAM, 100GB disk
- **Team Plan**: Custom pricing for teams

## 🚀 Go Live Checklist

- [ ] Environment variables configured
- [ ] Custom domain added (optional)
- [ ] CORS origin matches frontend domain
- [ ] All endpoints tested and working
- [ ] Error handling and fallbacks tested
- [ ] Monitoring and alerts configured
- [ ] Frontend updated with new backend URL

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: For code-related problems

Your AiFreeSet backend is now ready for production on Railway! 🎉