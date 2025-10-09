#!/usr/bin/env python3
"""
YouTube Cookie Export Helper

This script helps you export YouTube cookies from your browser
to use with the Cine Shazam backend for accessing restricted videos.

Usage:
    python export_youtube_cookies.py

The script will create a cookies/youtube_cookies.txt file that you can
populate with your YouTube cookies.
"""

import os
import sys
import webbrowser
from pathlib import Path

def create_cookie_file():
    """Create the cookie file and provide instructions"""
    
    # Create cookies directory
    cookie_dir = Path("cookies")
    cookie_dir.mkdir(exist_ok=True)
    
    cookie_file = cookie_dir / "youtube_cookies.txt"
    
    # Create template file
    template_content = """# YouTube Cookies File
# Add your YouTube cookies here in Netscape format
# 
# INSTRUCTIONS:
# 1. Open your browser and go to YouTube
# 2. Make sure you're signed in to your Google/YouTube account
# 3. Install a cookie export extension like "cookies.txt" for Chrome/Firefox
# 4. Export cookies for youtube.com and paste them below
# 5. Remove the # from the beginning of cookie lines
#
# Format: domain	flag	path	secure	expiration	name	value
# Example (remove the # to activate):
# .youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	abc123def456
# .youtube.com	TRUE	/	FALSE	1234567890	PREF	hl=en&tz=UTC
# .youtube.com	TRUE	/	FALSE	1234567890	YSC	your_session_cookie_value
#
# IMPORTANT: Keep your cookies secure and don't share them!
"""
    
    with open(cookie_file, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Created cookie template file: {cookie_file}")
    print("\n📋 NEXT STEPS:")
    print("1. Open your browser and go to YouTube")
    print("2. Make sure you're signed in to your Google/YouTube account")
    print("3. Install a cookie export extension:")
    print("   - Chrome: 'cookies.txt' extension")
    print("   - Firefox: 'cookies.txt' extension")
    print("4. Export cookies for youtube.com")
    print("5. Paste the cookies into the file above (remove # from cookie lines)")
    print("6. Save the file and restart the Cine Shazam service")
    
    print(f"\n📁 Cookie file location: {cookie_file.absolute()}")
    
    # Try to open the file in the default editor
    try:
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{cookie_file}'")
        elif sys.platform == "win32":  # Windows
            os.system(f"notepad '{cookie_file}'")
        else:  # Linux
            os.system(f"xdg-open '{cookie_file}'")
        print("📝 Opened cookie file in your default editor")
    except Exception as e:
        print(f"⚠️  Could not open file automatically: {e}")
        print(f"   Please manually open: {cookie_file.absolute()}")

def show_browser_instructions():
    """Show instructions for different browsers"""
    
    print("\n🌐 BROWSER-SPECIFIC INSTRUCTIONS:")
    print("\n🔵 Chrome:")
    print("1. Install 'cookies.txt' extension from Chrome Web Store")
    print("2. Go to YouTube and sign in")
    print("3. Click the extension icon")
    print("4. Select 'youtube.com' domain")
    print("5. Click 'Export' and copy the cookies")
    
    print("\n🟠 Firefox:")
    print("1. Install 'cookies.txt' extension from Firefox Add-ons")
    print("2. Go to YouTube and sign in")
    print("3. Right-click on the page and select 'Export cookies'")
    print("4. Select 'youtube.com' domain")
    print("5. Copy the exported cookies")
    
    print("\n🟢 Safari:")
    print("1. Enable Developer menu: Safari > Preferences > Advanced > Show Develop menu")
    print("2. Go to YouTube and sign in")
    print("3. Develop > Show Web Inspector")
    print("4. Storage tab > Cookies > youtube.com")
    print("5. Manually copy cookie values")

def main():
    print("🍪 YouTube Cookie Export Helper")
    print("=" * 40)
    
    create_cookie_file()
    show_browser_instructions()
    
    print("\n✅ Setup complete!")
    print("After adding your cookies, restart the Cine Shazam service to use them.")

if __name__ == "__main__":
    main()
