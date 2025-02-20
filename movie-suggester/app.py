from flask import Flask, request, jsonify, render_template
import requests
import random
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

app = Flask(__name__)

# Mapping moods to all TMDb genre IDs
GENRE_MAPPING = {
    "action": "28",
    "adventure": "12",
    "animation": "16",
    "comedy": "35",
    "crime": "80",
    "documentary": "99",
    "drama": "18",
    "family": "10751",
    "fantasy": "14",
    "history": "36",
    "horror": "27",
    "music": "10402",
    "mystery": "9648",
    "romance": "10749",
    "science fiction": "878",
    "tv movie": "10770",
    "thriller": "53",
    "war": "10752",
    "western": "37"
}

# Certification mappings (for filtering by age rating)
CERTIFICATION_MAPPING = {
    "G": "G",
    "PG": "PG",
    "14A": "14A",
    "18A": "18A",
    "A": "A"
}

def get_movie(genre, certification, language):
    """Fetch a random movie from TMDb API based on user preferences."""

    genre_id = GENRE_MAPPING.get(genre.lower(), "35")  # Default to Comedy
    certification_filter = f"&certification={certification}" if certification else ""
    language_filter = f"&language={language}" if language else "&language=en-US"

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}{certification_filter}{language_filter}"

    response = requests.get(url)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        random_movie = random.choice(data["results"])
        return {
            "title": random_movie["title"],
            "year": random_movie["release_date"].split("-")[0] if "release_date" in random_movie else "N/A",
            "rating": random_movie["vote_average"],
            "poster": f"https://image.tmdb.org/t/p/w500{random_movie['poster_path']}" if random_movie["poster_path"] else "",
            "link": f"https://www.themoviedb.org/movie/{random_movie['id']}",
        }
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get-movie", methods=["GET"])
def get_movie_api():
    genre = request.args.get("genre", "comedy")  # Default: Comedy
    certification = request.args.get("certification", None)
    language = request.args.get("language", "en")  # Default: English

    movie = get_movie(genre, certification, language)

    if movie:
        return jsonify(movie)
    return jsonify({"error": "No movie found!"})

if __name__ == "__main__":
    app.run(debug=True)
