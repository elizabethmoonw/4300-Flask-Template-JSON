import csv
import json


# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json(csvFilePath, jsonFilePath):

    # create a dictionary
    data = {}
    data["products"] = []

    # Open a csv reader called DictReader
    with open(csvFilePath, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:

            # Assuming a column named 'No' to
            # be the primary key
            # key = rows[""]
            new_rows = rows
            new_rows["product"] = rows["brand"] + " " + rows["product"]

            # price
            if rows["price"].startswith("Sale"):
                new_rows["price"] = float(
                    rows["price"][
                        rows["price"].rindex("$") + 1 : rows["price"].rindex(".") + 3
                    ]
                )
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
            new_rows["shades"] = rows["shades"][2:-2].split("], [")

            # reviews
            new_rows["reviews"] = rows["reviews"][2:].split('", "')

            data["products"].append(new_rows)
            # data[key] = rows

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(data, indent=2))


make_json("face_ulta_data.csv", "face_ulta_data.json")
