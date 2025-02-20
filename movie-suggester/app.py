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


@app.route("/get-languages", methods=["GET"])
def get_languages():
    """Fetch all available languages from TMDb API."""
    url = f"https://api.themoviedb.org/3/configuration/languages?api_key={TMDB_API_KEY}"

    response = requests.get(url)
    data = response.json()

    if isinstance(data, list):  # Ensure the response is a list
        languages = [{"code": lang["iso_639_1"], "name": lang["english_name"]} for lang in data]
        return jsonify(languages)

    return jsonify({"error": "Failed to fetch languages"}), 500


def get_movie(genre, certification, language, sort_by):
    """Fetch a movie from TMDb API based on user-selected filters."""

    genre_id = GENRE_MAPPING.get(genre.lower(), None)  # Allow "Any Genre"
    genre_filter = f"&with_genres={genre_id}" if genre_id else ""  # Apply only if genre is selected
    certification_filter = f"&certification_country=US&certification={certification}" if certification else ""
    language_filter = f"&with_original_language={language}" if language else ""
    sort_option = SORT_OPTIONS.get(sort_by.lower(), "popularity.desc")  # Default: Popularity

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}{genre_filter}{certification_filter}{language_filter}&sort_by={sort_option}"

    print(f"DEBUG: Fetching URL -> {url}")  # ✅ Debugging API call

    response = requests.get(url)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        random_movie = random.choice(data["results"])
        return {
            "status": "success",
            "title": random_movie["title"],
            "year": random_movie.get("release_date", "N/A")[:4],  # Get only the year
            "rating": random_movie["vote_average"],
            "poster": f"https://image.tmdb.org/t/p/w500{random_movie['poster_path']}" if random_movie["poster_path"] else "",
            "link": f"https://www.themoviedb.org/movie/{random_movie['id']}",
        }
    else:
        print("DEBUG: No movies found! Suggesting a random English movie.")
        return get_random_english_movie()  # ✅ Show alternative

def get_random_english_movie():
    """Fetches a random popular English movie if no matching movie is found."""
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language=en&sort_by=popularity.desc"

    response = requests.get(url)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        random_movie = random.choice(data["results"])
        return {
            "status": "fallback",
            "message": "No movie found based on your selected filters. Here is a popular English movie instead.",
            "title": random_movie["title"],
            "year": random_movie.get("release_date", "N/A")[:4],  # Get only the year
            "rating": random_movie["vote_average"],
            "poster": f"https://image.tmdb.org/t/p/w500{random_movie['poster_path']}" if random_movie["poster_path"] else "",
            "link": f"https://www.themoviedb.org/movie/{random_movie['id']}",
        }
    return {"status": "error", "message": "No movies found, even in English!"}


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
