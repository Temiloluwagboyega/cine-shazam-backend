import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB", "cine_shazam")
    
    # Speech-to-Text Configuration
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    CHUNK_MAX_SECONDS = int(os.getenv("CHUNK_MAX_SECONDS", "10"))
    
    # Environment Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Frontend Configuration
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB in bytes
    UPLOAD_TIMEOUT = int(os.getenv("UPLOAD_TIMEOUT", "300"))  # 5 minutes

settings = Settings()
