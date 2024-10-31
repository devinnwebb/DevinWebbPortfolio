# similarity_analysis.py
import json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from scipy.spatial.distance import euclidean
import numpy as np

# Load and preprocess the dataset
def load_data(file_path):
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f]
    return pd.DataFrame(data)

def preprocess_data(df):
    # Extract 'avg' rating from 'rating' dictionary
    df['average_rating'] = df['rating'].apply(lambda x: x['avg'] if isinstance(x, dict) and 'avg' in x else 0)
    
    # Normalize ratings
    df['normalized_rating'] = MinMaxScaler().fit_transform(df[['average_rating']])
    
    # Extract actor names for Jaccard similarity
    df['actor_names'] = df['actors'].apply(lambda x: [actor[1] for actor in x] if isinstance(x, list) else [])
    
    # Genre encoding using MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    genres_encoded = mlb.fit_transform(df['genres'])
    genre_df = pd.DataFrame(genres_encoded, columns=mlb.classes_)
    
    # Add genre and normalized rating to main dataframe
    df = pd.concat([df, genre_df], axis=1)
    
    return df, genre_df

# Similarity calculations
def calculate_genre_similarity(genre_df):
    return cosine_similarity(genre_df)

def calculate_rating_similarity(df, query_index):
    # Ensure query_rating is a scalar value
    query_rating = df.loc[query_index, 'normalized_rating']
    if isinstance(query_rating, pd.Series):
        query_rating = query_rating.iloc[0]
    
    # Calculate Euclidean distance for each rating in the dataset
    rating_sim = [euclidean([query_rating], [r]) for r in df['normalized_rating']]
    return rating_sim

def calculate_actor_similarity(df, query_index):
    query_actors = set(df.iloc[query_index]['actor_names'])
    similarities = []
    for actors in df['actor_names']:
        actors_set = set(actors)
        intersection = query_actors.intersection(actors_set)
        union = query_actors.union(actors_set)
        if not union:
            similarity = 0
        else:
            similarity = len(intersection) / len(union)
        similarities.append(similarity)
    return similarities

# Aggregate similarities
def get_top_similar(df, genre_sim, rating_sim, actor_sim, query_index, top_n=10):
    combined_similarity = (
        0.5 * genre_sim +
        0.3 * (1 - np.array(rating_sim)) +  # Inverting distance to get similarity
        0.2 * np.array(actor_sim)
    )
    similar_indices = combined_similarity.argsort()[::-1][1:top_n + 1]
    return df.iloc[similar_indices][['title', 'genres', 'actor_names', 'average_rating']]

# Main function to execute analysis
def main():
    # Load and preprocess data
    df = load_data('imdb_movies_2000to2022.prolific (1).json')
    df, genre_df = preprocess_data(df)
    
    # Query movies
    queries = ['The Lord of the Rings: The Fellowship of the Ring', 'Inception', 'Shrek']
    query_indices = [df[df['title'] == query].index[0] for query in queries]
    
    # Compute similarities and display results
    for query, query_index in zip(queries, query_indices):
        print(f"\nTop 10 movies similar to {query}:\n")
        
        genre_sim = calculate_genre_similarity(genre_df)[query_index]
        rating_sim = calculate_rating_similarity(df, query_index)
        actor_sim = calculate_actor_similarity(df, query_index)
        
        similar_movies = get_top_similar(df, genre_sim, rating_sim, actor_sim, query_index)
        print(similar_movies)

if __name__ == "__main__":
    main()
