import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import os

# Load the dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "final_merged_dataset.csv"))

# Ensure missing values are handled
df["course_title"] = df["course_title"].fillna("No Title Available")
df["combined_features"] = df["course_title"] + " " + df["course_difficulty"] + " " + df["course_Certificate_type"]

# Drop duplicates before creating pivot table
df = df.drop_duplicates(subset=["user_id", "item_id"])

# Convert text features into numerical vectors
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["combined_features"])

# Compute cosine similarity between courses
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Train KNN model for collaborative filtering
pivot_table = df.pivot(index="user_id", columns="item_id", values="rating").fillna(0)
matrix = pivot_table.values
print(f"Pivot table shape: {pivot_table.shape}")  # Example output: (500 users, 776 items)
print(f"Matrix shape: {matrix.shape}")  # Should match the pivot table size

knn = NearestNeighbors(metric="cosine", algorithm="brute")
knn.fit(matrix)

def hybrid_recommend(user_id, liked_course, num_recommendations=5, weight_cf=0.5, weight_cb=0.5):
    """
    Hybrid Recommendation System combining Collaborative Filtering & Content-Based Filtering.
    """
    # Convert to lowercase and strip spaces
    if liked_course.strip().lower() not in df["course_title"].str.lower().str.strip().values:
        return ["Course not found in dataset"]


    idx = df[df["course_title"] == liked_course].index[0]

    # Get content-based recommendations
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    content_recommendations = [df.iloc[i[0]]["course_title"] for i in sim_scores[1:num_recommendations + 1]]

    # Ensure user exists in pivot table before running KNN
    if user_id not in pivot_table.index:
        return [f"User {user_id} not found in dataset"]

    user_index = pivot_table.index.get_loc(user_id)  # Correct user index lookup
    distances, indices = knn.kneighbors([matrix[user_index]], n_neighbors=num_recommendations + 1)

    # Fix collaborative filtering recommendations
    cf_recommendations = []
    for i in indices[0][1:]:
        if i >= len(pivot_table.columns):  # Ensure index is within bounds
            continue  # Skip this recommendation if it's out of range

        item_id = pivot_table.columns[i]  # Get item_id from pivot table
        course_title = df[df["item_id"] == item_id]["course_title"].values

        if len(course_title) > 0:
            cf_recommendations.append(course_title[0])
        else:
            cf_recommendations.append("Unknown Course")  # Handle missing course titles


    # Combine recommendations using weights
    combined_recommendations = list(set(content_recommendations[:int(num_recommendations * weight_cb)] +
                                        cf_recommendations[:int(num_recommendations * weight_cf)]))

    return combined_recommendations[:num_recommendations]
