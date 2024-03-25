import csv
import json
import re


def ingredients2():
    with open("cosmetic_p.csv") as csvf:
        csvReader = csv.DictReader(csvf)
        ingredients_set = set()

        for row in csvReader:
            ingred_list = row["ingredients"].split(", ")
            ingredients_set.update(ingred.lower() for ingred in ingred_list)

        ingredient_dict = {}
        ingredient_dict["ingredients"] = list(ingredients_set)

        # with open("ingredient_list.json", "w", encoding="utf-8") as jsonf:
        #     jsonf.write(json.dumps(ingredient_dict, indent=2))

        return ingredients_set


def ingredients3():
    set1 = ingredients_set().intersection(ingredients2())
    ingredient_dict = {}
    ingredient_dict["ingredients"] = sorted(list(set1))

    with open("ingredient_list.json", "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(ingredient_dict, indent=2))


def ingredients_set():
    with open("clean_dataset.json") as jsonf:
        file = json.load(jsonf)
        # with open("clean_dataset.csv") as csvf:
        # csvReader = csv.DictReader(csvf)

        ingredients = set()

        # print(file)

        for key, lst in file.items():
            # print(item)
            # for key, ingred_list in item.items():
            ingred_list = []
            for ingred in lst:
                new_ingred = re.sub(
                    "--|\[|\]|\+| -|are subject to change at the manufacturer's discretion. for the most complete and up-to-date list of|please be aware that ingredient lists may change or vary from time to time. please refer to the ingredient list on the product package you receive for the most up-to-date list of| occasionally updates formulas to make sure they are as clean and effective as possible. please refer to the ingredient list on the product package you receive for the most up to date list of",
                    "",
                    ingred,
                )
                new_ingred = re.sub(" +", " ", new_ingred)
                ingred_list.append(new_ingred.lower())
            ingredients.update(ingred_list)
            # for ingredient in ingred_list:
            #     ingredients.add(ingredient)
            # print()
            # ingredients.update(item["ingredients"])
            # print(row["\ufeffingredients"])
            # print(row)
            # ingredients.update(row["ingredients"])
            # print(ingredients)
        # ingredients = set(itertools.chain(csvReader))
        # print(ingredients)
        # return list(ingredients)
        # return ingredients
        ingredient_dict = {}
        ingredient_dict["ingredients"] = list(ingredients)

        with open("ulta_ingredients.json", "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(ingredient_dict, indent=2))


def ulta_ingredients():
    with open("../scraping/all_data.json") as jsonf:
        file = json.load(jsonf)
        ingredients = set()

        for product in file["products"]:
            prod_ingredients = product["ingredients"]
            # print(prod_ingredients)
            ingredients.update(prod_ingredients)

            ingredient_dict = {}
            ingredient_dict["ingredients"] = sorted(list(ingredients))

            with open("ulta_ingredients.json", "w", encoding="utf-8") as jsonf:
                jsonf.write(json.dumps(ingredient_dict, indent=2))


# ingredients_set()
# ingredients2()
ulta_ingredients()
