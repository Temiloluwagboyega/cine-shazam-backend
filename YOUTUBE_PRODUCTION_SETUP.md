# YouTube Production Setup Guide

This guide explains how to handle YouTube bot detection and authentication in production environments.

## 🚨 The Problem

YouTube has implemented aggressive bot detection that blocks automated requests. This affects:
- Production deployments (Render, Heroku, AWS, etc.)
- Server environments without browser cookies
- Automated systems trying to access YouTube videos

## 🔧 Solutions

### Option 1: Environment Variable Cookies (Recommended for Production)

1. **Export YouTube Cookies from Your Browser**
   ```bash
   # Run the helper script locally
   python export_youtube_cookies.py
   ```

2. **Get Your YouTube Cookies**
   - Install "cookies.txt" extension in Chrome/Firefox
   - Go to YouTube and sign in to your account
   - Export cookies for youtube.com domain
   - Copy the exported cookies

3. **Set Environment Variable in Production**
   ```bash
   # In your production environment (Render, Heroku, etc.)
   YOUTUBE_COOKIES=".youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	your_cookie_value
   .youtube.com	TRUE	/	FALSE	1234567890	PREF	hl=en&tz=UTC
   .youtube.com	TRUE	/	FALSE	1234567890	YSC	your_session_cookie"
   ```

4. **Deploy with Cookies**
   - Add the `YOUTUBE_COOKIES` environment variable to your production deployment
   - The system will automatically use these cookies for YouTube requests

### Option 2: Alternative Video Sources

For videos that don't require authentication, the system will automatically fall back to:
- YouTube oEmbed API (for basic video info)
- Alternative extraction methods
- Basic video ID extraction

### Option 3: Proxy/VPN Solution

If cookies don't work, you can:
1. Use a proxy service that handles YouTube authentication
2. Deploy from a region with less restrictive YouTube access
3. Use a VPN service in your deployment environment

## 🚀 Production Deployment Steps

### For Render.com

1. **Add Environment Variable**
   ```bash
   # In Render dashboard, add:
   YOUTUBE_COOKIES=your_cookies_here
   ```

2. **Deploy**
   - The system will automatically detect and use the cookies
   - No additional configuration needed

### For Heroku

1. **Set Environment Variable**
   ```bash
   heroku config:set YOUTUBE_COOKIES="your_cookies_here"
   ```

2. **Deploy**
   ```bash
   git push heroku main
   ```

### For AWS/Docker

1. **Add to Environment**
   ```dockerfile
   ENV YOUTUBE_COOKIES="your_cookies_here"
   ```

2. **Or use AWS Systems Manager**
   ```bash
   aws ssm put-parameter --name "/cine-shazam/youtube-cookies" --value "your_cookies_here" --type "SecureString"
   ```

## 🔍 Testing

### Test Cookie Setup
```bash
# Test locally with cookies
export YOUTUBE_COOKIES="your_cookies_here"
python -c "from app.services.youtube_extractor import YouTubeExtractor; print('Cookies loaded successfully')"
```

### Test Production
```bash
# Test the production endpoint
curl -X POST https://your-domain.com/api/v1/identify-from-youtube-streaming \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtu.be/FPczjPUHthY?si=oiaXzNaae4ZEj6rU"}'
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Sign in to confirm you're not a bot"**
   - Solution: Add valid YouTube cookies via `YOUTUBE_COOKIES` environment variable

2. **"Failed to extract any player response"**
   - Solution: Try different cookie values or use alternative methods

3. **Cookies not working**
   - Check cookie format (must be Netscape format)
   - Ensure cookies are not expired
   - Try exporting fresh cookies from browser

### Debug Mode

Enable debug logging to see which methods are being tried:
```bash
export DEBUG=true
```

## 📋 Cookie Format

Cookies must be in Netscape format:
```
domain	flag	path	secure	expiration	name	value
.youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	abc123
.youtube.com	TRUE	/	FALSE	1234567890	PREF	hl=en&tz=UTC
```

## 🔒 Security Notes

- **Never commit cookies to version control**
- **Use environment variables for production**
- **Rotate cookies regularly**
- **Use secure storage for sensitive cookies**

## 📞 Support

If you're still having issues:
1. Check the logs for specific error messages
2. Try the alternative methods (oEmbed API)
3. Consider using a different video source
4. Contact support with specific error details

## 🔄 Fallback Methods

The system automatically tries multiple approaches:
1. **Standard**: Full bot detection bypass with cookies
2. **Minimal**: Basic options without complex headers  
3. **Aggressive**: Different user agents and referers
4. **Production**: Optimized for server environments
5. **Alternative**: oEmbed API and basic video ID extraction

If one method fails, the system automatically tries the next one.
