import spacy
import re

def extract_age_gender(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    male_keywords = {"man", "boy", "male", "gentleman", "dude"}
    female_keywords = {"woman", "girl", "female", "lady"}
    all_gender_keywords = male_keywords | female_keywords

    # Define regex patterns for age extraction
    age_number_pattern = r'\b(\d{1,3})\s?(?:years?|yrs?|y/o|old)?\b|\b(\d{2})s\b'
    age_description_pattern = r'\b(?:young|teen|teenager|adult|middle-aged|senior|elderly|child|baby|infant)\b'

    genders = [token.text.lower() for token in doc if token.text.lower() in all_gender_keywords]
    numerical_ages = [int(match.group(1) or match.group(2)) for match in re.finditer(age_number_pattern, text)]
    descriptive_ages = [match.group(0) for match in re.finditer(age_description_pattern, text)]

    age = numerical_ages[0] if numerical_ages else None
    gender = genders[0] if genders else None

    if age is None and descriptive_ages:
        description = descriptive_ages[0]
        if description in {"young", "teen", "teenager"}:
            age = 18
        elif description in {"adult", "middle-aged"}:
            age = 35
        elif description in {"senior", "elderly"}:
            age = 65
        elif description in {"child", "baby", "infant"}:
            age = 5

    return age, gender


def calculate_meal_calories(age, gender):
    male_keywords = {"man", "boy", "male", "gentleman", "dude"}
    female_keywords = {"woman", "girl", "female", "lady"}

    gender = gender.lower()
    if gender in male_keywords:
        weight = 85
        height = 178
        multiplier = 1.55
        lower_factor = 0.9
        upper_factor = 1.15
        gender_offset = 5
    elif gender in female_keywords:
        weight = 70
        height = 170
        multiplier = 1.45
        lower_factor = 0.85
        upper_factor = 1.08
        gender_offset = -161
    else:
        raise ValueError("Gender value not supported in list!")

    BMR = (10 * weight) + (6.25 * height) - (5 * age) + gender_offset
    TDEE = BMR * multiplier
    meal_calories = TDEE * 0.40

    lower_calories = meal_calories * lower_factor
    upper_calories = meal_calories * upper_factor

    return round(lower_calories), round(upper_calories)


def estimate_meal_calories(user_input):
    age, gender = extract_age_gender(user_input)

    if not age:
        return "Could not determine age from input."
    if not gender:
        return "Could not determine gender from input."

    return calculate_meal_calories(age, gender)
