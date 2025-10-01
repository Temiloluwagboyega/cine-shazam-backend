import requests
import pysrt
import tempfile
import os
import time
from app.config import settings
from app.db.database import db

BASE_URL = "https://api.opensubtitles.com/api/v1"

class SubtitleLoader:
    def __init__(self):
        self.api_key = settings.OPENSUBTITLES_API_KEY
        self.username = settings.OPENSUBTITLES_USERNAME
        self.password = settings.OPENSUBTITLES_PASSWORD
        self.token = None
        
        # Validate that credentials are loaded
        if not self.api_key or not self.username or not self.password:
            raise ValueError(
                "OpenSubtitles credentials not found in environment variables. "
                "Please check your .env file contains: OPENSUBTITLES_API_KEY, "
                "OPENSUBTITLES_USERNAME, OPENSUBTITLES_PASSWORD"
            )
        
        # Rate limiting - OpenSubtitles allows 1 request per second
        self.last_request_time = 0

    def _rate_limit(self):
        """Ensure we don't exceed the 1 request per second limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < 1.0:
            sleep_time = 1.0 - time_since_last_request
            print(f"⏳ Rate limiting: waiting {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _make_request(self, method, url, **kwargs):
        """Make a request with rate limiting and retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            self._rate_limit()
            
            try:
                response = requests.request(method, url, **kwargs)
                
                if response.status_code == 429:  # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 2))
                    print(f"⏳ Rate limit hit, waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Max retries exceeded")

    def _headers(self, auth=False):
        headers = {
            "Api-Key": self.api_key, 
            "Content-Type": "application/json",
            "User-Agent": "CineShazam v1.0"
        }
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self):
        url = f"{BASE_URL}/login"
        payload = {"username": self.username, "password": self.password}
        headers = self._headers()
        
        print(f"🔐 Attempting login to OpenSubtitles API...")
        print(f"Username: {self.username}")
        
        res = self._make_request("POST", url, json=payload, headers=headers)
        
        print(f"Response status: {res.status_code}")
        
        if res.status_code != 200:
            print(f"Response content: {res.text}")
        
        res.raise_for_status()
        self.token = res.json().get("token")
        print(f"✅ Login successful, token received")

    def search_subtitles(self, imdb_id: str, lang="en"):
        if not self.token:
            self.login()
        url = f"{BASE_URL}/subtitles"
        params = {"imdb_id": imdb_id, "languages": lang}
        res = self._make_request("GET", url, headers=self._headers(auth=True), params=params)
        res.raise_for_status()
        data = res.json()
        if not data.get("data"):
            return None
        return data["data"][0]  # take the first match

    def download_subtitle(self, file_id: int):
        if not self.token:
            self.login()
        url = f"{BASE_URL}/download"
        payload = {"file_id": file_id}
        res = self._make_request("POST", url, json=payload, headers=self._headers(auth=True))
        res.raise_for_status()
        return res.json()["link"]

    async def save_to_db(self, imdb_id: str, movie_title: str, srt_path: str):
        subs = pysrt.open(srt_path)
        docs = []
        for sub in subs:
            docs.append({
                "movie": movie_title,
                "imdb_id": imdb_id,
                "text": sub.text,
                "start_time": str(sub.start),
                "end_time": str(sub.end)
            })
        if docs:
            await db["subtitles"].insert_many(docs)
            print(f"✅ Inserted {len(docs)} subtitles for {movie_title}")

    async def fetch_and_store(self, imdb_id: str, movie_title: str):
        # step 1: search
        result = self.search_subtitles(imdb_id)
        if not result:
            print(f"❌ No subtitles found for {movie_title}")
            return

        file_id = result["attributes"]["files"][0]["file_id"]

        # step 2: download link
        link = self.download_subtitle(file_id)

        # step 3: download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as tmp:
            resp = self._make_request("GET", link)
            tmp.write(resp.content)
            tmp_path = tmp.name

        # step 4: parse + insert
        await self.save_to_db(imdb_id, movie_title, tmp_path)

        # cleanup
        os.remove(tmp_path)
