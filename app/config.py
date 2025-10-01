import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_DB: str = os.getenv("MONGO_DB", "cine_shazam")

    OPENSUBTITLES_API_KEY: str = os.getenv("OPENSUBTITLES_API_KEY")
    OPENSUBTITLES_USERNAME: str = os.getenv("OPENSUBTITLES_USERNAME")
    OPENSUBTITLES_PASSWORD: str = os.getenv("OPENSUBTITLES_PASSWORD")

settings = Settings()
