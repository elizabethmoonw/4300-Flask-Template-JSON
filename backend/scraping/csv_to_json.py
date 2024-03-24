# adapted from https://www.geeksforgeeks.org/convert-csv-to-json-using-python/
import csv
import json
import re


# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json(csv_list, jsonFilePath):
    data = {}
    data["products"] = []

    for csvFilePath in csv_list:
        # create a dictionary
        # Open a csv reader called DictReader
        with open(csvFilePath, encoding="utf-8") as csvf:
            csvReader = csv.DictReader(csvf)

            # Convert each row into a dictionary
            # and add it to data
            for rows in csvReader:
                new_rows = rows
                if csvFilePath == "face_ulta_data.csv":
                    new_rows["product"] = rows["brand"] + " " + rows["product"]

                # price
                # if rows["price"] == "":
                # continue
                if rows["price"].startswith("Sale"):
                    try:
                        new_rows["price"] = float(
                            rows["price"][
                                rows["price"].rindex("$")
                                + 1 : rows["price"].rindex(".")
                                + 3
                            ]
                        )
                    except:
                        continue
                else:
                    new_rows["price"] = float(
                        rows["price"][
                            rows["price"].index("$") + 1 : rows["price"].index(".") + 3
                        ]
                    )

                # avg rating
                new_rows["avg_rating"] = float(rows["avg_rating"])

                # ingredients
                new_rows["ingredients"] = rows["ingredients"][:-1].split(", ")

                # shades
                shades = rows["shades"][2:-2].split("], [")
                new_shades = []

                for shade in shades:
                    if ", (" in shade:
                        if "array" not in shade:
                            shade_rgb = shade[
                                shade.rindex("(") + 1 : shade.rindex(")")
                            ].split(", ")
                            for i in range(len(shade_rgb)):
                                shade_rgb[i] = int(shade_rgb[i])
                        else:
                            shade_rgb = []
                        shade_tokens = shade[: shade.rindex(", (")].split(", ")
                        shade_name = shade_tokens[0][1:-2]
                        shade_img = shade_tokens[1][1:-1]
                        new_shade = {
                            "shade_name": shade_name,
                            "shade_img": shade_img,
                            "shade_rgb": shade_rgb,
                        }
                        new_shades.append(new_shade)
                new_rows["shades"] = new_shades

                # reviews
                # new_reviews = []

                reviews = rows["reviews"][2:-2]
                new_reviews = re.split("', \"|\", '|\", \"|', '", reviews)
                new_rows["reviews"] = new_reviews

                # for review in reviews:
                #     new_review = review.split("', '")
                #     new_reviews.extend(new_review)

                # med_1_reviews = []

                # for review in new_reviews:
                #     new_review = review.split("', \"")
                #     med_1_reviews.extend(new_review)

                # med_2_reviews = []

                # for review in med_1_reviews:
                #     new_review = review.split("\", '")
                #     med_2_reviews.extend(new_review)

                # final_reviews = []

                # for review in med_2_reviews:
                #     new_review = review.split('", "')
                #     final_reviews.extend(new_review)

                # new_rows["reviews"] = final_reviews

                data["products"].append(new_rows)

        # Open a json writer, and use the json.dumps()
        # function to dump data
        with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(data, indent=2))


# make_json("face_ulta_data.csv", "face_ulta_data.json")
# make_json("eyes_ulta_data.csv", "eyes_ulta_data.json")
make_json(["face_ulta_data.csv", "eyes_ulta_data.csv"], "all_data.json")
