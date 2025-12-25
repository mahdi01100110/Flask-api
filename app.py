from flask import Flask, request, jsonify
from MovieRecommendor import recommend,movie_titles  # تابع توصیه‌گر
from flask_cors import CORS
from fuzzywuzzy import process
from GetPoster import get_movie_poster
from TMDBrequest import search_tmdb_movie

def find_closest_title(user_input, titles):
    best_match = process.extractOne(user_input, titles)
    return best_match[0] if best_match else None

def find_similar_titles(user_input, titles, limit=5):
    matches = process.extract(user_input, titles, limit=limit)
    return [m[0] for m in matches]

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Movie Recommendation API is running!"

@app.route("/tmdb-test")
def tmdb_test():
    title = request.args.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    movies = search_tmdb_movie(title)
    return jsonify(movies)

@app.route('/recommend', methods=['GET'])
def recommend_api():
    title = request.args.get('title')

    if not title:
        return jsonify({"error": "title parameter is required"}), 400

    similar_titles = find_similar_titles(title, movie_titles)
    closest_title = similar_titles[0] if similar_titles else None

    if not closest_title:
        return jsonify({
            "input_movie": title,
            "matched_title": None,
            "similar_titles": similar_titles,
            "recommendations": []
        })

    try:
        recommended_titles = recommend(closest_title)

        recommendations = []
        for movie in recommended_titles:
            recommendations.append({
                "title": movie,
                "poster": get_movie_poster(movie)
            })

        return jsonify({
            "input_movie": title,
            "matched_title": closest_title,
            "similar_titles": similar_titles,
            "recommendations": recommendations
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
