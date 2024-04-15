import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import json
import os


def ingredient_idx(products_df: pd.DataFrame):
    """
    Creates an inverted index of ingredients
    ----------
    products : list
        A list of product dictionaries, each containing an 'ingredients' key.
    Returns
    -------
    dict
        dict with unique index for each unique ingredient found in the dataset.
    """
    idx = 0
    ingredient_index = {}
    for _, product in products_df.iterrows():
        for ingredient in product["ingredients"]:
            if ingredient not in ingredient_index:
                ingredient_index[ingredient] = idx
                idx += 1
    return ingredient_index


def oh_encoder(product_ingredients, ingredient_index_map):
    """
    One hot encodes the ingredients list where each element corresponds to an
    ingredient, and its value is 1 if the ingredient is present in the
    product and 0 otherwise
    ----------
    product_ingredients : list
        A list of ingredients for a single product.
    ingredient_index_map : dict
        A dictionary mapping ingredients to indices.
    Returns
    -------
    numpy.array
        A one-hot encoded array representing the presence of ingredients in the product.
    """
    x = np.zeros(len(ingredient_index_map))
    for ingredient in product_ingredients:
        if ingredient in ingredient_index_map:
            idx = ingredient_index_map[ingredient]
            x[idx] = 1
    return x


def create_tsne(products_df: pd.DataFrame):
    ingredient_index_map = ingredient_idx(products_df)
    m = len(products_df)
    n = len(ingredient_index_map)
    a = np.zeros((m, n))

    for i, product in products_df.iterrows():
        a[i, :] = oh_encoder(product["ingredients"], ingredient_index_map)

    model = TSNE(n_components=2, learning_rate=200, random_state=1)
    tsne_features = model.fit_transform(a)
    products_df["X"] = tsne_features[:, 0]
    products_df["Y"] = tsne_features[:, 1]
    return products_df


def reverse_product_idx(products_df: pd.DataFrame, product: str):
    product_names = list(products_df["product"])
    return product_names.index(product)


def find_most_similar_cosine_filtered(product_index, products_df, n_similar=10):
    """
    Finds the n most similar products with cosine similarity
    ----------
    product_idx : int
        The input product index
    n_similar : int
        number of similar products to be returned
    Returns
    -------
    list
         A list of n most similar products
    """
    # Filter by category
    products_df = create_tsne(products_df)
    target_product = products_df.iloc[product_index]
    target_category = target_product["category"]

    same_category_products = products_df[products_df["category"] == target_category]
    tsne_features = np.array(
        [[p["X"], p["Y"]] for _, p in same_category_products.iterrows()]
    )
    target_feature = np.array([[target_product["X"], target_product["Y"]]])

    similarities = cosine_similarity(target_feature, tsne_features)[0]

    # sorted_indices = np.argsort(similarities)[::-1][1 : n_similar + 1]
    sorted_indices = np.argsort(similarities)[::-1][1:]
    # print(sorted_indices)
    return same_category_products.iloc[sorted_indices]


def ingredient_boolean_search(products_df, disliked_ingredients):
    """
    Filters out products that contain the specified disliked ingredients
    ----------
    disliked_ingredients: string list
    """
    products_df.reset_index(drop=True, inplace=True)

    dislikes = products_df["ingredients"].apply(
        lambda ingredients: not any(
            ingredient in disliked_ingredients for ingredient in ingredients
        )
    )
    output_df = products_df[dislikes]

    return output_df
    # filtered_df = products_df[(products_df["product"].str.lower().str.contains(query.lower()))]
