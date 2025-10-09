#!/usr/bin/env python3
"""
YouTube API Key Setup Helper

This script helps you get a YouTube Data API key for global access
to YouTube videos without requiring personal authentication.
"""

import webbrowser
import os
import sys

def show_api_setup_instructions():
    """Show step-by-step instructions for getting YouTube API key"""
    
    print("🔑 YouTube API Key Setup Guide")
    print("=" * 40)
    
    print("\n📋 Step-by-Step Instructions:")
    print("-" * 30)
    
    print("\n1️⃣ Go to Google Cloud Console")
    print("   https://console.developers.google.com/")
    
    print("\n2️⃣ Create or Select Project")
    print("   - Click 'Select a project' dropdown")
    print("   - Click 'New Project' or select existing")
    print("   - Give it a name like 'Cine Shazam'")
    
    print("\n3️⃣ Enable YouTube Data API v3")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'YouTube Data API v3'")
    print("   - Click on it and press 'Enable'")
    
    print("\n4️⃣ Create API Key")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'API Key'")
    print("   - Copy the generated API key")
    
    print("\n5️⃣ (Optional) Restrict API Key")
    print("   - Click on your API key to edit")
    print("   - Under 'API restrictions', select 'YouTube Data API v3'")
    print("   - Under 'Application restrictions', add your domain")
    
    print("\n6️⃣ Set Environment Variable")
    print("   - Add to your production environment:")
    print("   YOUTUBE_API_KEY=your_api_key_here")
    
    print("\n✅ That's it! Your API key will work for all users worldwide.")

def show_quota_info():
    """Show information about API quotas and limits"""
    
    print("\n📊 API Quota Information")
    print("=" * 30)
    
    print("\n🆓 Free Tier Limits:")
    print("   - 10,000 requests per day")
    print("   - 100 requests per 100 seconds")
    print("   - Perfect for most applications")
    
    print("\n💰 Pricing (if you exceed free tier):")
    print("   - $0.10 per 1,000 additional requests")
    print("   - Very affordable for production use")
    
    print("\n📈 Usage Examples:")
    print("   - 1,000 video lookups per day = Free")
    print("   - 10,000 video lookups per day = Free")
    print("   - 50,000 video lookups per day = $4/day")

def show_benefits():
    """Show benefits of using YouTube API over cookies"""
    
    print("\n🌟 Benefits of YouTube API")
    print("=" * 30)
    
    print("\n✅ Global Access")
    print("   - Works for all users worldwide")
    print("   - No personal authentication required")
    print("   - No browser dependencies")
    
    print("\n✅ Reliable & Official")
    print("   - Official Google API")
    print("   - High uptime and reliability")
    print("   - Rich metadata available")
    
    print("\n✅ Easy Setup")
    print("   - One-time configuration")
    print("   - No manual cookie export")
    print("   - Works in all environments")
    
    print("\n✅ Scalable")
    print("   - Handles high traffic")
    print("   - No session limitations")
    print("   - Professional solution")

def open_google_console():
    """Open Google Cloud Console in browser"""
    try:
        webbrowser.open("https://console.developers.google.com/")
        print("\n🌐 Opened Google Cloud Console in your browser")
    except Exception as e:
        print(f"\n⚠️  Could not open browser: {e}")
        print("   Please manually go to: https://console.developers.google.com/")

def show_production_setup():
    """Show production deployment instructions"""
    
    print("\n🚀 Production Deployment")
    print("=" * 30)
    
    print("\n🔵 Render.com:")
    print("   1. Go to your Render dashboard")
    print("   2. Select your service")
    print("   3. Go to Environment tab")
    print("   4. Add: YOUTUBE_API_KEY=your_api_key_here")
    print("   5. Save and redeploy")
    
    print("\n🟠 Heroku:")
    print("   1. Run: heroku config:set YOUTUBE_API_KEY=your_api_key_here")
    print("   2. Or use Heroku dashboard > Settings > Config Vars")
    
    print("\n🟢 AWS/Docker:")
    print("   1. Add to Dockerfile: ENV YOUTUBE_API_KEY=your_api_key_here")
    print("   2. Or use AWS Systems Manager Parameter Store")

def main():
    print("🎬 YouTube API Setup for Cine Shazam")
    print("=" * 50)
    
    show_benefits()
    show_api_setup_instructions()
    show_quota_info()
    show_production_setup()
    
    print("\n" + "=" * 50)
    print("🎯 Ready to get started?")
    
    # Ask if user wants to open Google Console
    try:
        response = input("\n🌐 Open Google Cloud Console now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            open_google_console()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. You can run this script again anytime!")
        return
    
    print("\n✅ Setup complete!")
    print("After getting your API key, add it to your production environment.")
    print("The system will automatically use it for all YouTube requests.")

if __name__ == "__main__":
    main()
