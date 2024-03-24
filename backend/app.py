import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")
ingredient_file_path = os.path.join(current_directory, "dislikes.json")

eyes_csv_path = os.path.join(current_directory, "scraping/face_ulta_data.csv")

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
    matches = df[df["product"].str.lower().str.contains(query.lower())]
    matches_filtered = matches[["product"]]
    matches_filtered_json = matches_filtered.to_json(orient="records")
    return matches_filtered_json


def csv_search(query):
    matches = []
    matches = eyes_df[eyes_df["product"].str.lower().str.contains(query.lower())]
    matches_filtered = matches[["product", "price", "ingredients", "link"]]
    matches_filtered_json = matches_filtered.to_json(orient="records")
    return matches_filtered_json


def results_search(query, min_price, max_price):
    matches = []
    matches = df[
        (df["product"].str.lower().str.contains(query.lower()))
        & (df["price"] >= min_price)
        & (df["price"] <= max_price)
    ]
    matches_filtered = matches[
        ["product", "link", "price", "img_link", "ingredients", "avg_rating", "reviews"]
    ]
    matches_filtered_json = matches_filtered.to_json(orient="records")
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
    return results_search(input_keywords[0], min_price, max_price)


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
