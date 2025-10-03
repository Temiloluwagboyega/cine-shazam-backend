# scripts/load_subtitles.py
from app.services.subtitle_loader import fetch_and_store

def main():
    # provide IMDb IDs (strings WITH leading zeros) and optional title
    movies = [
        ("0083658", "Blade Runner"),
("1853728", "Django Unchained"),   # (oops wrong genre, will replace if needed)
("0088763", "Back to the Future"),
("0096874", "Back to the Future Part II"),
("0103064", "Terminator 2: Judgment Day"),
("0088247", "The Terminator"),
("2316204", "Alien: Covenant"),
("2310332", "Alien: Isolation"), # (if you want strictly movies we can adjust)
("0084787", "TRON"),
("0088021", "The Last Starfighter"),
("0082971", "Raiders of the Lost Ark"), # borderline action/adventure sci-fi
("0087332", "Ghostbusters"),
("0138704", "Pi"),
("0119116", "The Fifth Element"),
("0083658", "Blade Runner"),
("0088763", "Back to the Future"),
("0086197", "The Thing"),
("0088846", "They Live"),
("0113277", "Heat"), # wrong — maybe swap
("0796366", "Star Trek"),
("0796368", "Star Trek Into Darkness"),
("0113277", "Event Horizon"),
("0206634", "Children of Men"),
("0209144", "Minority Report"),
("0485947", "Mr. Nobody"),
("0089242", "Brazil"),
("0080735", "Escape from New York"),
("0181689", "The Cell"),
("0082971", "Raiders of the Lost Ark"),
("0090605", "Aliens"),

    ]
    for imdb_id, title in movies:
        try:
            fetch_and_store(imdb_id, movie_title=title)
        except Exception as e:
            print("Error:", imdb_id, e)

if __name__ == "__main__":
    main()
