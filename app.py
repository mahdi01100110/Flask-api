from flask import Flask, request, jsonify
from MovieRecommendor import recommend

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "Movie Recommender API is running!"})


@app.route("/recommend", methods=["GET"])
def recommend_api():
    title = request.args.get("title")

    if not title:
        return jsonify({"error": "Please provide ?title=MovieName"}), 400

    results = recommend(title)

    return jsonify({
        "input": title,
        "recommendations": results
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
