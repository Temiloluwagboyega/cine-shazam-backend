# app/services/audio_transcribe.py
import tempfile
import os
import subprocess
import whisper
from pytube import YouTube
from moviepy.editor import VideoFileClip
from app.config import settings

# load whisper model once (synchronous)
_whisper_model = None
def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
    return _whisper_model

def extract_audio_from_video(video_path, out_wav=None):
    if out_wav is None:
        out_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(out_wav, verbose=False, logger=None)
    clip.close()
    return out_wav

def download_youtube_audio(url, out_path=None):
    # download best audio to a temp file (mp4/m4a) then convert to wav
    tmp = out_path or tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    stream.download(filename=tmp)
    # convert with ffmpeg to wav
    wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    cmd = ["ffmpeg", "-y", "-i", tmp, "-ar", "16000", "-ac", "1", wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        os.remove(tmp)
    except:
        pass
    return wav

def transcribe_audio_file(wav_path):
    model = get_whisper()
    result = model.transcribe(wav_path)
    return result.get("text","")
