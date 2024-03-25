import numpy as np
import pandas as pd
import os
import re

BASE_DIR = os.path.abspath(".")
DATASET_DIR = os.path.join(BASE_DIR, "data")

# # [TODO] REPLACE WITH FULL SET
df = pd.read_csv(os.path.join(DATASET_DIR, "test.csv"))


def clean_ingredients(data, normalization_map=None):
    """
    Removes rows from df based on specific non-ingredient phrases,
    non-ingredient keywords, or na values, and normalizes ingredient names.
    ----------
    data : DataFrame
        Input df containing 'ingredients' column.
    normalization_map : dict
        A dictionary mapping synonymous ingredient to a standardized form.
    Returns
    -------
    DataFrame
        The cleaned and normalized DataFrame.
    """
    non_ingredient_phrases = [
        "this brand is excluded from most ulta beauty coupons",
        "are subject to change at the manufacturer's discretion. for the most complete and up-to-date information\", refer to the product packaging",
    ]
    non_ingredient_words = {
        "active",
        "inactive",
        "ingredients",
        "may contain",
        "shimmer",
        "matte",
        "sunscreen",
        "emollient",
        # "fair",
        # "neutral",
    }

    if normalization_map is None:
        normalization_map = {
            "aqua": "water",
            "eau": "water",
            "vitamin c": "citric acid",
        }

    normalization_map = {k.lower(): v.lower() for k, v in normalization_map.items()}
    data = data.dropna(subset=["ingredients"])

    for phrase in non_ingredient_phrases:
        data = data[~data["ingredients"].str.contains(phrase, case=False, na=False)]

    def process_ingredients(text):
        text = text.lower()
        for word in non_ingredient_words:
            text = re.sub(r"\b" + word + r"\b", "", text)
        tokens = [token.strip() for token in text.split(",") if token.strip()]
        processed_tokens = [normalization_map.get(token, token) for token in tokens]
        return ", ".join(sorted(set(processed_tokens), key=processed_tokens.index))

    data["ingredients"] = data["ingredients"].apply(process_ingredients)
    return data


def tokenize(text):
    """
    Tokenizes ingredients string into a list of ingredients.
    ----------
    text : str
        The input text string
    Returns
    -------
    list
         A list of tokenized ingredients.
    """
    cleaned_str = re.sub(r"\([^)]*\)|\d+(\.\d+)?%|[\\/:]|^[. ]+|[. ]+$", " ", text)
    cleaned_str = re.sub(r"\s+", " ", cleaned_str).lower().strip()

    tokens = [ing.strip().lower() for ing in cleaned_str.split(",") if ing.strip()]

    return tokens


df_cleaned = clean_ingredients(df)
df_cleaned["tokenized_ingredients"] = df_cleaned.apply(
    lambda x: tokenize(x["ingredients"]) if pd.notnull(x["ingredients"]) else [], axis=1
)
df_cleaned["product_index"] = df_cleaned.index

df_cleaned.to_json(os.path.join(DATASET_DIR, "clean_dataset.json"), orient="records")
