import joblib
import pandas as pd
import numpy as np

def load_model():
    food_model = joblib.load("ModelCollection/food_model.pkl")
    restaurant_model = joblib.load("ModelCollection/restaurant_model.pkl")
    scaler = joblib.load("ModelCollection/scaler.pkl")
    food_encoder = joblib.load("ModelCollection/food_encoder.pkl")
    restaurant_encoder = joblib.load("ModelCollection/restaurant_encoder.pkl")
    return food_model, restaurant_model, scaler, food_encoder, restaurant_encoder


def find_nearest_calorie_value(calories, available_calories):
    return min(available_calories, key=lambda x: abs(x - calories))


def recommend_food(calories):
    df_food = pd.read_csv("../data/food_data_encoded.csv")
    available_calories = df_food['estimated_calories'].unique()
    closest_calories = find_nearest_calorie_value(calories, available_calories)

    food_model, restaurant_model, scaler, food_encoder, restaurant_encoder = load_model()
    input_calories = scaler.transform([[closest_calories]])

    predicted_food_label = food_model.predict(input_calories)
    predicted_restaurant_label = restaurant_model.predict(input_calories)

    df_result = df_food[(df_food['food_name_encoded'] == predicted_food_label[0]) & (df_food['restaurant_id_encoded'] == predicted_restaurant_label[0])]
    result_json = df_result.to_json(orient='records')

    return result_json
