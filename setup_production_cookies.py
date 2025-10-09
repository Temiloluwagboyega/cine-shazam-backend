#!/usr/bin/env python3
"""
Production Cookie Setup Helper

This script helps you set up YouTube cookies for production deployment.
It generates the environment variable format needed for production systems.
"""

import os
import sys
from pathlib import Path

def read_cookie_file():
    """Read cookies from the local cookie file"""
    cookie_file = Path("cookies/youtube_cookies.txt")
    
    if not cookie_file.exists():
        print("❌ Cookie file not found!")
        print("Run 'python export_youtube_cookies.py' first to create the cookie file.")
        return None
    
    with open(cookie_file, 'r') as f:
        content = f.read()
    
    # Extract actual cookie lines (not comments)
    cookie_lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            cookie_lines.append(line)
    
    if not cookie_lines:
        print("❌ No cookies found in the file!")
        print("Please add your YouTube cookies to cookies/youtube_cookies.txt")
        return None
    
    return '\n'.join(cookie_lines)

def generate_env_variable(cookies):
    """Generate the environment variable format"""
    # Escape quotes and newlines for environment variable
    escaped_cookies = cookies.replace('"', '\\"').replace('\n', '\\n')
    return f'YOUTUBE_COOKIES="{escaped_cookies}"'

def show_deployment_instructions(env_var):
    """Show deployment instructions for different platforms"""
    
    print("\n🚀 PRODUCTION DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    
    print("\n📋 Environment Variable to Set:")
    print("-" * 30)
    print(env_var)
    
    print("\n🔧 Platform-Specific Instructions:")
    print("-" * 35)
    
    print("\n🔵 Render.com:")
    print("1. Go to your Render dashboard")
    print("2. Select your service")
    print("3. Go to Environment tab")
    print("4. Add new environment variable:")
    print(f"   Key: YOUTUBE_COOKIES")
    print(f"   Value: {env_var.split('=', 1)[1]}")
    print("5. Save and redeploy")
    
    print("\n🟠 Heroku:")
    print("1. Run this command:")
    print(f"   heroku config:set YOUTUBE_COOKIES='{env_var.split('=', 1)[1]}'")
    print("2. Or use Heroku dashboard:")
    print("   - Go to Settings tab")
    print("   - Add Config Var")
    print("   - Key: YOUTUBE_COOKIES")
    print("   - Value: [paste the cookie content]")
    
    print("\n🟢 AWS/Docker:")
    print("1. Add to your Dockerfile:")
    print(f"   ENV YOUTUBE_COOKIES='{env_var.split('=', 1)[1]}'")
    print("2. Or use AWS Systems Manager:")
    print("   aws ssm put-parameter --name \"/cine-shazam/youtube-cookies\" \\")
    print(f"     --value \"{env_var.split('=', 1)[1]}\" --type \"SecureString\"")
    
    print("\n🟡 Vercel:")
    print("1. Go to your project dashboard")
    print("2. Go to Settings > Environment Variables")
    print("3. Add new variable:")
    print("   Name: YOUTUBE_COOKIES")
    print(f"   Value: {env_var.split('=', 1)[1]}")
    print("4. Redeploy your application")

def main():
    print("🍪 Production Cookie Setup Helper")
    print("=" * 40)
    
    # Read cookies from file
    cookies = read_cookie_file()
    if not cookies:
        return
    
    print(f"✅ Found {len(cookies.split(chr(10)))} cookie lines")
    
    # Generate environment variable
    env_var = generate_env_variable(cookies)
    
    # Show deployment instructions
    show_deployment_instructions(env_var)
    
    print("\n✅ Setup complete!")
    print("After setting the environment variable, restart your production service.")
    
    # Ask if user wants to copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(env_var)
        print("\n📋 Environment variable copied to clipboard!")
    except ImportError:
        print("\n💡 Tip: Install pyperclip to copy to clipboard automatically:")
        print("   pip install pyperclip")

if __name__ == "__main__":
    main()
