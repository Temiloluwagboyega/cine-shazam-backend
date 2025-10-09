import os
import tempfile
import logging
import random
from typing import Optional, Dict, List
import aiofiles
from fastapi import UploadFile
import ffmpeg
import subprocess

logger = logging.getLogger(__name__)

class VideoProcessor:
	"""Service for processing uploaded video files"""
	
	def __init__(self):
		from app.config import settings
		self.supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
		self.max_file_size = settings.MAX_FILE_SIZE
	
	async def save_uploaded_file(self, file: UploadFile) -> Optional[str]:
		"""
		Save uploaded file to temporary location
		
		Args:
			file: Uploaded file from FastAPI
			
		Returns:
			Path to saved file or None if failed
		"""
		try:
			# Validate file extension
			file_extension = os.path.splitext(file.filename)[1].lower()
			if file_extension not in self.supported_formats:
				logger.error(f"Unsupported file format: {file_extension}")
				return None
			
			# Create temporary file
			temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
			temp_file_path = temp_file.name
			temp_file.close()
			
			# Save uploaded file
			async with aiofiles.open(temp_file_path, 'wb') as f:
				content = await file.read()
				
				# Check file size
				if len(content) > self.max_file_size:
					logger.error(f"File too large: {len(content)} bytes (max: {self.max_file_size})")
					os.unlink(temp_file_path)
					return None
				
				await f.write(content)
			
			logger.info(f"Saved uploaded file to: {temp_file_path}")
			return temp_file_path
			
		except Exception as e:
			logger.error(f"Error saving uploaded file: {str(e)}")
			return None
	
	async def extract_audio_from_video(self, video_path: str) -> Optional[str]:
		"""
		Extract audio from video file using moviepy
		
		Args:
			video_path: Path to video file
			
		Returns:
			Path to extracted audio file or None if failed
		"""
		try:
			logger.info(f"Extracting audio from video: {video_path}")
			
			# Create temporary file for audio
			temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
			temp_audio_path = temp_audio.name
			temp_audio.close()
			
			# Extract audio using ffmpeg
			try:
				(
					ffmpeg
					.input(video_path)
					.output(temp_audio_path, acodec='pcm_s16le', ac=1, ar='16k')
					.overwrite_output()
					.run(quiet=True)
				)
				
				logger.info(f"Audio extraction completed: {temp_audio_path}")
				return temp_audio_path
				
			except ffmpeg.Error as e:
				logger.error(f"FFmpeg error: {e}")
				return None
			
		except Exception as e:
			logger.error(f"Error extracting audio from video: {str(e)}")
			return None
	
	async def get_video_info(self, video_path: str) -> Optional[Dict]:
		"""
		Get video file information using moviepy
		
		Args:
			video_path: Path to video file
			
		Returns:
			Dictionary with video information or None if failed
		"""
		try:
			logger.info(f"Getting video info for: {video_path}")
			
			# Get video info using ffmpeg
			try:
				probe = ffmpeg.probe(video_path)
				video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
				audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
				
				info = {
					'duration': float(probe['format'].get('duration', 0)),
					'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
					'size': [int(video_stream.get('width', 0)), int(video_stream.get('height', 0))] if video_stream else [0, 0],
					'has_audio': audio_stream is not None,
					'filename': os.path.basename(video_path),
					'file_size': os.path.getsize(video_path),
					'audio_duration': float(audio_stream.get('duration', 0)) if audio_stream else 0,
					'audio_fps': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0
				}
				
				logger.info(f"Video info: {info}")
				return info
				
			except ffmpeg.Error as e:
				logger.error(f"FFmpeg probe error: {e}")
				return None
			
		except Exception as e:
			logger.error(f"Error getting video info: {str(e)}")
			return None
	
	async def extract_subtitles_from_video(self, video_path: str) -> Optional[List[str]]:
		"""
		Extract subtitle text from video file (if embedded)
		
		Args:
			video_path: Path to video file
			
		Returns:
			List of subtitle texts or None if no subtitles found
		"""
		try:
			# This is a placeholder for subtitle extraction
			# In a real implementation, you would use libraries like:
			# - ffmpeg-python to extract subtitle streams
			# - pysrt for SRT files
			# - pymediainfo for metadata extraction
			
			logger.info("Subtitle extraction not implemented yet - using speech-to-text instead")
			return None
			
		except Exception as e:
			logger.error(f"Error extracting subtitles: {str(e)}")
			return None
	
	def cleanup_temp_file(self, file_path: str):
		"""Clean up temporary file"""
		try:
			if os.path.exists(file_path):
				os.unlink(file_path)
				logger.info(f"Cleaned up temporary file: {file_path}")
		except Exception as e:
			logger.error(f"Error cleaning up temp file: {str(e)}")
	
	def validate_video_file(self, file: UploadFile) -> Dict[str, any]:
		"""
		Validate uploaded video file
		
		Args:
			file: Uploaded file
			
		Returns:
			Dictionary with validation result
		"""
		result = {
			'valid': True,
			'errors': [],
			'warnings': []
		}
		
		# Check file extension
		if not file.filename:
			result['valid'] = False
			result['errors'].append("No filename provided")
			return result
		
		file_extension = os.path.splitext(file.filename)[1].lower()
		if file_extension not in self.supported_formats:
			result['valid'] = False
			result['errors'].append(f"Unsupported file format: {file_extension}")
		
		# Check content type
		if file.content_type and not file.content_type.startswith('video/'):
			result['warnings'].append(f"Unexpected content type: {file.content_type}")
		
		return result
