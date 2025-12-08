import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re


# ---------------------------------------------------------
# 1) Load Ratings
# ---------------------------------------------------------
column_names = ['user_id', 'movie_id', 'rating', 'timestamp']

ratings = pd.read_csv(
    'ml-100k/u.data',
    sep='\t',
    names=column_names,
    engine='python'
)

# ---------------------------------------------------------
# 2) Load Movies
# ---------------------------------------------------------
item_columns = [
    'movie_id', 'title', 'release_date', 'video_release_date', 
    'imdb_url', 'unknown', 'Action', 'Adventure', 'Animation',
    'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 
    'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 
    'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

movies = pd.read_csv(
    'ml-100k/u.item',
    sep='|',
    names=item_columns,
    encoding='latin-1'
)


data = ratings.merge(movies[['movie_id', 'title', 'Drama', 'Comedy', 'Action', 'Horror']], on='movie_id')




# ---------------------------------------------------------
# 3) Mean Rating
# ---------------------------------------------------------

# محاسبه میانگین امتیاز هر فیلم
mean_ratings = ratings.groupby('movie_id')['rating'].mean()
movies['mean_rating'] = movies['movie_id'].map(mean_ratings)


# ---------------------------------------------------------
# 4) Extract Year From Title
# ---------------------------------------------------------

def extract_year(title):
    match = re.search(r'\((\d{4})\)', title)
    return match.group(1) if match else ""

movies['year'] = movies['title'].apply(extract_year)



# ---------------------------------------------------------
# 5) Dynamic Genre Weight Calculation
# ---------------------------------------------------------
genre_cols = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 
            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 
            'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 
            'Thriller', 'War', 'Western']

genre_freq = movies[genre_cols].sum()
max_freq = genre_freq.max()
# وزن پویا
genre_weights = np.log(max_freq / genre_freq + 1)



# ---------------------------------------------------------
# 6) Create Final Feature Text Per Movie
# ---------------------------------------------------------
def generate_features(row):

    text = ""

    # 1. اضافه کردن ژانرها با وزن پویا
    for genre in genre_cols:
        if row[genre] == 1:
            repeat = int(genre_weights[genre] * 3)  # ضریب 3 = شدت تاثیر
            text += (genre + " ") * repeat

    # 2. اضافه کردن عنوان با وزن کمتر
    text += (row['title'] + " ") * 1

    # 3. اضافه کردن سال ساخت
    if row['year'] != "":
        text += ("year_" + row['year'] + " ") * 2

    # 4. اضافه کردن میانگین امتیاز
    rating_level = int(row['mean_rating'])
    text += ("rating_" + str(rating_level)) + " "

    return text

movies['features'] = movies.apply(generate_features, axis=1)

# ---------------------------------------------------------
# 7) TF-IDF + Cosine Similarity (FINAL)
# ---------------------------------------------------------
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['features'])


cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


indices = movies.reset_index().set_index('title')


# ---------------------------------------------------------
# 8) Recommend Function
# ---------------------------------------------------------

def recommend(title, num_recommendations=10):
    if title not in indices.index:
        return []

    idx = indices.loc[title]['index']

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:num_recommendations+1]
    movie_indices = [i[0] for i in sim_scores]

    return movies['title'].iloc[movie_indices].tolist()

recommend("toy story (1995)")