import os
import json
import pickle
import pandas as pd
import streamlit as st
import asyncio
import aiohttp
import themoviedb

# ------------------------------
# TMDB API Key
# ------------------------------
config_data = json.load(open("config.json"))
TMDB_API_KEY = config_data["TMDB_API_KEY"]
themoviedb.api_key = TMDB_API_KEY

# ------------------------------
# Load Data
# ------------------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ------------------------------
# Async poster fetching
# ------------------------------
async def fetch_poster_async(session, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        async with session.get(url, timeout=10) as response:
            data = await response.json()
            poster_path = data.get('poster_path')
            poster_url = "https://image.tmdb.org/t/p/w500" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
            return movie_id, poster_url
    except:
        return movie_id, "https://via.placeholder.com/500x750?text=No+Image"

async def fetch_all_posters(movie_ids):
    poster_dict = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_poster_async(session, mid) for mid in movie_ids]
        for future in asyncio.as_completed(tasks):
            movie_id, poster_url = await future
            poster_dict[movie_id] = poster_url
    return poster_dict

# ------------------------------
# Precompute posters at startup
# ------------------------------
@st.cache_data
def get_posters():
    return asyncio.run(fetch_all_posters(movies['movie_id']))

poster_dict = get_posters()

# ------------------------------
# Recommendation Function
# ------------------------------
def recommend(movie):
    movie = movie.lower().strip()
    if movie not in movies['title'].str.lower().values:
        return []

    idx = movies[movies['title'].str.lower() == movie].index[0]
    distances = similarity[idx]
    top5 = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommendations = []
    for i in top5:
        m = movies.iloc[i[0]]
        recommendations.append({
            'title': m.title,
            'poster': poster_dict[m.movie_id]
        })
    return recommendations

# ------------------------------
# Streamlit App
# ------------------------------
st.set_page_config(page_title="CineVision", page_icon="🎥", layout="wide")
st.title("🎥 CineVision")
st.markdown("_Intelligent Movie Recommendations Powered by Machine Learning_")
st.markdown("Get **top 5 movie recommendations** based on your selection!")

# ------------------------------
# CSS Styling (existing style)
# ------------------------------
st.markdown("""
<style>
:root {
    --bg-color-start: #ffffff;
    --bg-color-end: #f3e6ff;
    --text-color: #2e2e2e;
    --primary-color: #6a5acd;
    --secondary-color: #87ceeb;
    --card-bg: #ffffff;
    --shadow: rgba(0, 0, 0, 0.1);
}

/* App background & font */
.stApp {
    background: linear-gradient(to bottom right, var(--bg-color-start), var(--bg-color-end));
    font-family: 'Roboto', sans-serif;
    color: var(--text-color);
    display: flex;
    flex-direction: column;
    align-items: center;       
    justify-content: flex-start;
    min-height: 100vh;
    text-align: center;        
    padding: 2rem;
}

/* Main title */
h1, h2, h3 {
    color: var(--text-color);
    font-weight: 400;
}

/* Button styling */
.stButton>button {
    background-color: var(--primary-color);
    color: white;
    font-weight: 500;
    border-radius: 24px;
    padding: 0.5em 2em;
    border: none;
    font-size: 1rem;
    transition: background 0.2s;
    display: block;
    margin: 0.5rem auto 2rem auto; 
}
.stButton>button:hover {
    background-color: var(--secondary-color);
    color: white;
}

/* Selectbox styling */
.stSelectbox>div>div>div>select {
    width: 100% !important;     
    font-size: 1rem;            
    padding: 0.5rem 0.75rem;    
    border-radius: 12px;
    border: 1px solid #ccc;
    text-align: center;         
}

/* Movie card styling */
.movie-card {
    text-align: center;
    font-weight: 500;
    font-size: 0.85rem;
    color: var(--text-color);
    margin-bottom: 1rem;
}
.movie-card img {
    border-radius: 12px;
    background-color: var(--card-bg);
    box-shadow: 0 2px 8px var(--shadow);
    transition: transform 0.15s, box-shadow 0.15s;
    margin-bottom: 0.5rem;
}
.movie-card img:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px var(--shadow);
}
/* Movie title */
.movie-card .title {
    font-weight: 600;
    font-size: 1rem;
}

/* Spinner color and centering */
.stSpinner {
    position: fixed !important;
    top: 70% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    z-index: 9999 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.stSpinner > div > div {
    border-top-color: var(--primary-color);
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Centered Movie Selection
# ------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie = st.selectbox("Select a movie:", movies['title'].values)
    recommend_button = st.button("Show Recommendations")

# ------------------------------
# Show Recommendations
# ------------------------------
if recommend_button:
    recommendations = recommend(selected_movie)
    if recommendations:
        st.markdown("### 🍿 Recommended Movies:")
        cols = st.columns(5, gap="medium")
        for rec, col in zip(recommendations, cols):
            with col:
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{rec['poster']}" width="stretch">
                        <div class="title">{rec['title']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.error("😔 Movie not found in dataset! Try another movie.")
        st.info("Tip: Make sure spelling matches or choose from the dropdown.")
