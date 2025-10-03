import os
import requests
import pysrt
import tempfile
from app.config import settings
from app.db.mongodb import subtitles_coll

BASE_URL = "https://api.opensubtitles.com/api/v1"

class OpenSubClient:
    def __init__(self):
        self.api_key = settings.OPENSUB_API_KEY
        self.username = settings.OPENSUB_USERNAME
        self.password = settings.OPENSUB_PASSWORD
        self.token = None

    def headers(self, auth=False):
        h = {
            "Api-Key": self.api_key, 
            "Content-Type": "application/json",
            "User-Agent": "CineShazam v1.0.0"
        }
        if auth and self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def login(self):
        if not self.username or not self.password:
            return None
        url = f"{BASE_URL}/login"
        res = requests.post(url, json={"username": self.username, "password": self.password}, headers=self.headers())
        res.raise_for_status()
        self.token = res.json().get("token")
        return self.token

    def search_subtitles(self, imdb_id, language="en"):
        params = {"imdb_id": imdb_id, "languages": language}
        res = requests.get(f"{BASE_URL}/subtitles", headers=self.headers(), params=params)
        res.raise_for_status()
        return res.json().get("data", [])

    def download_file(self, file_id):
        if not self.token:
            self.login()
        res = requests.post(f"{BASE_URL}/download", json={"file_id": file_id}, headers=self.headers(auth=True))
        res.raise_for_status()
        link = res.json().get("link")
        return link

def parse_srt_to_docs(srt_text, movie_id, movie_title):
    subs = pysrt.from_string(srt_text)
    docs = []
    for s in subs:
        # convert start/end to seconds
        def to_seconds(t):
            return t.hours*3600 + t.minutes*60 + t.seconds + t.milliseconds/1000.0

        docs.append({
            "movie_id": movie_id,
            "movie_title": movie_title,
            "text": s.text.replace("\n", " ").strip(),
            "start_time": to_seconds(s.start),
            "end_time": to_seconds(s.end)
        })
    return docs

def fetch_and_store(imdb_id, movie_title=None, language="en"):
    client = OpenSubClient()
    data = client.search_subtitles(imdb_id, language=language)
    if not data:
        print(f"No subtitles found for {imdb_id}")
        return 0

    # take first file of first match
    entry = data[0]
    files = entry.get("attributes", {}).get("files", [])
    if not files:
        print(f"No files for {imdb_id}")
        return 0
    file_id = files[0].get("file_id")
    if not file_id:
        print("file id missing")
        return 0

    link = client.download_file(file_id)
    # download text
    r = requests.get(link)
    r.raise_for_status()
    srt_text = r.text

    docs = parse_srt_to_docs(srt_text, imdb_id, movie_title or imdb_id)
    if docs:
        # insert many
        subtitles_coll.insert_many(docs)
        print(f"Inserted {len(docs)} subtitles for {imdb_id} / {movie_title}")
        return len(docs)
    print("No parsed docs")
    return 0
