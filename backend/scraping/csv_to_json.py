# adapted from https://www.geeksforgeeks.org/convert-csv-to-json-using-python/
import csv
import json
import re


# Function to convert a CSV to JSON
# Takes the file paths as arguments


def filter_ingredients(ingred_list):
    new_ingredients = ingred_list
    new_ingredients = [ingred.lower().strip() for ingred in new_ingredients]
    new_ingredients = [ingred.replace("'", "") for ingred in new_ingredients]
    new_ingredients = list(filter(None, new_ingredients))
    new_ingredients = list(
        filter(
            lambda x: x != " "
            and "ci " not in x
            and len(x) > 2
            and "please be aware" not in x
            and "please refer" not in x
            and "for the most" not in x
            and "----" not in x
            and "*" not in x
            and "when in rome" not in x
            and "\u202d" not in x
            and "\u00e9" not in x
            and "may contain" not in x
            and "styrene/acrylates copolymer propylene glycol laureth-21 pentylene"
            not in x
            and not x.startswith("(")
            and not x.startswith(".")
            and not x.startswith("/")
            and not x.startswith(",")
            and not x.startswith(";")
            and "\\\\\\" not in x
            and "<" not in x
            and ">" not in x
            and not x.startswith("20")
            and not x.startswith("22")
            and not x.startswith("23")
            and not x.startswith("77")
            and not x.startswith("8")
            and not x.startswith("9")
            and "%" not in x,
            new_ingredients,
        )
    )
    new_ingredients = [
        ("water" if "water" in token or "aqua" in token or "eau" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        ("fragrance" if "fragrance" in token or "parfum" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        (
            "beeswax"
            if "beesxwax" in token
            or "cire d'abeille" in token
            or "cera alba" in token
            or "bees wax" in token
            else token
        )
        for token in new_ingredients
    ]
    new_ingredients = [
        ("bis-diglyceryl polyacyladipate" if "bis-diglyceryl" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        (
            "carnauba wax"
            if "carnauba wax" in token or "copernicia cerifera" in token
            else token
        )
        for token in new_ingredients
    ]
    new_ingredients = [
        ("dimethicone" if "dimethicone" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        (
            "euphorbia cerifera wax"
            if "euphorbia cerifera" in token or "candelilla" in token
            else token
        )
        for token in new_ingredients
    ]
    new_ingredients = [
        ("vinyl dimethicone" if "vinyl dimethicone" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        ("yeast extract" if "yeast extract" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        ("tocopheryl acetate" if "tocopheryl acetate" in token else token)
        for token in new_ingredients
    ]
    new_ingredients = [
        ("titanium dioxide" if "titanium dioxide" in token else token)
        for token in new_ingredients
    ]
    return new_ingredients


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
            for i, rows in enumerate(csvReader):
                # key = i
                new_rows = {}
                # new_rows["id"] = float(rows["id"])
                new_rows.update(rows)
                new_rows["id"] = int(rows["id"])
                del new_rows[""]

                new_rows["product"] = (
                    rows["product"]
                    .replace("ÃÂ´", "ô")
                    .replace("ÃÂ©", "é")
                    .replace("ÃÂ¨", "è")
                )

                # if (
                #     csvFilePath == "face_ulta_data.csv"
                #     or csvFilePath == "lips_ulta_data.csv"
                # ):
                #     new_rows["product"] = rows["brand"] + " " + rows["product"]

                # # price
                # if rows["price"].startswith("Sale"):
                #     try:
                #         new_rows["price"] = float(
                #             rows["price"][
                #                 rows["price"].rindex("$")
                #                 + 1 : rows["price"].rindex(".")
                #                 + 3
                #             ]
                #         )
                #     except:
                #         continue
                # else:
                #     new_rows["price"] = float(
                #         rows["price"][
                #             rows["price"].index("$") + 1 : rows["price"].index(".") + 3
                #         ]
                #     )
                new_rows["price"] = float(rows["price"])

                # avg rating
                new_rows["avg_rating"] = float(rows["avg_rating"])

                # ingredients
                # new_rows["ingredients"] = rows["ingredients"][:-1].split(", ")
                ingredients = rows["ingredients"]
                if ingredients.startswith("WARNING"):
                    new_ingredients = []
                else:
                    if "May Contain" in ingredients:
                        ingredients = ingredients[
                            : ingredients.index("May Contain") - 1
                        ]
                    if ingredients.endswith("."):
                        ingredients = ingredients[:-1]
                    if "Iron Oxides " in ingredients:
                        new_ingredients = re.split(
                            ", |\. | \d+%| \d+\.\d+%|Inactive: |Active: |.*: |\+ / \-|\[|\]|\+/\-| Iron Oxides",
                            ingredients,
                        )
                    else:
                        new_ingredients = re.split(
                            ", |\. | \d+%| \d+\.\d+%|Inactive: |Active: |.*: |\+ / \-|\[|\]|\+/\-",
                            ingredients,
                        )
                    new_ingredients = filter_ingredients(new_ingredients)

                new_rows["ingredients"] = new_ingredients

                # shades
                # shades = rows["shades"][2:-2].split("], [")
                # new_shades = []

                # for shade in shades:
                #     if ", (" in shade:
                #         if "array" not in shade:
                #             shade_rgb = shade[
                #                 shade.rindex("(") + 1 : shade.rindex(")")
                #             ].split(", ")
                #             for i in range(len(shade_rgb)):
                #                 shade_rgb[i] = int(shade_rgb[i])
                #         else:
                #             shade_rgb = []
                #         shade_tokens = shade[: shade.rindex(", (")].split(", ")
                #         shade_name = shade_tokens[0][1:-2]
                #         shade_img = shade_tokens[1][1:-1]
                #         new_shade = {
                #             "shade_name": shade_name,
                #             "shade_img": shade_img,
                #             "shade_rgb": shade_rgb,
                #         }
                #         new_shades.append(new_shade)
                # new_rows["shades"] = new_shades

                # new_rows["shades"] = [
                #     json.loads(shade)
                #     for shade in rows["shades"][1:-1].replace("'", '"')
                # ]
                if rows["shades"][1:-1] == "":
                    new_rows["shades"] = []
                else:
                    # print(rows["shades"][1:-1])
                    old_shades = rows["shades"][2:-2].split("}, {")
                    # print(old_shades)
                    new_shades = []
                    for shade in old_shades:
                        new_shade = {}
                        new_shade["shade_name"] = shade[
                            shade.index(":") + 3 : shade.index(",") - 1
                        ]
                        if "https" not in shade:
                            new_shade["shade_img"] = ""
                        else:
                            new_shade["shade_img"] = shade[
                                shade.index("https") : shade.index("shade_rgb") - 4
                            ]
                        # print(
                        #     shade[shade.index("[") + 1 : shade.index("]")].split(", ")
                        # )
                        if shade[shade.rindex("[") + 1 : shade.rindex("]")] == "":
                            new_shade["shade_rgb"] = []
                        else:
                            # print(shade[shade.index("[") + 1 : shade.index("]")])
                            new_shade["shade_rgb"] = list(
                                map(
                                    int,
                                    shade[
                                        shade.rindex("[") + 1 : shade.rindex("]")
                                    ].split(", "),
                                )
                            )
                        new_shades.append(new_shade)
                    new_rows["shades"] = new_shades

                # reviews
                # new_reviews = []

                reviews = rows["reviews"][2:-2]
                # if len(reviews) == 1 and reviews[0] == "":
                #     new_reviews = []
                # else:
                new_reviews = re.split("', \"|\", '|\", \"|', '", reviews)
                new_reviews = list(
                    filter(lambda x: "Comments about " not in x, new_reviews)
                )
                new_rows["reviews"] = new_reviews

                data["products"].append(new_rows)
                new_rows["summary"] = rows["summary"]
                if rows["tags"][1:-1] == "":
                    new_rows["tags"] = []
                else:
                    new_rows["tags"] = rows["tags"][2:-2].split("', '")
                # data[key] = new_rows

        # Open a json writer, and use the json.dumps()
        # function to dump data
        print("number of products: ", len(data["products"]))

        with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(data, indent=2))


# def make_json(csv_list, jsonFilePath):
#     data = {}
#     data["products"] = []

#     for csvFilePath in csv_list:
#         # create a dictionary
#         # Open a csv reader called DictReader
#         with open(csvFilePath, encoding="latin-1") as csvf:
#             csvReader = csv.DictReader(csvf)

#             # Convert each row into a dictionary
#             # and add it to data
#             for i, rows in enumerate(csvReader):
#                 key = i
#                 new_rows = {}
#                 new_rows["id"] = i
#                 new_rows.update(rows)

#                 # if (
#                 #     csvFilePath == "face_ulta_data.csv"
#                 #     or csvFilePath == "lips_ulta_data.csv"
#                 # ):
#                 #     new_rows["product"] = rows["brand"] + " " + rows["product"]

#                 # # price
#                 # if rows["price"].startswith("Sale"):
#                 #     try:
#                 #         new_rows["price"] = float(
#                 #             rows["price"][
#                 #                 rows["price"].rindex("$")
#                 #                 + 1 : rows["price"].rindex(".")
#                 #                 + 3
#                 #             ]
#                 #         )
#                 #     except:
#                 #         continue
#                 # else:
#                 #     new_rows["price"] = float(
#                 #         rows["price"][
#                 #             rows["price"].index("$") + 1 : rows["price"].index(".") + 3
#                 #         ]
#                 #     )
#                 new_rows["price"] = float(rows["price"])

#                 # avg rating
#                 new_rows["avg_rating"] = float(rows["avg_rating"])

#                 # ingredients
#                 # new_rows["ingredients"] = rows["ingredients"][:-1].split(", ")
#                 ingredients = rows["ingredients"]
#                 if ingredients.startswith("WARNING"):
#                     new_ingredients = []
#                 else:
#                     if "May Contain" in ingredients:
#                         ingredients = ingredients[
#                             : ingredients.index("May Contain") - 1
#                         ]
#                     if ingredients.endswith("."):
#                         ingredients = ingredients[:-1]
#                     if "Iron Oxides " in ingredients:
#                         new_ingredients = re.split(
#                             ", |\. | \d+%| \d+\.\d+%|Inactive: |Active: |.*: |\+ / \-|\[|\]|\+/\-| Iron Oxides",
#                             ingredients,
#                         )
#                     else:
#                         new_ingredients = re.split(
#                             ", |\. | \d+%| \d+\.\d+%|Inactive: |Active: |.*: |\+ / \-|\[|\]|\+/\-",
#                             ingredients,
#                         )
#                     new_ingredients = filter_ingredients(new_ingredients)

#                 new_rows["ingredients"] = new_ingredients

#                 # shades
#                 shades = rows["shades"][2:-2].split("], [")
#                 new_shades = []

#                 for shade in shades:
#                     if ", (" in shade:
#                         if "array" not in shade:
#                             shade_rgb = shade[
#                                 shade.rindex("(") + 1 : shade.rindex(")")
#                             ].split(", ")
#                             for i in range(len(shade_rgb)):
#                                 shade_rgb[i] = int(shade_rgb[i])
#                         else:
#                             shade_rgb = []
#                         shade_tokens = shade[: shade.rindex(", (")].split(", ")
#                         shade_name = shade_tokens[0][1:-2]
#                         shade_img = shade_tokens[1][1:-1]
#                         new_shade = {
#                             "shade_name": shade_name,
#                             "shade_img": shade_img,
#                             "shade_rgb": shade_rgb,
#                         }
#                         new_shades.append(new_shade)
#                 new_rows["shades"] = new_shades

#                 # reviews
#                 # new_reviews = []

#                 reviews = rows["reviews"][2:-2]
#                 # if len(reviews) == 1 and reviews[0] == "":
#                 #     new_reviews = []
#                 # else:
#                 new_reviews = re.split("', \"|\", '|\", \"|', '", reviews)
#                 new_reviews = list(
#                     filter(lambda x: "Comments about " not in x, new_reviews)
#                 )
#                 new_rows["reviews"] = new_reviews

#                 data["products"].append(new_rows)
#                 new_rows["summary"] = rows["summary"]
#                 data[key] = new_rows

#         # Open a json writer, and use the json.dumps()
#         # function to dump data
#         with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
#             jsonf.write(json.dumps(data, indent=2))


# make_json("face_ulta_data.csv", "face_ulta_data.json")
# make_json("eyes_ulta_data.csv", "eyes_ulta_data.json")
make_json(["../data/tagged_products.csv"], "4_27_data.json")
