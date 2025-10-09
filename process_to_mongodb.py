#!/usr/bin/env python3

import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_to_mongodb():
    """Process Kaggle dataset and store in MongoDB"""
    print("🚀 Starting Kaggle to MongoDB processing...")
    
    # Connect to MongoDB Atlas
    print("📡 Connecting to MongoDB Atlas...")
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "cine_shazam")
    
    if not mongo_uri:
        raise Exception("MONGO_URI not found in environment variables")
    
    client = MongoClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)
    db = client[mongo_db]
    collection = db["movie_subtitles"]
    
    # Clear existing data
    print("🗑️ Clearing existing data...")
    collection.drop()
    
    # Create indexes for fast searching
    print("🔍 Creating database indexes...")
    collection.create_index("text_lower")
    collection.create_index("movie_title")
    collection.create_index("imdb_id")
    collection.create_index([("text_lower", "text")])  # Text search index
    
    print("📥 Loading Kaggle datasets...")
    
    # Load the datasets
    subtitles_df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        'adiamaan/movie-subtitle-dataset',
        'movies_subtitles.csv'
    )
    
    metadata_df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        'adiamaan/movie-subtitle-dataset',
        'movies_meta.csv'
    )
    
    print(f"✅ Loaded {len(subtitles_df):,} subtitle entries")
    print(f"✅ Loaded {len(metadata_df):,} movie metadata entries")
    
    # Get only popular movies for faster processing
    print("🎯 Filtering popular movies...")
    popular_movies = metadata_df[metadata_df['vote_count'] > 500].copy()
    popular_movies = popular_movies.sort_values('vote_count', ascending=False).head(2000)
    
    print(f"📊 Selected {len(popular_movies):,} popular movies")
    
    # Get subtitles for popular movies only
    popular_imdb_ids = set(popular_movies['imdb_id'].tolist())
    popular_subtitles = subtitles_df[subtitles_df['imdb_id'].isin(popular_imdb_ids)]
    
    print(f"📊 Found {len(popular_subtitles):,} subtitle entries for popular movies")
    
    # Merge datasets
    print("🔄 Merging datasets...")
    df = popular_subtitles.merge(
        popular_movies[['imdb_id', 'title', 'release_date', 'genres', 'overview', 'vote_average', 'vote_count']], 
        on='imdb_id', 
        how='left'
    )
    
    print(f"✅ Merged dataset: {len(df):,} entries")
    
    # Process and insert data in batches
    print("💾 Processing and inserting data...")
    batch_size = 1000
    total_entries = len(df)
    processed = 0
    
    for i in range(0, total_entries, batch_size):
        batch = df.iloc[i:i+batch_size]
        documents = []
        
        for idx, row in batch.iterrows():
            # Extract year from release_date
            year = 'Unknown'
            if pd.notna(row.get('release_date')) and row.get('release_date'):
                try:
                    year = str(row.get('release_date')).split('-')[0]
                except:
                    year = 'Unknown'
            
            # Clean genres
            genres = str(row.get('genres', ''))
            if genres and genres != 'nan':
                try:
                    genres_list = json.loads(genres)
                    genres_clean = [g['name'] for g in genres_list if isinstance(g, dict)]
                except:
                    genres_clean = []
            else:
                genres_clean = []
            
            document = {
                'movie_title': str(row.get('title', 'Unknown')),
                'year': year,
                'subtitle_text': str(row['text']),
                'text_lower': str(row['text']).lower(),
                'imdb_id': row['imdb_id'],
                'genres': genres_clean,
                'overview': str(row.get('overview', '')),
                'start_time': float(row.get('start_time', 0)),
                'end_time': float(row.get('end_time', 0)),
                'vote_average': float(row.get('vote_average', 0)),
                'vote_count': int(row.get('vote_count', 0)),
                'processed_at': datetime.now()
            }
            documents.append(document)
        
        # Insert batch
        if documents:
            collection.insert_many(documents)
        
        processed += len(batch)
        progress = (processed / total_entries) * 100
        print(f"📈 Progress: {processed:,}/{total_entries:,} ({progress:.1f}%) - Inserted batch of {len(documents)} documents")
    
    print(f"✅ Successfully inserted {processed:,} documents into MongoDB")
    
    # Test the database
    print("🧪 Testing database...")
    test_queries = ['deeper', 'serious', 'inception', 'batman']
    for query in test_queries:
        count = collection.count_documents({"text_lower": {"$regex": query, "$options": "i"}})
        print(f"🔍 '{query}': {count:,} matches")
        
        # Show sample results
        sample = collection.find({"text_lower": {"$regex": query, "$options": "i"}}).limit(3)
        for doc in sample:
            print(f"  📽️ {doc['movie_title']} ({doc['year']}): {doc['subtitle_text'][:50]}...")
    
    print("🎉 Processing complete! Data is now in MongoDB and ready for fast searching.")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    process_to_mongodb()
