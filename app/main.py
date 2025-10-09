from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.config import settings

from app.routes.movie_identification import router as movie_identification_router

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cine Shazam Backend",
    description="Movie identification service using audio/video processing and MongoDB database",
    version="1.0.0"
)

# Configure CORS origins based on environment
def get_cors_origins():
	"""Get CORS origins based on environment variables"""
	origins = [
		"http://localhost:3000",  # React dev server
		"http://localhost:3001",  # Alternative React port
		"http://localhost:5173",  # Vite dev server
		"http://localhost:8080",  # Vue dev server
	]
	
	# Add production origins from environment variables
	if os.getenv("FRONTEND_URL"):
		origins.append(os.getenv("FRONTEND_URL"))
	
	# Add specific production domains
	origins.extend([
		"https://cine-shazam.vercel.app",  # Your specific Vercel deployment
		"https://cine-shazam.netlify.app",  # Netlify (if used)
		"https://cine-shazam.onrender.com",  # Render (if used)
	])
	
	# For production, allow all origins to avoid CORS issues
	# In development, also allow all origins
	origins = ["*"]
	
	return origins

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(movie_identification_router)

@app.get("/")
async def root():
    return {
        "message": "Cine Shazam Backend API",
        "version": "1.0.0",
        "status": "running",
				"endpoints": {
					"video_upload": "/api/v1/identify-from-video",
					"youtube_url": "/api/v1/identify-from-youtube",
					"youtube_streaming": "/api/v1/identify-from-youtube-streaming",
					"text_input": "/api/v1/identify-from-text",
					"text_input_enhanced": "/api/v1/identify-from-text-enhanced",
					"test_kaggle_dataset": "/api/v1/test-kaggle-dataset",
					"health": "/api/v1/health"
				}
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cine-shazam-backend"}

