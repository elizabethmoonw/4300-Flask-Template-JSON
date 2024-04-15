import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import json
import os
import re

BASE_DIR = os.path.abspath(".")
DATASET_DIR = os.path.join(BASE_DIR, "data")

# [TODO] Change cleaned json
with open(os.path.join(DATASET_DIR, "clean_dataset.json"), "r") as file:
    products = json.load(file)


def ingredient_idx(products):
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
    for product in products:
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


def tsne_plot(products):
    """
    Generates and displays a 2D t-SNE plot of products based on their ingredients.
    ----------
    products : list
        A list of products to plot.
    """

    for i, product in enumerate(products):
        product["X"] = tsne_features[i, 0]
        product["Y"] = tsne_features[i, 1]

    df = pd.DataFrame(products)
    df["X"] = tsne_features[:, 0]
    df["Y"] = tsne_features[:, 1]

    fig = px.scatter(
        df,
        x="X",
        y="Y",
        hover_data="product",
        color_discrete_sequence=["pink"],
        # title="2D t-SNE Visualization of Cosmetic Products",
    )

    fig.update_layout(
        # title="t-SNE of Cosmetic Products",
        title="Ingredient Similarity",
        title_x=0.5,
        xaxis_title="t-SNE 1",
        yaxis_title="t-SNE 2",
        template="seaborn",
    )
    fig.update_traces(marker=dict(size=8, opacity=0.9))

    fig.update_layout(
        font_family="Rockwell",
    )
    fig.show()

    return df


# EXAMPLE: t-SNE Face Plot
ingredient_index_map = ingredient_idx(products)
m = len(products)
n = len(ingredient_index_map)
a = np.zeros((m, n))

for i, product in enumerate(products):
    a[i, :] = oh_encoder(product["ingredients"], ingredient_index_map)

model = TSNE(n_components=2, learning_rate=200)
tsne_features = model.fit_transform(a)
tsne_plot(products)


def find_most_similar_cosine(product_index, products, n_similar=5):
    """
    Finds the n most similar products based on cosine similarity using t-SNE features.
    ----------
    product_index : int
        The index of the target product in the products list.
    products : list
        List of products with 'X' and 'Y' t-SNE attributes.
    n_similar : int
        Number of similar products to return.
    Returns
    -------
    list
        A list of n most similar products.
    """
    target_product = products[product_index]
    target_category = target_product["category"]

    same_category_products = [p for p in products if p["category"] == target_category]
    tsne_features = np.array([[p["X"], p["Y"]] for p in same_category_products])

    target_feature = np.array([[target_product["X"], target_product["Y"]]])
    similarities = cosine_similarity(target_feature, tsne_features)[0]

    sorted_indices = np.argsort(similarities)[::-1][1 : n_similar + 1]
    return [same_category_products[i] for i in sorted_indices]


# EXAMPLE
similar_products = find_most_similar_cosine(0, products)
print("Finding most similar products for: " + products[0]["product"])
for product in similar_products:
    print(product["product"])
    print(product["ingredients"])

similar_products = find_most_similar_cosine(1, products)
print("Finding most similar products for: " + products[1]["product"])
for product in similar_products:
    print(product["product"])
    print(product["ingredients"])
