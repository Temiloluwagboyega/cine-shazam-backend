# Cine Shazam Backend - Production Deployment Guide

## 🚀 Render Deployment

### 1. Prerequisites
- MongoDB Atlas account and cluster
- Render account
- GitHub repository with your code

### 2. Environment Variables Setup

In your Render dashboard, set these environment variables:

#### Required Variables:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=cine_shazam
FRONTEND_URL=https://your-frontend-domain.com
```

#### Optional Variables:
```
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
MAX_FILE_SIZE=104857600
UPLOAD_TIMEOUT=300
CHUNK_MAX_SECONDS=10
WHISPER_MODEL=base
```

### 3. Render Service Configuration

1. **Service Type**: Web Service
2. **Environment**: Python 3
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python start.py`
5. **Plan**: Starter (or higher for production)

**Note**: The system automatically uses:
- **Development**: Uvicorn with hot reload
- **Production**: Gunicorn with multiple workers for better performance

### 4. MongoDB Atlas Setup

1. Create a MongoDB Atlas cluster
2. Create a database user with read/write permissions
3. Whitelist Render's IP addresses (or use 0.0.0.0/0 for all IPs)
4. Get your connection string and set it as `MONGO_URI`

### 5. Data Population

After deployment, run the data processing script to populate your MongoDB:

```bash
# This should be run locally or on a separate service
python process_to_mongodb.py
```

### 6. CORS Configuration

The system is configured to allow requests from:
- `http://localhost:3000` (React dev)
- `http://localhost:5173` (Vite dev)
- `https://*.vercel.app` (Vercel deployments)
- `https://*.netlify.app` (Netlify deployments)
- `https://*.render.com` (Render deployments)
- Your custom frontend URL (set via `FRONTEND_URL`)

## 🔧 Local Development

### 1. Environment Setup
```bash
# Copy the template
cp config.template .env

# Edit .env with your values
nano .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server
```bash
# Using the production script
python start.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Production Endpoints:
- `GET /` - API information
- `GET /health` - Health check
- `POST /api/v1/identify-from-video` - Video upload processing
- `POST /api/v1/identify-from-youtube` - YouTube processing (download)
- `POST /api/v1/identify-from-youtube-streaming` - YouTube streaming (real-time)
- `POST /api/v1/identify-from-text` - Text input processing
- `POST /api/v1/identify-from-text-enhanced` - Enhanced text processing
- `GET /api/v1/test-kaggle-dataset` - Dataset testing

## 🔒 Security Considerations

1. **CORS**: Configured for specific origins
2. **File Upload**: Limited to 100MB
3. **Timeout**: 5-minute upload timeout
4. **Environment**: Production mode by default
5. **Logging**: Structured logging for monitoring

## 📊 Monitoring

The application includes:
- Health check endpoint
- Structured logging
- Error handling
- Request/response logging

## 🚨 Troubleshooting

### Common Issues:

1. **MongoDB Connection Failed**
   - Check `MONGO_URI` format
   - Verify IP whitelist in MongoDB Atlas
   - Check database user permissions

2. **CORS Errors**
   - Verify `FRONTEND_URL` is set correctly
   - Check if your frontend domain is in allowed origins

3. **File Upload Issues**
   - Check `MAX_FILE_SIZE` setting
   - Verify `UPLOAD_TIMEOUT` is sufficient

4. **YouTube Processing Fails**
   - Ensure `yt-dlp` is properly installed
   - Check if FFmpeg is available in the environment

## 📈 Performance Optimization

1. **Database Indexing**: Ensure MongoDB has proper indexes
2. **Caching**: Consider adding Redis for caching
3. **CDN**: Use CDN for static assets
4. **Load Balancing**: Use multiple workers in production
5. **Gunicorn Configuration**: Optimized for production with:
   - Multiple worker processes
   - Uvicorn worker class for async support
   - Request timeouts and limits
   - Graceful worker restarts

### Gunicorn Settings:
- **Workers**: CPU cores × 2 + 1
- **Worker Class**: `uvicorn.workers.UvicornWorker`
- **Timeout**: 300 seconds (5 minutes)
- **Max Requests**: 1000 per worker (prevents memory leaks)
- **Keep-Alive**: 2 seconds

## 🔄 Updates and Maintenance

1. **Dependencies**: Keep requirements.txt updated
2. **Security**: Regular security updates
3. **Monitoring**: Monitor logs and performance
4. **Backups**: Regular MongoDB backups
