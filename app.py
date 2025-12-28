from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import process
import re

from MovieRecommendor import recommend, movie_titles
from TMDBrequest import search_tmdb_movie

# -------------------------
# helpers
# -------------------------

FUZZY_THRESHOLD = 80


def normalize_title(title: str) -> str:
    """
    پاک‌سازی عنوان دیتاست برای ارسال به TMDB
    مثال:
    'Magnificent Seven, The (1954)' -> 'The Magnificent Seven'
    """
    title = re.sub(r"\(\d{4}\)", "", title)  # remove year
    if ", The" in title:
        title = "The " + title.replace(", The", "")
    return title.strip()


def fuzzy_match(user_input, titles, limit=5):
    """
    خروجی:
    [(title, score), ...]
    """
    return process.extract(user_input, titles, limit=limit)


# -------------------------
# flask app
# -------------------------

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Movie Recommendation API is running!"

@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("query", "").lower()

    if len(q) < 2:
        return jsonify({"results": []})

    matches = [
        t for t in movie_titles
        if q in t.lower()
    ][:7]

    return jsonify({"results": matches})

@app.route("/recommend", methods=["GET"])
def recommend_api():
    user_title = request.args.get("title", "").strip()

    if not user_title:
        return jsonify({"error": "title parameter is required"}), 400

    # 1. fuzzy matching روی دیتاست
    matches = fuzzy_match(user_title, movie_titles)

    if not matches:
        # دیتاست کاملاً خالی یا خطا
        return jsonify({
            "source": "tmdb",
            "results": search_tmdb_movie(user_title)
        })

    closest_title, score = matches[0]

    # 2. اگر شباهت کم بود → مستقیم TMDB
    if score < FUZZY_THRESHOLD:
        return jsonify({
            "source": "tmdb",
            "results": search_tmdb_movie(user_title)
        })

    try:
        # 3. ML recommender
        recommended_titles = recommend(closest_title)

        recommendations = []

        for raw_title in recommended_titles:
            clean_title = normalize_title(raw_title)
            tmdb_results = search_tmdb_movie(clean_title)

            if tmdb_results:
                movie = tmdb_results[0]
                recommendations.append({
                    "title": movie.get("title", clean_title),
                    "poster": movie.get("poster"),
                    "rating": movie.get("rating")
                })
            else:
                recommendations.append({
                    "title": clean_title,
                    "poster": None,
                    "rating": None
                })

        return jsonify({
            "source": "ml+tmdb",
            "input_movie": user_title,
            "matched_title": closest_title,
            "match_score": score,
            "similar_titles": [m[0] for m in matches],
            "recommendations": recommendations
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# run
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
