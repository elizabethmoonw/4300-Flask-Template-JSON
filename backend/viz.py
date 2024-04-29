import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from utils import find_most_similar_cosine_filtered, ingredient_idx, oh_encoder
from sklearn.metrics.pairwise import cosine_similarity


# fake cosine function on ingredients
def find_most_similar_cosine_filtered(product_index, products_df):
    ingredient_index_map = ingredient_idx(products_df)
    products_df["ingredients_vector"] = products_df["ingredients"].apply(
        lambda x: oh_encoder(x, ingredient_index_map)
    )

    vectors = np.stack(products_df["ingredients_vector"])
    target_vector = vectors[product_index].reshape(1, -1)
    similarities = cosine_similarity(target_vector, vectors).flatten()

    sorted_indices = np.argsort(similarities)[::-1][1:]
    return products_df.iloc[sorted_indices].head(10), similarities[sorted_indices[:10]]


def plot_similarity_heatmap(
    target_product_index, most_similar_products, cosine_similarities, products_df
):
    fig = go.Figure(
        data=go.Heatmap(
            z=[cosine_similarities],
            y=most_similar_products["product"],
            x=["Similarity"],
            colorscale="magenta",
            transpose=True,
        )
    )

    fig.update_layout(
        title=f"Cosine Similarity of {products_df.iloc[target_product_index]['product']} to Recommendations",
        # xaxis=dict(tickangle=90),
        margin=dict(l=60, r=60, t=60, b=60),
        # font=dict(family="Balto", size=15),
    ),

    fig.show()


json_file_path = "init.json"

with open(json_file_path, "r") as file:
    data = json.load(file)
    df = pd.DataFrame(data["products"])

# print(find_most_similar_cosine_filtered(0, df))

target_product_idx = 0
most_similar_products, similarities = find_most_similar_cosine_filtered(
    target_product_idx, df
)

# print(most_similar_products["product"])
plot_similarity_heatmap(target_product_idx, most_similar_products, similarities, df)
