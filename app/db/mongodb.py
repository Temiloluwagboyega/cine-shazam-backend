import motor.motor_asyncio
from app.config import settings

# Add SSL configuration to handle connection issues
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=20000,
    socketTimeoutMS=20000
)
db = client[settings.MONGO_DB]

# For convenience: collections
movies_coll = db["movies"]          # optional movie metadata
subtitles_coll = db["subtitles"]    # one doc per subtitle line (chunk)
