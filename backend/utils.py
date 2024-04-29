import json
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import util
import os
import math

ingredient_mat = {}


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
    unique_ingredients = set()
    for ingredients in products_df["ingredients"]:
        unique_ingredients.update(ingredients)

    ingredient_index = {
        ingredient: i for i, ingredient in enumerate(sorted(unique_ingredients))
    }
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
    indices = [
        ingredient_index_map[ing]
        for ing in product_ingredients
        if ing in ingredient_index_map
    ]
    x[indices] = 1
    return x


# All prods
def encode_ingredients(products_df):
    ingredient_index_map = ingredient_idx(products_df)
    encoded_data = np.zeros((len(products_df), len(ingredient_index_map)))

    for i, product in products_df.iterrows():
        encoded_data[i, :] = oh_encoder(product["ingredients"], ingredient_index_map)

    return encoded_data


# dimensionality reduction
def create_tsne(products_df: pd.DataFrame, encoded_matrix):
    tsne = TSNE(n_components=2, learning_rate=200, random_state=1)
    tsne_features = tsne.fit_transform(encoded_matrix)

    products_df["X"] = tsne_features[:, 0]
    products_df["Y"] = tsne_features[:, 1]

    return products_df


def reverse_product_idx(product: str, product_names: list):
    if product in product_names:
        return product_names.index(product)
    return -1


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
    if product_index == -1:
        return pd.DataFrame()

    target_product = products_df.iloc[product_index]
    target_category = target_product["category"]

    ingredient_index_map = ingredient_idx(products_df)
    products_df["ingredients_vector"] = products_df["ingredients"].apply(
        lambda x: oh_encoder(x, ingredient_index_map)
    )
    same_category_products = products_df[products_df["category"] == target_category]
    vectors = np.array(
        [p["ingredients_vector"] for _, p in same_category_products.iterrows()]
    )

    target_feature = [products_df.iloc[product_index]["ingredients_vector"]]
    similarities = cosine_similarity(target_feature, vectors)[0]

    target_tags = products_df.iloc[product_index]["tag_vectors"]
    tag_vectors = np.array(
        [p["tag_vectors"] for _, p in same_category_products.iterrows()],
        dtype=np.float32,
    )

    tag_similarities = np.array(util.pytorch_cos_sim(target_tags, tag_vectors)).reshape(
        similarities.shape
    )
    # tag_similarities = cosine_similarity(target_tags, tag_vectors)[0]
    similarities = np.multiply(np.power(tag_similarities, 20), similarities)

    sorted_indices = np.argsort(similarities)[::-1][1:]
    return same_category_products.iloc[sorted_indices]


def ingredient_boolean_search(products_df, disliked_ingredients):
    """
    Filters out products that contain the specified disliked ingredients
    ----------
    disliked_ingredients: string list
    """
    dislikes = products_df["ingredients"].apply(
        lambda ingredients: not any(
            ingredient in disliked_ingredients for ingredient in ingredients
        )
    )
    output_df = products_df[dislikes]
    return output_df


# The "default values are: alpha=1, beta=0.75, gamma=0.15"
def rocchio(
    query_vector, relevant_vectors, irrelevant_vectors, alpha=0.3, beta=0.3, gamma=0.8
):
    """
    Performs Rocchio's algorithm to update vector weights
    ----------
    query_idx : int
        the input query index
    relevant_indices : int
        the indices of relevant products
    irrelevant_indices : int
        the indices of irrelevant products
    Returns
    -------
    list
         updated query weight vector
    """
    relevant_mean = np.mean(relevant_vectors, axis=0)
    irrelevant_mean = (
        np.mean(irrelevant_vectors, axis=0)
        if irrelevant_vectors.size > 0
        else np.zeros_like(query_vector)
    )

    # print("Relevant Mean Norm:", np.linalg.norm(relevant_mean))
    # print("Irrelevant Mean Norm:", np.linalg.norm(irrelevant_mean))

    updated_query = (
        alpha * query_vector + beta * relevant_mean - gamma * irrelevant_mean
    )

    # print("Original:", np.linalg.norm(query_vector))
    # print("Updated:", np.linalg.norm(updated_query))
    return updated_query


def save_encoded_matrix(encoded_matrix):
    np.save("encoded_matrix.npy", encoded_matrix)


def load_encoded_matrix():
    return np.load("encoded_matrix.npy")


def load_products(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == ".json":
        return pd.read_json(file_path)
    elif file_extension == ".csv":
        return pd.read_csv(file_path)


def create_ingredient_mat(products_df):
    ingredient_mat = ingredient_idx(products_df)


def get_top_shades(shade_rgb, relevant_products):
    """
    Given a shade and list of relevant products, return the closest shades for each relevant products
    ----------
    shade_rgb : list
        A list containing the 3-tuple RGB value
    products : dict
        A dict of relevant product as keys and their shade information as values
    Returns
    -------
    dict
        dict mapping product name to tuple containing (list of rgb, product name)
    """
    # print(shade_rgb)
    # print(relevant_products)
    best_shades = {}
    if shade_rgb == []:
        return best_shades

    for ind in relevant_products.index:
        product = relevant_products["product"][ind]
        shade_info = relevant_products["shades"][ind]
        # print(shade_info)
        try:
            shade_diff = np.ones(len(shade_info))
            for shade_i in range(len(shade_info)):
                rgb = shade_info[shade_i]["shade_rgb"]
                if len(rgb) > 0:
                    shade_diff[shade_i] = math.sqrt(
                        (rgb[0] - shade_rgb[0]) ** 2
                        + (rgb[1] - shade_rgb[1]) ** 2
                        + (rgb[2] - shade_rgb[2]) ** 2
                    ) / math.sqrt(195075)
            try:
                closest_i = np.argmin(shade_diff)
                if shade_diff[closest_i] == 1:
                    continue
                else:
                    best_shades[product] = (
                        shade_info[closest_i]["shade_rgb"],
                        shade_info[closest_i]["shade_name"],
                    )
            except:
                continue
        except SyntaxError:
            continue

    # print(best_shades)
    return best_shades


def filter_shades(shade_matches, top_10_df):
    """
    If result product has a closest shade, add the shade to the result
    ----------
    shade_matches : dict
        dict mapping product name to tuple containing (list of rgb, product name)
    top_10_df : dataframe
        dataframe of length 10 with top 10 similar products
    Returns
    -------
    dataframe
        dataframe with two new columns: closest_shade_name and closest_shade_rgb
    """
    new_shade_names = []
    new_shade_rgbs = []
    for ind in top_10_df.index:
        product = top_10_df["product"][ind]
        if product in shade_matches:
            raw_shade_name = shade_matches[product][1]
            # print("raw " + raw_shade_name)
            brand = top_10_df["brand"][ind]
            # print("brand " + brand)
            # new_shade_names.append(shade_matches[product][1])
            new_shade_rgbs.append(shade_matches[product][0])
            try:
                prod_name = product[product.index(brand) + len(brand) + 1 :]
                # print(prod_name)
                new_shade_name = raw_shade_name[
                    : shade_matches[product][1].index(prod_name) - 1
                ]
                new_shade_names.append(new_shade_name)
            except:
                new_shade_names.append("")
        else:
            new_shade_names.append("")
            new_shade_rgbs.append([])
            # top_10_df.loc[top_10_df["product"] == product, "closest_shade_name"] = (
            #     shade_matches[product][1]
            # )
            # top_10_df.loc[top_10_df["product"] == product, "closest_shade_rgb"] = (
            #     shade_matches[product][0]
            # )
    top_10_df["closest_shade_name"] = new_shade_names
    top_10_df["closest_shade_rgb"] = new_shade_rgbs
    # print(top_10_df)
    return top_10_df


BASE_DIR = os.path.abspath(".")
DATASET_DIR = os.path.join(BASE_DIR, "data")
products_file_path = os.path.join(DATASET_DIR, "tagged_products.csv")

products_df = load_products(products_file_path)

encoded_matrix = encode_ingredients(products_df)
save_encoded_matrix(encoded_matrix)
load_encoded_matrix()
