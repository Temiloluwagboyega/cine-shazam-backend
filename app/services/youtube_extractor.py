import logging
import tempfile
import os
import random
from typing import Optional, Dict, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
import yt_dlp

logger = logging.getLogger(__name__)

class YouTubeExtractor:
	"""Service for extracting audio from YouTube videos"""
	
	def __init__(self):
		self.executor = ThreadPoolExecutor(max_workers=2)
		
	def _get_ydl_opts(self, output_path: str) -> Dict:
		"""Get yt-dlp options for audio extraction"""
		return {
			'format': 'bestaudio/best',
			'outtmpl': output_path.replace('.wav', '.%(ext)s'),
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'wav',
				'preferredquality': '192',
			}],
			'noplaylist': True,
			'quiet': True,
			'no_warnings': True,
			'extract_flat': False,
		}
	
	async def extract_audio_from_url(self, youtube_url: str, max_duration: int = 300) -> Optional[Tuple[str, Dict]]:
		"""
		Extract audio from YouTube URL using streaming approach
		
		Args:
			youtube_url: YouTube video URL
			max_duration: Maximum duration in seconds to extract (default: 5 minutes)
			
		Returns:
			Tuple of (audio_file_path, video_info) or None if failed
		"""
		try:
			logger.info(f"Streaming audio from YouTube URL: {youtube_url}")
			
			# Create temporary file for audio
			temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
			temp_file.close()
			audio_path = temp_file.name
			
			# Get video info first
			video_info = await self._get_video_info(youtube_url)
			if not video_info:
				logger.error("Failed to get video info")
				return None
			
			# Stream audio using yt-dlp with FFmpeg
			loop = asyncio.get_event_loop()
			success = await loop.run_in_executor(
				self.executor,
				self._stream_audio_with_ydlp,
				youtube_url,
				audio_path,
				max_duration
			)
			
			if success and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
				logger.info(f"YouTube audio streaming completed: {audio_path}")
				return audio_path, video_info
			else:
				logger.error("Failed to stream audio from YouTube")
				return None
				
		except Exception as e:
			logger.error(f"Error streaming audio from YouTube: {str(e)}")
			return None
	
	def _stream_audio_with_ydlp(self, youtube_url: str, output_path: str, max_duration: int) -> bool:
		"""Stream audio using yt-dlp with FFmpeg in a separate thread"""
		try:
			# Get the best audio URL without downloading
			ydl_opts = {
				'format': 'bestaudio/best',
				'quiet': True,
				'no_warnings': True,
				'extract_flat': False,
			}
			
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(youtube_url, download=False)
				audio_url = info.get('url')
				
				if not audio_url:
					logger.error("No audio URL found")
					return False
				
				# Use FFmpeg to stream and convert audio
				import subprocess
				ffmpeg_cmd = [
					'ffmpeg',
					'-i', audio_url,
					'-t', str(max_duration),  # Limit duration
					'-acodec', 'pcm_s16le',   # Convert to WAV
					'-ac', '1',               # Mono
					'-ar', '16000',           # 16kHz sample rate
					'-y',                     # Overwrite output file
					output_path
				]
				
				logger.info(f"Streaming audio with FFmpeg: {audio_url[:50]}...")
				result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
				
				if result.returncode == 0:
					logger.info(f"Audio streaming completed successfully")
					return True
				else:
					logger.error(f"FFmpeg streaming failed: {result.stderr}")
					return False
					
		except Exception as e:
			logger.error(f"Error in audio streaming: {str(e)}")
			return False

	def _extract_with_ydlp(self, youtube_url: str, ydl_opts: Dict) -> Optional[Tuple[str, Dict]]:
		"""Extract audio using yt-dlp in a separate thread"""
		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				# Get video info first
				info = ydl.extract_info(youtube_url, download=False)
				
				# Extract audio
				ydl.download([youtube_url])
				
				# Prepare video info
				video_info = {
					'title': info.get('title', 'Unknown'),
					'duration': info.get('duration', 0),
					'uploader': info.get('uploader', 'Unknown'),
					'upload_date': info.get('upload_date', 'Unknown'),
					'view_count': info.get('view_count', 0),
					'description': info.get('description', ''),
					'url': youtube_url
				}
				
				# Find the downloaded file - yt-dlp will create the file with the correct extension
				base_path = ydl_opts['outtmpl'].replace('.%(ext)s', '')
				# Look for the actual downloaded file
				possible_extensions = ['.wav', '.webm', '.m4a', '.mp3']
				audio_path = None
				
				for ext in possible_extensions:
					test_path = base_path + ext
					if os.path.exists(test_path):
						audio_path = test_path
						break
				
				if not audio_path:
					logger.error(f"Could not find downloaded audio file with base path: {base_path}")
					return None
				
				return audio_path, video_info
				
		except Exception as e:
			logger.error(f"yt-dlp extraction failed: {str(e)}")
			return None
	
	async def _get_video_info(self, youtube_url: str) -> Optional[Dict]:
		"""Get video information without downloading"""
		try:
			ydl_opts = {
				'quiet': True,
				'no_warnings': True,
			}
			
			loop = asyncio.get_event_loop()
			info = await loop.run_in_executor(
				self.executor,
				self._get_info_sync,
				youtube_url,
				ydl_opts
			)
			
			if info:
				return {
					'title': info.get('title', 'Unknown'),
					'duration': info.get('duration', 0),
					'uploader': info.get('uploader', 'Unknown'),
					'upload_date': info.get('upload_date', 'Unknown'),
					'view_count': info.get('view_count', 0),
					'description': info.get('description', '')[:500],  # Limit description length
					'url': youtube_url
				}
			return None
			
		except Exception as e:
			logger.error(f"Error getting video info: {str(e)}")
			return None
	
	def _extract_audio_sync(self, youtube_url: str, output_path: str, max_duration: int) -> bool:
		"""Synchronous audio extraction (runs in thread pool)"""
		try:
			ydl_opts = self._get_ydl_opts(output_path)
			
			# If video is longer than max_duration, extract only a portion
			if max_duration < 3600:  # Less than 1 hour
				ydl_opts['postprocessors'] = [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'wav',
					'preferredquality': '192',
				}]
			
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				ydl.download([youtube_url])
			
			return os.path.exists(output_path)
			
		except Exception as e:
			logger.error(f"Error in sync audio extraction: {str(e)}")
			return False
	
	def _get_info_sync(self, youtube_url: str, ydl_opts: Dict) -> Optional[Dict]:
		"""Synchronous info extraction (runs in thread pool)"""
		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(youtube_url, download=False)
				return info
		except Exception as e:
			logger.error(f"Error in sync info extraction: {str(e)}")
			return None
	
	async def extract_audio_segment(self, youtube_url: str, start_time: int, duration: int) -> Optional[str]:
		"""
		Extract a specific audio segment from YouTube video
		
		Args:
			youtube_url: YouTube video URL
			start_time: Start time in seconds
			duration: Duration in seconds
			
		Returns:
			Path to extracted audio file or None if failed
		"""
		try:
			logger.info(f"Extracting audio segment: {start_time}s to {start_time + duration}s")
			
			# Create temporary file for audio
			temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
			temp_file.close()
			audio_path = temp_file.name
			
			ydl_opts = {
				'format': 'bestaudio/best',
				'outtmpl': audio_path,
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'wav',
					'preferredquality': '192',
				}],
				'postprocessor_args': [
					'-ss', str(start_time),
					'-t', str(duration)
				],
				'noplaylist': True,
				'quiet': True,
				'no_warnings': True,
			}
			
			loop = asyncio.get_event_loop()
			success = await loop.run_in_executor(
				self.executor,
				self._extract_segment_sync,
				youtube_url,
				ydl_opts
			)
			
			if success and os.path.exists(audio_path):
				logger.info(f"Successfully extracted audio segment to: {audio_path}")
				return audio_path
			else:
				logger.error("Failed to extract audio segment")
				if os.path.exists(audio_path):
					os.unlink(audio_path)
				return None
				
		except Exception as e:
			logger.error(f"Error extracting audio segment: {str(e)}")
			return None
	
	def _extract_segment_sync(self, youtube_url: str, ydl_opts: Dict) -> bool:
		"""Synchronous segment extraction (runs in thread pool)"""
		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				ydl.download([youtube_url])
			return True
		except Exception as e:
			logger.error(f"Error in sync segment extraction: {str(e)}")
			return False
	
	async def stream_and_transcribe_realtime(self, youtube_url: str, max_duration: int = 60) -> Optional[Dict]:
		"""
		Stream audio and transcribe in real-time chunks for faster processing
		
		Args:
			youtube_url: YouTube video URL
			max_duration: Maximum duration in seconds to process
			
		Returns:
			Dictionary with transcription results or None if failed
		"""
		try:
			logger.info(f"Real-time streaming and transcribing: {youtube_url}")
			
			# Get video info first
			video_info = await self._get_video_info(youtube_url)
			if not video_info:
				logger.error("Failed to get video info")
				return None
			
			# Stream audio in chunks and transcribe each chunk
			loop = asyncio.get_event_loop()
			result = await loop.run_in_executor(
				self.executor,
				self._stream_and_transcribe_chunks,
				youtube_url,
				max_duration
			)
			
			if result:
				result['video_info'] = video_info
				logger.info(f"Real-time streaming completed successfully")
				return result
			else:
				logger.error("Failed to stream and transcribe in real-time")
				return None
				
		except Exception as e:
			logger.error(f"Error in real-time streaming: {str(e)}")
			return None

	def _stream_and_transcribe_chunks(self, youtube_url: str, max_duration: int) -> Optional[Dict]:
		"""Stream audio in chunks and transcribe each chunk"""
		try:
			import subprocess
			import tempfile
			import speech_recognition as sr
			
			# Get the best audio URL
			ydl_opts = {
				'format': 'bestaudio/best',
				'quiet': True,
				'no_warnings': True,
				'extract_flat': False,
			}
			
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(youtube_url, download=False)
				audio_url = info.get('url')
				
				if not audio_url:
					logger.error("No audio URL found")
					return None
			
			# Process audio in 10-second chunks
			chunk_duration = 10
			chunks = []
			all_text = []
			
			for start_time in range(0, min(max_duration, 60), chunk_duration):  # Limit to 60 seconds for testing
				# Create temporary file for this chunk
				chunk_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
				chunk_file.close()
				chunk_path = chunk_file.name
				
				try:
					# Extract audio chunk using FFmpeg
					ffmpeg_cmd = [
						'ffmpeg',
						'-i', audio_url,
						'-ss', str(start_time),
						'-t', str(chunk_duration),
						'-acodec', 'pcm_s16le',
						'-ac', '1',
						'-ar', '16000',
						'-y',
						chunk_path
					]
					
					result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
					
					if result.returncode == 0 and os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 0:
						# Transcribe this chunk
						try:
							r = sr.Recognizer()
							with sr.AudioFile(chunk_path) as source:
								audio = r.record(source)
								text = r.recognize_google(audio)
								all_text.append(text)
								logger.info(f"Chunk {start_time}-{start_time+chunk_duration}s: {text[:50]}...")
						except Exception as e:
							logger.warning(f"Failed to transcribe chunk {start_time}: {e}")
					
				finally:
					# Clean up chunk file
					if os.path.exists(chunk_path):
						os.unlink(chunk_path)
			
			if all_text:
				full_text = ' '.join(all_text)
				return {
					'transcription': {
						'text': full_text,
						'language': 'en',
						'duration': len(all_text) * chunk_duration
					},
					'chunks_processed': len(all_text),
					'chunk_duration': chunk_duration
				}
			else:
				logger.error("No audio chunks were successfully transcribed")
				return None
				
		except Exception as e:
			logger.error(f"Error in chunk streaming: {str(e)}")
			return None

	def cleanup_temp_file(self, file_path: str):
		"""Clean up temporary file"""
		try:
			if os.path.exists(file_path):
				os.unlink(file_path)
				logger.info(f"Cleaned up temporary file: {file_path}")
		except Exception as e:
			logger.error(f"Error cleaning up temp file: {str(e)}")
	
	def __del__(self):
		"""Cleanup executor on destruction"""
		if hasattr(self, 'executor'):
			self.executor.shutdown(wait=False)
