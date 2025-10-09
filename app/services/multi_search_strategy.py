import logging
from typing import List, Dict, Optional
from app.services.mongodb_search import MongoDBSubtitleSearch

logger = logging.getLogger(__name__)

class MultiSearchStrategy:
	"""Simplified search strategy using MongoDB only"""
	
	def __init__(self):
		self.mongodb_search = MongoDBSubtitleSearch()
	
	async def comprehensive_search(self, text: str) -> Dict:
		"""Simplified search using MongoDB only"""
		logger.info(f"Starting MongoDB search for: {text[:50]}...")
		
		# Use MongoDB for fast search
		mongodb_results = await self.mongodb_search.search_subtitles(text, limit=10)
		logger.info(f"MongoDB search found {len(mongodb_results)} results")
		
		# Remove duplicates
		unique_results = self._deduplicate_results(mongodb_results)
		
		return {
			"success": True,
			"input_text": text,
			"search_method": "mongodb_only",
			"movie_results": unique_results[:15],  # Top 15 results
			"total_results": len(unique_results)
		}
	
	def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
		"""Remove duplicate results based on movie title and year"""
		seen = set()
		unique_results = []
		
		for result in results:
			key = (result.get('movie_title', ''), result.get('year', ''))
			if key not in seen and key != ('Unknown', 'Unknown'):
				seen.add(key)
				unique_results.append(result)
		
		return unique_results