#!/usr/bin/env python3
"""
Production startup script for Cine Shazam Backend
"""
import os
import subprocess
import sys
from app.config import settings

if __name__ == "__main__":
    if settings.DEBUG:
        # Use uvicorn for development
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level="debug",
            access_log=True,
        )
    else:
        # Use gunicorn for production
        gunicorn_cmd = [
            "gunicorn",
            "app.main:app",
            "-c", "gunicorn.conf.py",  # Use config file
        ]
        
        print(f"Starting production server with Gunicorn...")
        print(f"Command: {' '.join(gunicorn_cmd)}")
        
        try:
            subprocess.run(gunicorn_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Gunicorn failed to start: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("Server stopped by user")
            sys.exit(0)
