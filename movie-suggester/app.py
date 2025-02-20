from flask import Flask, request, jsonify, render_template
import requests
import random
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

app = Flask(__name__)

# Mapping TMDb genres
GENRE_MAPPING = {
    "action": "28", "adventure": "12", "animation": "16", "comedy": "35", "crime": "80",
    "documentary": "99", "drama": "18", "family": "10751", "fantasy": "14", "history": "36",
    "horror": "27", "music": "10402", "mystery": "9648", "romance": "10749",
    "science fiction": "878", "tv movie": "10770", "thriller": "53", "war": "10752", "western": "37"
}

# Sorting options mapping for TMDb API
SORT_OPTIONS = {
    "popular": "popularity.desc",
    "top_rated": "vote_average.desc",
    "newest": "release_date.desc"
}

def get_movie(genre, certification, language, sort_by):
    """Fetch a movie from TMDb API based on user-selected filters."""

    genre_id = GENRE_MAPPING.get(genre.lower(), "35")  # Default: Comedy
    certification_filter = f"&certification_country=US&certification={certification}" if certification else ""
    language_filter = f"&with_original_language={language}" if language else ""
    sort_option = SORT_OPTIONS.get(sort_by.lower(), "popularity.desc")  # Default: Popularity

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}{certification_filter}{language_filter}&sort_by={sort_option}"

    print(f"DEBUG: Fetching URL -> {url}")  # ✅ Debugging API call

    response = requests.get(url)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        random_movie = random.choice(data["results"])
        return {
            "title": random_movie["title"],
            "year": random_movie.get("release_date", "N/A")[:4],  # Get only the year
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
    sort_by = request.args.get("sort_by", "popular")  # Default: Popular

    movie = get_movie(genre, certification, language, sort_by)

    if movie:
        return jsonify(movie)
    return jsonify({"error": "No movie found!"})

if __name__ == "__main__":
    app.run(debug=True)
