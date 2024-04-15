import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from utils import (
    reverse_product_idx,
    find_most_similar_cosine_filtered,
    ingredient_boolean_search,
)

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")
ingredient_file_path = os.path.join(current_directory, "dislikes.json")

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

eyes_df = pd.read_csv(eyes_csv_path)

model = SentenceTransformer("all-MiniLM-L12-v2")
product_names = df["product"].tolist()
product_embeddings = model.encode(product_names, convert_to_tensor=True)

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


def results_search(query, min_price, max_price, product, dislikes):
    # matches = []
    # matches = df[(df["product"].str.lower().str.contains(query.lower()))]
    # print("before matches")
    # print(len(df))
    # print(len(ingred_filtered))
    # print(product)
    best_matches = find_most_similar_cosine_filtered(
        reverse_product_idx(df, product), df
    )
    ingred_filtered = ingredient_boolean_search(best_matches, dislikes)
    filter_matches = ingred_filtered[
        (ingred_filtered["price"] >= min_price)
        & (ingred_filtered["price"] <= max_price)
    ][:10]
    # print("after matches")
    matches_filtered = filter_matches[
        ["product", "link", "price", "img_link", "ingredients", "avg_rating", "reviews"]
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


@app.route("/")
def home():
    return render_template("base.html", title="sample html")


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return csv_search(text)


@app.route("/filter")
def filter_search():
    dislikes = request.args.get("dislikes")
    input_dislikes = [dislikes]
    keywords = request.args.get("keywords")
    input_keywords = [keywords]
    min_price = float(request.args.get("minPrice"))
    max_price = float(request.args.get("maxPrice"))
    product = request.args.get("product")
    return results_search(
        input_keywords[0], min_price, max_price, product, input_dislikes
    )


@app.route("/search")
def searchProducts():
    text = request.args.get("title")
    return json_search(text)


@app.route("/dislikes")
def searchIngredients():
    text = request.args.get("title")
    return dislike_search(text)


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5000)
