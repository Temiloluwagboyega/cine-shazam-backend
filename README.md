# CineShazam Backend

A FastAPI-based backend service for video recognition and subtitle search, similar to Shazam but for movies and TV shows.

## 🎬 Features

- **Subtitle Database**: Download and store movie subtitles from OpenSubtitles API
- **Video Recognition**: Identify movies from video clips using subtitle matching
- **FastAPI Backend**: RESTful API for video upload and search
- **MongoDB Storage**: Efficient storage and retrieval of subtitle data
- **Rate Limiting**: Proper handling of OpenSubtitles API rate limits

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- OpenSubtitles API account

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cine-shazam-backend
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp config.template .env
   # Edit .env with your actual credentials
   ```

5. **Configure MongoDB**
   - Start MongoDB service
   - Update `MONGO_URI` in your `.env` file

6. **Load subtitle data**
   ```bash
   python -m app.scripts.load_subtitles
   ```

7. **Start the API server**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📁 Project Structure

```
cine-shazam-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py      # MongoDB connection
│   ├── routes/
│   │   ├── __init__.py
│   │   └── search.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── subtitle_loader.py    # OpenSubtitles integration
│   │   └── subtitle_service.py   # Subtitle processing
│   └── scripts/
│       └── load_subtitles.py     # Data loading script
├── requirements.txt
├── config.template
├── .gitignore
└── README.md
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=cine_shazam

# OpenSubtitles API Configuration
OPENSUBTITLES_API_KEY=your_api_key_here
OPENSUBTITLES_USERNAME=your_username_here
OPENSUBTITLES_PASSWORD=your_password_here
```

## 📊 API Endpoints

- `GET /` - Health check
- `POST /search` - Search for movie by video clip
- `GET /subtitles/{movie_id}` - Get subtitles for a movie

## 🎯 Usage

### Loading Subtitle Data

The script loads subtitles for popular movies:

```bash
python -m app.scripts.load_subtitles
```

This will:
1. Connect to OpenSubtitles API
2. Download subtitles for configured movies
3. Parse and store subtitle data in MongoDB
4. Handle rate limiting automatically

### Searching for Movies

Upload a video clip to identify the movie:

```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: multipart/form-data" \
     -F "video=@your_video_clip.mp4"
```

## 🛠️ Development

### Adding New Movies

Edit `app/scripts/load_subtitles.py` to add more movies:

```python
movies = [
    {"imdb_id": "0133093", "title": "The Matrix"},
    {"imdb_id": "1375666", "title": "Inception"},
    # Add more movies here
]
```

### Running Tests

```bash
pytest
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions, please open an issue on GitHub.
