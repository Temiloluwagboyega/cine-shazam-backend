import logging
from typing import List, Dict, Optional
import pymongo
from pymongo import MongoClient
import re
import ssl
import urllib.parse
from app.config import settings

logger = logging.getLogger(__name__)

class MongoDBSubtitleSearch:
	"""Fast search through MongoDB subtitle database"""
	
	def __init__(self):
		self.client = None
		self.db = None
		self.collection = None
		self._connected = False
		
	def _connect(self):
		"""Connect to MongoDB with comprehensive SSL and connection strategies"""
		if self._connected:
			return
			
		if not settings.MONGO_URI:
			logger.error("MONGO_URI not found in environment variables")
			self._connected = False
			return
		
		# Parse the MongoDB URI to extract components
		parsed_uri = urllib.parse.urlparse(settings.MONGO_URI)
		
		# Try multiple connection strategies
		connection_strategies = [
			{
				"name": "Custom SSL Context",
				"method": self._try_custom_ssl_context
			},
			{
				"name": "Legacy SSL Parameters",
				"method": self._try_legacy_ssl_params
			},
			{
				"name": "Direct Connection String",
				"method": self._try_direct_connection
			},
			{
				"name": "Legacy SSL",
				"method": self._try_legacy_ssl
			},
			{
				"name": "Minimal Configuration",
				"method": self._try_minimal_config
			}
		]
		
		for strategy in connection_strategies:
			try:
				logger.info(f"Trying MongoDB connection with {strategy['name']}...")
				
				if strategy['method']():
					logger.info(f"Successfully connected to MongoDB using {strategy['name']}")
					return
					
			except Exception as e:
				logger.warning(f"Failed to connect with {strategy['name']}: {str(e)}")
				if self.client:
					self.client.close()
					self.client = None
				continue
		
		# If all connection attempts failed
		logger.error("All MongoDB connection attempts failed")
		self._connected = False
	
	def _try_custom_ssl_context(self) -> bool:
		"""Try connection with custom SSL context"""
		try:
			# Create a custom SSL context
			ssl_context = ssl.create_default_context()
			ssl_context.check_hostname = False
			ssl_context.verify_mode = ssl.CERT_NONE
			
			# Try with custom SSL context
			self.client = MongoClient(
				settings.MONGO_URI,
				tls=True,
				tlsInsecure=True,
				ssl_context=ssl_context,
				serverSelectionTimeoutMS=15000,
				connectTimeoutMS=15000,
				socketTimeoutMS=15000,
				maxPoolSize=5,
				retryWrites=False,
				directConnection=False
			)
			
			return self._test_connection()
			
		except Exception as e:
			logger.debug(f"Custom SSL context failed: {e}")
			return False
	
	def _try_direct_connection(self) -> bool:
		"""Try direct connection to primary server"""
		try:
			# Extract host from URI and try direct connection
			parsed_uri = urllib.parse.urlparse(settings.MONGO_URI)
			host = parsed_uri.hostname
			
			if host and 'mongodb.net' in host:
				# Try connecting directly to the primary shard
				direct_uri = settings.MONGO_URI.replace('mongodb+srv://', 'mongodb://')
				direct_uri = direct_uri.replace('?retryWrites=true&w=majority', '')
				
				self.client = MongoClient(
					direct_uri,
					tls=True,
					tlsAllowInvalidCertificates=True,
					tlsAllowInvalidHostnames=True,
					serverSelectionTimeoutMS=10000,
					connectTimeoutMS=10000,
					socketTimeoutMS=10000,
					maxPoolSize=3,
					retryWrites=False,
					directConnection=True
				)
				
				return self._test_connection()
			
		except Exception as e:
			logger.debug(f"Direct connection failed: {e}")
			return False
	
	def _try_legacy_ssl_params(self) -> bool:
		"""Try legacy SSL parameters that might work better with older pymongo"""
		try:
			self.client = MongoClient(
				settings.MONGO_URI,
				ssl=True,
				ssl_cert_reqs=ssl.CERT_NONE,
				ssl_match_hostname=False,
				ssl_ca_certs=None,
				ssl_certfile=None,
				ssl_keyfile=None,
				serverSelectionTimeoutMS=15000,
				connectTimeoutMS=15000,
				socketTimeoutMS=15000,
				maxPoolSize=3,
				retryWrites=False,
				directConnection=False
			)
			
			return self._test_connection()
			
		except Exception as e:
			logger.debug(f"Legacy SSL params failed: {e}")
			return False
	
	def _try_legacy_ssl(self) -> bool:
		"""Try legacy SSL configuration"""
		try:
			self.client = MongoClient(
				settings.MONGO_URI,
				ssl=True,
				ssl_cert_reqs=ssl.CERT_NONE,
				ssl_match_hostname=False,
				serverSelectionTimeoutMS=20000,
				connectTimeoutMS=20000,
				socketTimeoutMS=20000,
				maxPoolSize=5,
				retryWrites=False
			)
			
			return self._test_connection()
			
		except Exception as e:
			logger.debug(f"Legacy SSL failed: {e}")
			return False
	
	def _try_minimal_config(self) -> bool:
		"""Try minimal configuration with basic parameters"""
		try:
			self.client = MongoClient(
				settings.MONGO_URI,
				serverSelectionTimeoutMS=5000,
				connectTimeoutMS=5000,
				socketTimeoutMS=5000,
				maxPoolSize=1
			)
			
			return self._test_connection()
			
		except Exception as e:
			logger.debug(f"Minimal config failed: {e}")
			return False
	
	def _test_connection(self) -> bool:
		"""Test the current connection and set up database/collection"""
		try:
			self.db = self.client[settings.MONGO_DB]
			self.collection = self.db["movie_subtitles"]
			
			# Test connection with a simple operation
			self.collection.count_documents({})
			self._connected = True
			return True
			
		except Exception as e:
			logger.debug(f"Connection test failed: {e}")
			return False
	
	async def search_subtitles(self, query: str, limit: int = 10) -> List[Dict]:
		"""
		Search for subtitles containing the query text
		
		Args:
			query: Text to search for
			limit: Maximum number of results to return
			
		Returns:
			List of movie results with subtitle matches
		"""
		try:
			# Connect if not already connected
			if not self._connected:
				self._connect()
			
			if not self._connected:
				logger.error("Not connected to MongoDB")
				return []
			
			query_lower = query.lower()
			logger.info(f"Searching MongoDB for: {query}")
			
			# Search using simple contains (MongoDB Atlas free tier doesn't support regex)
			# Try multiple search strategies
			results = []
			
			# Strategy 1: Try regex first (might work on some Atlas tiers)
			# Temporarily disabled to test Strategy 3
			# try:
			# 	results = list(self.collection.find(
			# 		{"text_lower": {"$regex": query_lower, "$options": "i"}}
			# 	).sort("vote_count", -1).limit(limit * 2))
			# 	logger.info(f"Strategy 1 (regex) found {len(results)} results")
			# except Exception as e:
			# 	logger.warning(f"Regex search failed: {e}, trying alternative methods")
			# 	results = []
			
			# Strategy 2: If regex fails, use simple contains with $in
			# Temporarily disabled to test Strategy 3
			# if not results:
			# 	# Split query into words and search for each
			# 	query_words = query_lower.split()
			# 	if query_words:
			# 		# Search for documents containing any of the query words
			# 		word_conditions = [{"text_lower": {"$regex": word, "$options": "i"}} for word in query_words]
			# 		try:
			# 			results = list(self.collection.find(
			# 				{"$or": word_conditions}
			# 			).sort("vote_count", -1).limit(limit * 3))  # Get more for filtering
			# 			logger.info(f"Strategy 2 (word search) found {len(results)} results")
			# 		except Exception as e:
			# 			logger.warning(f"Word search failed: {e}, trying exact match")
			# 			results = []
			
			# Strategy 3: If all else fails, try exact substring match with better filtering
			if not results:
				logger.info("Strategy 3: Using fallback exact substring search")
				# This is a fallback - search for exact substring
				# But limit the search to avoid performance issues and improve accuracy
				# Try to get documents in a more diverse order
				all_docs = list(self.collection.find({}).sort("_id", 1).limit(limit * 100))
				# Filter for documents that actually contain the query
				results = []
				query_words = query_lower.split()
				
				for doc in all_docs:
					text_lower = doc.get('text_lower', '').lower()
					
					# Normalize text for better matching (remove extra punctuation and spaces)
					import re
					normalized_text = re.sub(r'[^\w\s]', ' ', text_lower)
					normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
					normalized_query = re.sub(r'[^\w\s]', ' ', query_lower)
					normalized_query = re.sub(r'\s+', ' ', normalized_query).strip()
					
					# Check for exact phrase match first (normalized)
					if normalized_query in normalized_text:
						# Calculate a better match score based on position and completeness
						position = normalized_text.find(normalized_query)
						# Prefer matches that start closer to the beginning
						position_score = 1.0 - (position / max(len(normalized_text), 1))
						# Prefer longer, more complete matches
						completeness_score = len(normalized_query) / max(len(normalized_text), 1)
						doc['_match_score'] = position_score + completeness_score + 2.0  # Bonus for exact match
						results.append(doc)
					# Also check original text for exact match
					elif query_lower in text_lower:
						position = text_lower.find(query_lower)
						position_score = 1.0 - (position / max(len(text_lower), 1))
						completeness_score = len(query_lower) / max(len(text_lower), 1)
						doc['_match_score'] = position_score + completeness_score + 1.5  # Slightly lower bonus
						results.append(doc)
					
					# If no exact match, check for word-based matching
					elif len(query_words) > 1:
						# Count how many query words are found in the text
						word_matches = sum(1 for word in query_words if word in text_lower)
						if word_matches >= len(query_words) * 0.6:  # At least 60% of words must match
							# Calculate score based on word match ratio
							match_ratio = word_matches / len(query_words)
							doc['_match_score'] = match_ratio
							results.append(doc)
				
				# Sort by our custom match score
				results.sort(key=lambda x: x.get('_match_score', 0), reverse=True)
				results = results[:limit * 2]  # Limit results
				
			# Strategy 4: If still no results, try searching by movie title
			if not results and len(query_lower.split()) <= 3:  # Only for short queries
				try:
					results = list(self.collection.find(
						{"movie_title": {"$regex": query_lower, "$options": "i"}}
					).limit(limit))
				except Exception as e:
					logger.warning(f"Movie title search failed: {e}")
			
			logger.info(f"Found {len(results)} matches in MongoDB")
			if results:
				logger.info(f"Top result: {results[0].get('movie_title')} - {results[0].get('text_lower', '')[:50]}...")
			
			# Process results
			processed_results = []
			seen_movies = set()
			
			for doc in results:
				# Create unique key for deduplication
				movie_key = (doc.get('movie_title', ''), doc.get('year', ''))
				
				if movie_key not in seen_movies and movie_key != ('Unknown', 'Unknown'):
					seen_movies.add(movie_key)
					
					# Calculate match score
					match_score = self._calculate_match_score(query_lower, doc.get('text_lower', ''))
					
					result = {
						'movie_title': doc.get('movie_title', 'Unknown'),
						'year': doc.get('year', 'Unknown'),
						'subtitle_text': doc.get('subtitle_text', ''),
						'match_score': match_score,
						'source': 'mongodb',
						'imdb_id': doc.get('imdb_id', ''),
						'genres': doc.get('genres', []),
						'overview': doc.get('overview', ''),
						'start_time': doc.get('start_time', 0),
						'end_time': doc.get('end_time', 0),
						'vote_average': doc.get('vote_average', 0),
						'vote_count': doc.get('vote_count', 0)
					}
					
					processed_results.append(result)
			
			# Sort by match score and vote count
			processed_results.sort(key=lambda x: (x['match_score'], x['vote_count']), reverse=True)
			
			return processed_results[:limit]
			
		except Exception as e:
			logger.error(f"Error searching MongoDB: {str(e)}")
			return []
	
	def _calculate_match_score(self, query: str, text: str) -> float:
		"""Calculate how well the query matches the text"""
		if not text:
			return 0.0
		
		# Exact match gets highest score
		if query in text:
			# Calculate position bonus (earlier matches are better)
			position = text.find(query)
			position_bonus = 1.0 - (position / len(text))
			return 1.0 + position_bonus
		
		# Partial match
		words = query.split()
		text_words = text.split()
		
		matches = 0
		for word in words:
			if word in text_words:
				matches += 1
		
		return matches / len(words) if words else 0.0
	
	async def search_multiple_queries(self, queries: List[str], limit_per_query: int = 5) -> List[Dict]:
		"""Search with multiple queries and combine results"""
		try:
			all_results = []
			
			for query in queries:
				results = await self.search_subtitles(query, limit_per_query)
				all_results.extend(results)
			
			# Remove duplicates and sort by score
			unique_results = []
			seen = set()
			
			for result in all_results:
				key = (result['movie_title'], result['year'])
				if key not in seen and key != ('Unknown', 'Unknown'):
					unique_results.append(result)
					seen.add(key)
			
			# Sort by match score
			unique_results.sort(key=lambda x: x['match_score'], reverse=True)
			
			return unique_results
			
		except Exception as e:
			logger.error(f"Error in multiple query search: {str(e)}")
			return []
	
	def get_database_info(self) -> Dict:
		"""Get information about the MongoDB database"""
		if not self._connected:
			self._connect()
		
		if not self._connected:
			return {"status": "not_connected"}
		
		try:
			total_docs = self.collection.count_documents({})
			sample_doc = self.collection.find_one()
			
			return {
				"status": "connected",
				"total_documents": total_docs,
				"sample_document": sample_doc
			}
		except Exception as e:
			return {"status": "error", "error": str(e)}
	
	def __del__(self):
		"""Close MongoDB connection on destruction"""
		if self.client:
			self.client.close()
