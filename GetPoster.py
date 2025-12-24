import requests
import re


OMDB_API_KEY = "c2d29fcd"

def get_movie_poster(title):
    # جدا کردن سال اگر داخل پرانتز باشد
    match = re.search(r'\((\d{4})\)', title)
    year = match.group(1) if match else None
    clean_title = re.sub(r'\s*\(\d{4}\)', '', title)

    params = {
        "t": clean_title,
        "apikey": OMDB_API_KEY
    }
    if year:
        params["y"] = year

    r = requests.get("http://www.omdbapi.com/", params=params, timeout=5)
    data = r.json()

    if data.get("Response") == "True" and data.get("Poster") != "N/A":
        return data["Poster"]

    return None