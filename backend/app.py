import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
from utils import (
    reverse_product_idx,
    find_most_similar_cosine_filtered,
    ingredient_boolean_search,
    create_ingredient_mat,
    get_top_shades,
    filter_shades,
    rocchio,
)


# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")
ingredient_file_path = os.path.join(current_directory, "dislikes.json")
tag_file_path = os.path.join(current_directory, "tags.json")

eyes_csv_path = os.path.join(current_directory, "scraping/eyes_ulta_data.csv")

# Assuming your JSON data is stored in a file named 'init.json'
# with open(json_file_path, "r") as file:
#     data = json.load(file)
#     episodes_df = pd.DataFrame(data["episodes"])
#     reviews_df = pd.DataFrame(data["reviews"])

with open(json_file_path, "r") as file:
    data = json.load(file)
    df = pd.DataFrame(data["products"])

with open(ingredient_file_path, "r") as file:
    data = json.load(file)
    ingredients_df = pd.DataFrame(data)

with open(tag_file_path, "r") as file:
    data = json.load(file)
    tags_df = pd.DataFrame(data)

eyes_df = pd.read_csv(eyes_csv_path)

model = SentenceTransformer("all-MiniLM-L12-v2")
product_names = df["product"].tolist()
product_embeddings = model.encode(product_names, convert_to_tensor=True)
create_ingredient_mat(df)

app = Flask(__name__)
CORS(app)


# Sample search using json with pandas
def json_search(query):
    matches = []
    # print(df)
    # merged_df = pd.merge(
    #     episodes_df, reviews_df, left_on="id", right_on="id", how="inner"
    # )
    # matches = merged_df[merged_df["title"].str.lower().str.contains(query.lower())]
    if len(query) < 4:
        matches = df[df["product"].str.lower().str.contains(query.lower())]
        matches_filtered = matches[["product"]]
        matches_filtered_json = matches_filtered.to_json(orient="records")
        # print(matches_filtered_json)
    else:
        query_embedding = model.encode(query, convert_to_tensor=True)
        results = util.semantic_search(query_embedding, product_embeddings, top_k=10)
        results = results[0]
        matches = [product_names[res["corpus_id"]] for res in results]
        matches_filtered_json = json.dumps([{"product": match} for match in matches])
        # print(matches_filtered_json)
    return matches_filtered_json


def csv_search(query):
    matches = []
    matches = eyes_df[eyes_df["product"].str.lower().str.contains(query.lower())]
    matches_filtered = matches[["product", "price", "ingredients", "link"]]
    matches_filtered_json = matches_filtered.to_json(orient="records")
    return matches_filtered_json


def results_search(
    query,
    min_price,
    max_price,
    product,
    dislikes,
    shade,
    upvoted=[],
    downvoted=[],
    refine=False,
):
    # print(upvoted)
    # print(downvoted)
    # matches = []
    # matches = df[(df["product"].str.lower().str.contains(query.lower()))]
    # print("before matches")
    # print(len(df))
    # print(len(ingred_filtered))
    # print(product)
    product_vec = None
    if refine:
        # print("LSDkfjsd")
        if len(upvoted) != 0:
            upvoted_list = upvoted.split(",")
            # print(upvoted_list)
        else:
            upvoted_list = []
        if len(downvoted) != 0:
            downvoted_list = downvoted.split(",")
            # print(downvoted_list)
        else:
            downvoted_list = []
        product_index = reverse_product_idx(product, product_names)
        target_product = df.iloc[product_index]
        # print("prod vec length " + str(len(target_product["tag_vectors"])))
        product_vec = np.asarray(target_product["tag_vectors"], dtype=np.float32)
        product_vec = rocchio_update(product_vec, downvoted_list, upvoted_list)

    best_matches = find_most_similar_cosine_filtered(
        reverse_product_idx(product, product_names),
        df,
        n_similar=10,
        product_vector=product_vec,
    )

    # else:
    #     best_matches = find_most_similar_cosine_filtered(
    #         reverse_product_idx(product, product_names), df
    #     )

    if best_matches.size == 0:
        return best_matches.to_json(orient="records")

    if len(dislikes) != 0:
        dislikes_list = dislikes[0].split(",")
        ingred_filtered = ingredient_boolean_search(best_matches, dislikes_list)
    else:
        ingred_filtered = best_matches
    # print(ingred_filtered)
    filter_matches = ingred_filtered[
        (ingred_filtered["price"] >= min_price)
        & (ingred_filtered["price"] <= max_price)
    ][:10]
    if shade == "" or "undefined" in shade:
        shade_list = []
    else:
        shade_list = [int(x) for x in shade.split(",")]
    shade_matches = get_top_shades(shade_list, filter_matches)
    # print(shade_matches)
    filter_matches = filter_shades(shade_matches, filter_matches)
    # print("after matches")
    matches_filtered = filter_matches[
        [
            "product",
            "link",
            "price",
            "img_link",
            "ingredients",
            "avg_rating",
            "reviews",
            "summary",
            "closest_shade_name",
            "closest_shade_rgb",
            "tags",
        ]
    ]
    matches_filtered_json = matches_filtered.to_json(orient="records")
    # print("json" + matches_filtered_json)
    return matches_filtered_json


def dislike_search(query):
    matches = []
    matches = ingredients_df.loc[
        ingredients_df["ingredients"].str.lower().str.contains(query.lower())
    ]
    matches_filtered = matches
    matches_filtered_json = matches_filtered.to_json(orient="records")
    return matches_filtered_json


def suggest_search(
    input_keyword,
    min_price,
    max_price,
    input_dislikes,
    # upvoted=[],
    # downvoted=[],
    # refine=False,
):
    category = ""
    makeup_types = [
        "foundation",
        "face-powder",
        "face powder",
        "concealer",
        "face-primer",
        "face primer",
        "bb-cc-creams",
        "bb cream",
        "cc cream",
        "blush",
        "bronzer",
        "contouring",
        "highlighter",
        "lipstick",
        "lip-gloss",
        "lip gloss",
        "lip-oil",
        "lip oil",
        "lip-liner",
        "lip liner",
        "lip-stain",
        "lip stain",
        "lip-balms-treatments",
        "lip balm",
        "eyeshadow-palettes",
        "eyeshadow palettes",
        "mascara",
        "eyeliner",
        "eyebrows",
        "eyeshadow",
    ]
    for cat in makeup_types:
        if cat in input_keyword:
            category = cat

    # product_vec = None
    # if refine:
    #     product_vec = np.zeros((1, 768))
    #     product_vec = rocchio_update(product_vec, downvoted, upvoted)

    matches = df

    # matches = find_most_similar_cosine_filtered(
    #     reverse_product_idx(product, product_names),
    #     df,
    #     n_similar=10,
    #     product_vector=product_vec,
    # )

    if category != "":
        matches = df.loc[matches["category"] == category]

    # matches = df[(df["product"].str.lower().str.contains(input_keyword.lower()))]

    ingred_filtered = ingredient_boolean_search(matches, input_dislikes)
    filter_matches = ingred_filtered[
        (ingred_filtered["price"] >= min_price)
        & (ingred_filtered["price"] <= max_price)
    ]
    input_keyword = input_keyword.split(",")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    input_embeddings = model.encode(input_keyword)
    product_tags = filter_matches["tags"]
    similarities = np.zeros((len(filter_matches)))
    for kw in input_embeddings:
        for i, product in enumerate(list(product_tags)):
            for j, tag in enumerate(list(product)):
                sim = util.pytorch_cos_sim(
                    np.array(kw, dtype=np.float32),
                    np.array(tags_df[tag], dtype=np.float32),
                )
                if sim[0][0] > 0.8:
                    similarities[i] += sim
    sorted_indices = np.argsort(similarities)[::-1][:10]
    filter_matches = filter_matches.iloc[sorted_indices]

    matches_filtered = filter_matches[
        [
            "product",
            "link",
            "price",
            "img_link",
            "ingredients",
            "avg_rating",
            "reviews",
            "summary",
            "tags",
        ]
    ]
    matches_filtered_json = matches_filtered.to_json(orient="records")
    return matches_filtered_json


def rocchio_update(product_vec, down_voted, up_voted):
    # if product is not None:
    #     product_vec = product["tag_vectors"]
    # else:
    #     product_vec = np.zeros((1, 768))
    # print("product vec shape " + str(product_vec.shape))
    # down_voted_vec = [np.zeros((384))]
    down_voted_vec = []
    for p in down_voted:
        prod = reverse_product_idx(p, product_names)
        # print(len(prod["tag_vectors"]))
        down_voted_vec.append(df.iloc[prod]["tag_vectors"])
    down_voted_vec = np.array(down_voted_vec, dtype=np.float32)

    # up_voted_vec = np.zeros((384))
    up_voted_vec = []
    for p in up_voted:
        prod = reverse_product_idx(p, product_names)
        up_voted_vec.append(df.iloc[prod]["tag_vectors"])
    up_voted_vec = np.array(up_voted_vec, dtype=np.float32)
    # up_voted_vec += df.iloc[prod]["tag_vectors"]
    # down_voted_vec = [p["tag_vectors"] for p in down_voted]
    # up_voted_vec = [p["tag_vectors"] for p in up_voted]
    # print("query vec shape " + str(product_vec.shape))
    # print("up vec shape " + str(up_voted_vec.shape))
    # print("down vec shape " + str(down_voted_vec.shape))

    return rocchio(
        query_vector=product_vec,
        relevant_vectors=up_voted_vec,
        irrelevant_vectors=down_voted_vec,
    )


def shade_search(product):
    # print("product " + product)
    product_row = df.loc[
        df["product"].str.lower().str.strip() == product.lower().strip()
    ].iloc[0]
    # print(product_row)
    if len(product_row["shades"]) != 0:
        # print([shade["shade_rgb"] for shade in product_row["shades"]])
        return [
            [shade["shade_rgb"], shade["shade_name"]] for shade in product_row["shades"]
        ]
    else:
        return []


def prod_search(product):
    # print("product " + product)
    match = df.loc[
        df["product"].str.lower().str.strip() == product.lower().strip()
    ].iloc[:1]

    if match.empty:
        return match.to_json(orient="records")

    match["closest_shade_name"] = [""]
    match["closest_shade_rgb"] = [[]]
    # print(match)
    match_filtered = match[
        [
            "product",
            "link",
            "price",
            "img_link",
            "ingredients",
            "avg_rating",
            "reviews",
            "summary",
            "closest_shade_name",
            "closest_shade_rgb",
            "tags",
        ]
    ]
    match_filtered_json = match_filtered.to_json(orient="records")
    return match_filtered_json


@app.route("/")
def home():
    return render_template("base.html", title="sample html")


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return csv_search(text)


@app.route("/product")
def product_search():
    text = request.args.get("title")
    return prod_search(text)


@app.route("/filter")
def filter_search():
    dislikes = request.args.get("dislikes")
    input_dislikes = [dislikes]
    keywords = request.args.get("keywords")
    input_keywords = [keywords]
    min_price = float(request.args.get("minPrice"))
    max_price = float(request.args.get("maxPrice"))
    product = request.args.get("product")
    shade = request.args.get("shade")
    refine_str = request.args.get("refine")
    if refine_str == "true":
        refine = True
    else:
        refine = False
    upvoted = request.args.get("upvoted")
    downvoted = request.args.get("downvoted")
    return results_search(
        input_keywords[0],
        min_price,
        max_price,
        product,
        input_dislikes,
        shade,
        upvoted,
        downvoted,
        refine,
    )


@app.route("/suggest")
def suggestion_search():
    dislikes = request.args.get("dislikes")
    input_dislikes = [dislikes]
    keywords = request.args.get("keywords")
    input_keywords = [keywords]
    min_price = float(request.args.get("minPrice"))
    max_price = float(request.args.get("maxPrice"))
    return suggest_search(input_keywords[0], min_price, max_price, input_dislikes)


@app.route("/search")
def searchProducts():
    text = request.args.get("title")
    return json_search(text)


@app.route("/dislikes")
def searchIngredients():
    text = request.args.get("title")
    return dislike_search(text)


@app.route("/shades")
def searchShades():
    text = request.args.get("title")
    return shade_search(text)


# @app.route("/refine_filter")
# def refineSearch():
#     text = request.args.get


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
