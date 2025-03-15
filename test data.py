import pandas as pd

file_path = /Users/mac/recommender_project/api/final_merged_dataset.csv

try:
    df = pd.read_csv(file_path)
    print("Dataset loaded successfully!")
    print(df.head())  # Show first 5 rows
except Exception as e:
    print(f"Error loading dataset: {e}")
