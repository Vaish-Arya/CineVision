CineVision 🎥

CineVision is an intelligent movie recommendation system that suggests movies based on similarity in genres, cast, crew, keywords, and plot overview. The project combines **Python, Machine Learning, and Streamlit** to provide a user-friendly interface for exploring movie recommendations.

Features:

- Recommends **top 5 movies** similar to the selected movie.
- Fetches **movie posters dynamically** from TMDB API.
- Uses **cosine similarity** on preprocessed movie data for accurate recommendations.
- Frontend built with **Streamlit** featuring an elegant and interactive UI.
- Backend handles **data preprocessing, feature extraction, and recommendation logic**.
- Supports large datasets with efficient computation using `pickle` serialized objects.

Backend Overview:

- Data sources: `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv`.
- Preprocessing:  
  - Extracts genres, keywords, cast (top 3), and director from the datasets.  
  - Cleans and stems textual data for similarity analysis.  
  - Combines movie features into a single `tags` column for vectorization.
- Modeling:  
  - Converts `tags` to numerical vectors using `CountVectorizer`.  
  - Computes cosine similarity between movies.  
  - Provides a function `recommend(movie)` to get top 5 similar movies.
- Data storage: 
  - Pickled objects: `movies.pkl`, `movie_dict.pkl`, `similarity.pkl` for efficient loading.

Frontend Overview

- Built with Streamlit for an interactive and responsive UI.
- Users can select a movie from a dropdown menu.
- Displays top 5 recommended movies with posters.
- Styling includes gradient backgrounds, cards for posters, and custom fonts.
- Handles API errors gracefully with placeholders if posters are missing.
