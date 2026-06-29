import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ── Load pickles (saved from your notebook) ──
new_df     = pickle.load(open("movies.pkl", "rb"))     # your new_df DataFrame
similarity = pickle.load(open("similarity.pkl", "rb")) # your similarity matrix

TMDB_API_KEY = "deab40e7206acc4351a86428a49a4496"   
POSTER_BASE  = "https://image.tmdb.org/t/p/w500"
FALLBACK     = "https://placehold.co/300x450/181818/555?text=No+Poster"


def fetch_poster(movie_id):
    if TMDB_API_KEY == "YOUR_TMDB_API_KEY":
        return FALLBACK
    try:
        url  = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        path = data.get("poster_path")
        return POSTER_BASE + path if path else FALLBACK
    except Exception:
        return FALLBACK


@app.route("/movies")
def get_movies():
    """All movie titles for the search dropdown."""
    return jsonify(new_df["title"].tolist())


@app.route("/recommend")
def recommend():
    """Return 5 recommendations — matches your notebook logic exactly."""
    movie = request.args.get("title", "")

    # case-insensitive match (same as your notebook)
    mask = new_df["title"].str.lower() == movie.lower()
    if not mask.any():
        return jsonify({"error": "Movie not found"}), 404

    mov_index  = new_df[mask].index[0]
    distance   = similarity[mov_index]
    mov_list   = np.argsort(distance)[::-1]   # same as your notebook

    results = []
    for i in mov_list[1:6]:
        row = new_df.iloc[i]
        results.append({
            "title":    row["title"],
            "movie_id": int(row["movie_id"]),
            "poster":   fetch_poster(int(row["movie_id"])),
        })

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
