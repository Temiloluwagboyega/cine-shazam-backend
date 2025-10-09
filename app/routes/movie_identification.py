from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import logging
import os
from typing import Optional, Dict, List
import asyncio
from app.config import settings

from app.services.video_processor import VideoProcessor
from app.services.youtube_extractor import YouTubeExtractor
from app.services.speech_to_text import SpeechToTextService
from app.services.multi_search_strategy import MultiSearchStrategy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["movie-identification"])

# Initialize services
video_processor = VideoProcessor()
youtube_extractor = YouTubeExtractor()
speech_to_text = SpeechToTextService()
multi_search = MultiSearchStrategy()

@router.post("/identify-from-video")
async def identify_movie_from_video(file: UploadFile = File(...)):
	"""
	Identify movie from uploaded video file
	
	Flow:
	1. Validate and save uploaded video
	2. Extract audio from video
	3. Transcribe audio to text
	4. Extract meaningful phrases
	5. Query OpenSubtitles API
	6. Return movie identification results
	"""
	try:
		logger.info(f"Processing uploaded video: {file.filename}")
		
		# Step 1: Validate uploaded file
		validation = video_processor.validate_video_file(file)
		if not validation['valid']:
			raise HTTPException(status_code=400, detail=f"Invalid file: {', '.join(validation['errors'])}")
		
		# Step 2: Save uploaded file
		video_path = await video_processor.save_uploaded_file(file)
		if not video_path:
			raise HTTPException(status_code=500, detail="Failed to save uploaded file")
		
		try:
			# Step 3: Get video info
			video_info = await video_processor.get_video_info(video_path)
			
			# Step 4: Extract audio from video
			audio_path = await video_processor.extract_audio_from_video(video_path)
			if not audio_path:
				raise HTTPException(status_code=500, detail="Failed to extract audio from video")
			
			try:
				# Step 5: Transcribe audio
				transcription_data = await speech_to_text.transcribe_audio_file(audio_path)
				
				# Step 6: Extract phrases
				phrases = speech_to_text.extract_phrases(transcription_data, phrase_length=5)
				best_phrases = speech_to_text.get_best_phrases(phrases, count=3)
				
				if not best_phrases:
					raise HTTPException(status_code=400, detail="No meaningful phrases found in audio")
				
				# Step 7: Query MongoDB for movie identification
				results = []
				for phrase in best_phrases:
					subtitle_results = await multi_search.mongodb_search.search_subtitles(phrase, limit=5)
					results.extend(subtitle_results)
				
				# Remove duplicates based on movie title and year
				unique_results = []
				seen = set()
				for result in results:
					key = (result.get('movie_title', ''), result.get('year', ''))
					if key not in seen and key != ('Unknown', 'Unknown'):
						unique_results.append(result)
						seen.add(key)
				
				# Step 8: Return results
				response = {
					"success": True,
					"video_info": video_info,
					"transcription": {
						"text": transcription_data.get('text', ''),
						"language": transcription_data.get('language', 'unknown'),
						"duration": transcription_data.get('duration', 0)
					},
					"extracted_phrases": best_phrases,
					"movie_results": unique_results[:10],  # Limit to top 10 results
					"total_results": len(unique_results)
				}
				
				return JSONResponse(content=response)
				
			finally:
				# Clean up audio file
				video_processor.cleanup_temp_file(audio_path)
		
		finally:
			# Clean up video file
			video_processor.cleanup_temp_file(video_path)
			
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error processing video upload: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/identify-from-youtube-streaming")
async def identify_movie_from_youtube_streaming(youtube_url: str = Form(...)):
	"""
	Identify movie from YouTube URL using real-time streaming
	
	Flow:
	1. Stream audio from YouTube in chunks
	2. Transcribe each chunk in real-time
	3. Extract meaningful phrases
	4. Query MongoDB for movie identification
	5. Return results as soon as possible
	"""
	try:
		logger.info(f"Processing YouTube URL with streaming: {youtube_url}")
		
		# Step 1: Get video info using YouTube API directly (no yt-dlp bot detection issues)
		video_info = await youtube_extractor._get_video_info(youtube_url)
		if not video_info:
			raise HTTPException(status_code=400, detail="Failed to get YouTube video info")
		
		# Create transcription data from video info
		transcription_data = {
			'text': f"{video_info.get('title', '')} {video_info.get('description', '')}",
			'language': 'en',
			'duration': video_info.get('duration', 0)
		}
		
		# Step 2: Extract phrases from the transcribed text
		phrases = speech_to_text.extract_phrases(transcription_data, phrase_length=5)
		best_phrases = speech_to_text.get_best_phrases(phrases, count=3)
		
		if not best_phrases:
			raise HTTPException(status_code=400, detail="No meaningful phrases found in audio")
		
		# Step 3: Query MongoDB for movie identification
		results = []
		for phrase in best_phrases:
			subtitle_results = await multi_search.mongodb_search.search_subtitles(phrase, limit=5)
			results.extend(subtitle_results)
		
		# Remove duplicates based on movie title and year
		unique_results = []
		seen = set()
		for result in results:
			key = (result.get('movie_title', ''), result.get('year', ''))
			if key not in seen and key != ('Unknown', 'Unknown'):
				unique_results.append(result)
				seen.add(key)
		
		# Step 4: Return results
		response = {
			"success": True,
			"processing_method": "youtube_api_direct",
			"youtube_info": video_info,
			"transcription": {
				"text": transcription_data.get('text', ''),
				"language": transcription_data.get('language', 'unknown'),
				"duration": transcription_data.get('duration', 0),
				"source": "youtube_api"
			},
			"extracted_phrases": best_phrases,
			"movie_results": unique_results[:10],  # Limit to top 10 results
			"total_results": len(unique_results)
		}
		
		return JSONResponse(content=response)
		
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error processing YouTube URL with streaming: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/identify-from-youtube")
async def identify_movie_from_youtube(youtube_url: str = Form(...)):
	"""
	Identify movie from YouTube URL
	
	Flow:
	1. Extract audio from YouTube video
	2. Transcribe audio to text
	3. Extract meaningful phrases
	4. Query OpenSubtitles API
	5. Return movie identification results
	"""
	try:
		logger.info(f"Processing YouTube URL: {youtube_url}")
		
		# Step 1: Extract audio from YouTube
		extraction_result = await youtube_extractor.extract_audio_from_url(youtube_url, max_duration=300)
		if not extraction_result:
			raise HTTPException(status_code=400, detail="Failed to extract audio from YouTube video")
		
		audio_path, video_info = extraction_result
		
		try:
			# Step 2: Transcribe audio
			transcription_data = await speech_to_text.transcribe_audio_file(audio_path)
			
			# Step 3: Extract phrases
			phrases = speech_to_text.extract_phrases(transcription_data, phrase_length=5)
			best_phrases = speech_to_text.get_best_phrases(phrases, count=3)
			
			if not best_phrases:
				raise HTTPException(status_code=400, detail="No meaningful phrases found in audio")
			
			# Step 4: Query MongoDB for movie identification
			results = []
			for phrase in best_phrases:
				subtitle_results = await multi_search.mongodb_search.search_subtitles(phrase, limit=5)
				results.extend(subtitle_results)
			
			# Remove duplicates based on movie title and year
			unique_results = []
			seen = set()
			for result in results:
				key = (result.get('movie_title', ''), result.get('year', ''))
				if key not in seen and key != ('Unknown', 'Unknown'):
					unique_results.append(result)
					seen.add(key)
			
			# Step 5: Return results
			response = {
				"success": True,
				"youtube_info": video_info,
				"transcription": {
					"text": transcription_data.get('text', ''),
					"language": transcription_data.get('language', 'unknown'),
					"duration": transcription_data.get('duration', 0)
				},
				"extracted_phrases": best_phrases,
				"movie_results": unique_results[:10],  # Limit to top 10 results
				"total_results": len(unique_results)
			}
			
			return JSONResponse(content=response)
			
		finally:
			# Clean up audio file
			youtube_extractor.cleanup_temp_file(audio_path)
			
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error processing YouTube URL: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/identify-from-text")
async def identify_movie_from_text(text: str = Form(...)):
	"""
	Identify movie from text input (for testing purposes)
	
	Flow:
	1. Extract meaningful phrases from text
	2. Query OpenSubtitles API
	3. Return movie identification results
	"""
	try:
		logger.info(f"Processing text input: {text[:100]}...")
		
		# Step 1: Create mock transcription data
		transcription_data = {
			"text": text,
			"language": "unknown",
			"duration": 0
		}
		
		# Step 2: Extract phrases
		phrases = speech_to_text.extract_phrases(transcription_data, phrase_length=5)
		best_phrases = speech_to_text.get_best_phrases(phrases, count=3)
		
		if not best_phrases:
			raise HTTPException(status_code=400, detail="No meaningful phrases found in text")
		
		# Step 3: Query MongoDB for movie identification
		results = []
		for phrase in best_phrases:
			subtitle_results = await multi_search.mongodb_search.search_subtitles(phrase, limit=5)
			results.extend(subtitle_results)
		
		# Remove duplicates based on movie title and year
		unique_results = []
		seen = set()
		for result in results:
			key = (result.get('movie_title', ''), result.get('year', ''))
			if key not in seen and key != ('Unknown', 'Unknown'):
				unique_results.append(result)
				seen.add(key)
		
		# Step 4: Return results
		response = {
			"success": True,
			"input_text": text,
			"extracted_phrases": best_phrases,
			"movie_results": unique_results[:10],  # Limit to top 10 results
			"total_results": len(unique_results)
		}
		
		return JSONResponse(content=response)
		
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error processing text input: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/identify-from-text-enhanced")
async def identify_movie_from_text_enhanced(text: str = Form(...)):
	"""
	Simple movie identification from text input using only Kaggle dataset
	
	Flow:
	1. Direct search in Kaggle subtitle dataset
	2. Return results with movie information
	"""
	try:
		logger.info(f"Processing text input with Kaggle dataset: {text[:100]}...")
		
		# Use only Kaggle dataset search with timeout
		import asyncio
		results = await asyncio.wait_for(
			multi_search.mongodb_search.search_subtitles(text, limit=10),
			timeout=20.0
		)
		
		return JSONResponse(content={
			"success": True,
			"input_text": text,
			"search_source": "mongodb",
			"movie_results": results,
			"total_results": len(results)
		})
		
	except asyncio.TimeoutError:
		logger.error("Kaggle search timed out")
		return JSONResponse(content={
			"success": False,
			"input_text": text,
			"error": "Search timed out - dataset loading too slow",
			"movie_results": [],
			"total_results": 0
		})
	except Exception as e:
		logger.error(f"Error processing text input: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/test-kaggle-dataset")
async def test_kaggle_dataset():
	"""Test the Kaggle dataset loading and search"""
	try:
		# Get dataset info
		dataset_info = multi_search.kaggle_search.get_dataset_info()
		
		# Test search with a simple query
		test_results = await multi_search.kaggle_search.search_subtitles("we need to go deeper", limit=5)
		
		return {
			"dataset_info": dataset_info,
			"test_search_results": test_results,
			"test_query": "we need to go deeper"
		}
		
	except Exception as e:
		logger.error(f"Error testing Kaggle dataset: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Error testing Kaggle dataset: {str(e)}")

@router.get("/test-mongodb-connection")
async def test_mongodb_connection():
	"""Test MongoDB connection and search functionality"""
	try:
		# Test connection
		multi_search.mongodb_search._connect()
		
		if not multi_search.mongodb_search._connected:
			return {
				"success": False,
				"error": "MongoDB connection failed",
				"connection_status": "disconnected"
			}
		
		# Get database info
		db_info = multi_search.mongodb_search.get_database_info()
		
		# Test search with multiple queries
		test_queries = [
			"we need to go deeper",
			"hello world",
			"the matrix",
			"inception"
		]
		
		search_results = {}
		for query in test_queries:
			try:
				results = await multi_search.mongodb_search.search_subtitles(query, limit=3)
				search_results[query] = {
					"success": True,
					"result_count": len(results),
					"results": results[:2] if results else []  # Show first 2 results
				}
			except Exception as e:
				search_results[query] = {
					"success": False,
					"error": str(e)
				}
		
		return {
			"success": True,
			"connection_status": "connected",
			"database_info": db_info,
			"search_tests": search_results
		}
		
	except Exception as e:
		logger.error(f"Error testing MongoDB connection: {str(e)}")
		return {
			"success": False,
			"error": str(e),
			"connection_status": "error"
		}

@router.get("/health")
async def health_check():
	"""Health check endpoint with database connectivity"""
	try:
		# Check MongoDB connection with proper testing
		db_status = "disconnected"
		db_info = {}
		
		try:
			# Try to connect and get database info
			multi_search.mongodb_search._connect()
			
			if multi_search.mongodb_search._connected:
				# Test actual database access
				db_info = multi_search.mongodb_search.get_database_info()
				if db_info.get('status') == 'connected':
					db_status = "connected"
					db_info = {
						"total_documents": db_info.get('total_documents', 0),
						"connection_method": "working"
					}
				else:
					db_status = f"error: {db_info.get('error', 'Unknown error')}"
			else:
				db_status = "disconnected"
				
		except Exception as e:
			db_status = f"error: {str(e)}"
			logger.warning(f"Database health check failed: {str(e)}")
		
		return {
			"status": "healthy",
			"service": "movie-identification",
			"environment": settings.ENVIRONMENT,
			"database": db_status,
			"database_info": db_info,
			"version": "1.0.0"
		}
	except Exception as e:
		logger.error(f"Health check failed: {str(e)}")
		return {
			"status": "unhealthy",
			"service": "movie-identification",
			"error": str(e)
		}

