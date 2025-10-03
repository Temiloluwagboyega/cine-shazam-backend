import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB", "cine_shazam")

    OPENSUB_API_KEY = os.getenv("OPENSUBTITLES_API_KEY")
    OPENSUB_USERNAME = os.getenv("OPENSUBTITLES_USERNAME", "")
    OPENSUB_PASSWORD = os.getenv("OPENSUBTITLES_PASSWORD", "")

    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "subtitles.faiss")
    FAISS_META_PATH = os.getenv("FAISS_META_PATH", "subtitles_meta.pkl")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    CHUNK_MAX_SECONDS = int(os.getenv("CHUNK_MAX_SECONDS", "10"))

settings = Settings()
