import asyncio
from app.services.subtitle_loader import SubtitleLoader

async def main():
    loader = SubtitleLoader()

    movies = [
        # Sci-Fi Classics
         {"imdb_id": "2446042", "title": "The Batman (2022)"},
  {"imdb_id": "4975722", "title": "Top Gun: Maverick"},
  {"imdb_id": "1091191", "title": "Everything Everywhere All at Once"},
  {"imdb_id": "9852360", "title": "RRR"},
  {"imdb_id": "9376612", "title": "Elvis (2022)"},
  {"imdb_id": "12361974", "title": "Glass Onion: A Knives Out Mystery"},
  {"imdb_id": "1527236", "title": "Nope"},
  {"imdb_id": "10648342", "title": "Avatar: The Way of Water"},
  {"imdb_id": "13373532", "title": "The Fabelmans"},
  {"imdb_id": "1259521", "title": "The Northman"},

  {"imdb_id": "10942445", "title": "Black Panther: Wakanda Forever"},
  {"imdb_id": "12347570", "title": "Asteroid City"},
  {"imdb_id": "10293938", "title": "Babylon (2022)"},
  {"imdb_id": "1454468", "title": "Barbie (2023)"},
  {"imdb_id": "1536537", "title": "Killers of the Flower Moon"},
  {"imdb_id": "1013752", "title": "Oppenheimer"},
  {"imdb_id": "3982082", "title": "Dune: Part Two"},
  {"imdb_id": "1877830", "title": "The Batman (2022)"},
  {"imdb_id": "1345836", "title": "The Dark Knight Rises"},
  {"imdb_id": "1321870", "title": "Everything Everywhere All at Once"},

  {"imdb_id": "16001996", "title": "Furiosa: A Mad Max Saga"},
  {"imdb_id": "14331314", "title": "Inside Out 2"},
  {"imdb_id": "1979376", "title": "The Marvels"},
  {"imdb_id": "1408232", "title": "M3GAN 2.0"},
  {"imdb_id": "1408422", "title": "La La Land 2: The Encore"},
  {"imdb_id": "2606464", "title": "Transformers One"},
  {"imdb_id": "1538352", "title": "The Hunger Games: The Ballad of Songbirds & Snakes"},
  {"imdb_id": "0936501", "title": "Black Adam"},
  {"imdb_id": "1405385", "title": "Mission: Impossible – Dead Reckoning Part One"},
  {"imdb_id": "1431045", "title": "Mission: Impossible – The Final Reckoning"},

  {"imdb_id": "0267787", "title": "The Super Mario Bros. Movie (2023)"},
  {"imdb_id": "12387772", "title": "Guardians of the Galaxy Vol. 3"},
  {"imdb_id": "1375666", "title": "Inception (remastered)"}  
    ]

    print(f"🎬 Starting to download subtitles for {len(movies)} movies...")
    print("=" * 50)
    
    for i, m in enumerate(movies, 1):
        print(f"\n[{i}/{len(movies)}] Processing: {m['title']}")
        await loader.fetch_and_store(m["imdb_id"], m["title"])
    
    print("\n" + "=" * 50)
    print("🎉 All movies processed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
