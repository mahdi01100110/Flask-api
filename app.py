from flask import Flask, request, jsonify
from MovieRecommendor import recommend  # تابع توصیه‌گر

app = Flask(__name__)

@app.route('/')
def home():
    return "Movie Recommendation API is running!"

@app.route('/recommend', methods=['GET'])
def recommend_api():
    title = request.args.get('title')

    if not title:
        return jsonify({"error": "title parameter is required"}), 400

    try:
        result = recommend(title)

        # تبدیل مطمئن به لیست
        try:
            result = list(result)
        except:
            result = result.tolist()

        return jsonify({
            "input_movie": title,
            "recommendations": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
