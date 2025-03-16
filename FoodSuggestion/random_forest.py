import joblib
import pandas as pd
import numpy as np
from google.cloud import storage
import os


GCS_BUCKET_NAME = 'quefoodhall-food-recommendations'
LOCAL_MODEL_DIR = 'FoodSuggestion/ModelCollection'
MODEL_FILES = [
    "food_model.pkl",
    "restaurant_model.pkl",
    "scaler.pkl",
    "food_encoder.pkl",
    "restaurant_encoder.pkl"
]


def download_models_from_gcs():
    try:
        print("Initializing Google Cloud Storage client...")
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

        for model_file in MODEL_FILES:
            local_path = os.path.join(LOCAL_MODEL_DIR, model_file)
            blob = bucket.blob(model_file)

            print(f"Downloading {model_file} from GCS...")
            blob.download_to_filename(local_path)
            print(f"Downloaded {model_file} to {local_path}")

    except Exception as e:
        print(f"Error downloading models: {e}")


download_models_from_gcs()

def load_model():
    food_model = joblib.load(os.path.join(LOCAL_MODEL_DIR, "food_model.pkl"))
    restaurant_model = joblib.load(os.path.join(LOCAL_MODEL_DIR, "restaurant_model.pkl"))
    scaler = joblib.load(os.path.join(LOCAL_MODEL_DIR, "scaler.pkl"))
    food_encoder = joblib.load(os.path.join(LOCAL_MODEL_DIR, "food_encoder.pkl"))
    restaurant_encoder = joblib.load(os.path.join(LOCAL_MODEL_DIR, "restaurant_encoder.pkl"))
    return food_model, restaurant_model, scaler, food_encoder, restaurant_encoder

def find_nearest_calorie_value(calories, available_calories):
    return min(available_calories, key=lambda x: abs(x - calories))

def recommend_food(calories):
    df_food = pd.read_csv("data/food_data_encoded.csv")
    available_calories = df_food['estimated_calories'].unique()
    closest_calories = find_nearest_calorie_value(calories, available_calories)

    food_model, restaurant_model, scaler, food_encoder, restaurant_encoder = load_model()
    input_calories = scaler.transform([[closest_calories]])

    predicted_food_label = food_model.predict(input_calories)
    predicted_restaurant_label = restaurant_model.predict(input_calories)

    df_subfood = df_food[df_food['food_name_encoded'] == predicted_food_label[0]].head()

    df_raw_rest = df_food[df_food['restaurant_id_encoded'] == predicted_restaurant_label[0]]
    df_rest = df_raw_rest[df_raw_rest['estimated_calories'] < df_subfood.iloc[0]['estimated_calories']].head()

    df_result = pd.concat([df_subfood, df_rest]).drop_duplicates(subset=['food_name'], keep="first")

    result_json = df_result.to_json(orient='records')

    return result_json
