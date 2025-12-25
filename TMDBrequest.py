import requests

TMDB_API_KEY = "7d519049e7fcf2394ace3fa9e656fd96"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def search_tmdb_movie(title):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US"
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []

    for movie in data.get("results", [])[:10]:
        results.append({
            "title": movie["title"],
            "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                      if movie.get("poster_path") else None
        })

    return results
