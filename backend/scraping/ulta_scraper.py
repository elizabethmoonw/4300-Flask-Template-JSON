from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import cv2
import urllib.request as ur
import numpy as np
from urllib.error import HTTPError


def get_links(categories):
    product_links = {}
    for k in categories:
        for c in categories[k]:
            product_links[c] = {}
            options = webdriver.ChromeOptions()
            # options.headless = True
            options.add_argument("--ignore-certificate-errors-spki-list")
            options.add_argument("--ignore-ssl-errors")
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.maximize_window()
            driver.get("https://www.ulta.com/shop/makeup/" + k + "/" + c)

            driver.implicitly_wait(3)
            for n in range(10):
                try:
                    try:
                        driver.find_element(
                            By.XPATH,
                            "//*[@id='product-listing-wrapper']/div[2]/div/div/div[3]/div[2]/div/button",
                        ).click()
                    except exceptions.StaleElementReferenceException:
                        driver.find_element(
                            By.XPATH,
                            "//*[@id='product-listing-wrapper']/div[2]/div/div/div[3]/div[2]/div/button",
                        ).click()
                    driver.implicitly_wait(1)
                except exceptions.NoSuchElementException:
                    break

            driver.implicitly_wait(5)
            links = driver.find_elements(By.TAG_NAME, "a")
            for i in range(len(links)):
                try:
                    product = links[i].get_attribute("href")
                    if (
                        product.startswith("https://www.ulta.com/p/")
                        and product not in product_links.values()
                    ):
                        product_name = (
                            product.split("/")[-1]
                            .replace("-pimprod", "-xls")
                            .split("-xls")[0]
                        )
                        product_links[c][product_name] = product
                except exceptions.StaleElementReferenceException:
                    new_links = driver.find_elements(By.TAG_NAME, "a")
                    product = new_links[i].get_attribute("href")
                    if (
                        product.startswith("https://www.ulta.com/p/")
                        and product not in product_links.values()
                    ):
                        product_name = (
                            product.split("/")[-1]
                            .replace("-pimprod", "-xls")
                            .split("-xls")[0]
                        )
                        product_links[c][product_name] = product
                    continue
            driver.quit()
    return product_links


# get product brand


def get_brand(driver):
    try:
        brand = driver.find_element(
            By.XPATH, '//*[@id="92384e5c-2234-4e8f-bef7-e80391889cfc"]/h1/span[1]/a'
        ).text
    except exceptions.StaleElementReferenceException:
        brand = driver.find_element(
            By.XPATH, '//*[@id="92384e5c-2234-4e8f-bef7-e80391889cfc"]/h1/span[1]/a'
        ).text
    return brand


# get product name
def get_name(driver):
    try:
        name = driver.find_element(
            By.CLASS_NAME, "Text-ds.Text-ds--title-5.Text-ds--left"
        ).text
    except exceptions.StaleElementReferenceException:
        name = driver.find_element(
            By.CLASS_NAME, "Text-ds.Text-ds--title-5.Text-ds--left"
        ).text
    return name


# get product price


def get_price(driver):
    try:
        price = driver.find_element(By.CLASS_NAME, "ProductPricing").text
    except exceptions.StaleElementReferenceException:
        price = driver.find_element(By.CLASS_NAME, "ProductPricing").text
    return price


# get product image


def get_img(driver):
    try:
        img = driver.find_element(
            By.XPATH,
            '//*[@id="d6d8bd59-1e47-41ad-bf7c-92d590e99862"]/div/div[1]/div[2]/div/picture/img',
        )
        img_link = img.get_attribute("src")
    except exceptions.StaleElementReferenceException:
        img = driver.find_element(
            By.XPATH,
            '//*[@id="d6d8bd59-1e47-41ad-bf7c-92d590e99862"]/div/div[1]/div[2]/div/picture/img',
        )
        img_link = img.get_attribute("src")
    return img_link


# get product shades


def get_rgb(link):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.11 (KHTML, like Gecko) "
        "Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
    }

    req = ur.Request(url=link, headers=header)
    try:
        page = ur.urlopen(req)
        arr = np.asarray(bytearray(page.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)  # 'Load it as it is'
        if type(img[40, 40] == int):
            b = g = r = img[40, 40]
        else:
            b, g, r = (img[40, 40])[:3]
        return (r, g, b)
    except HTTPError:
        return


def get_shades(driver):
    try:
        popup = driver.find_element(By.XPATH, '//*[@id="toast"]/p').click()
        driver.implicitly_wait(2)
        expand_shade = driver.find_element(
            By.CLASS_NAME, "Button-ds.Link_Huge.Button-ds--link"
        )
        if "+" in expand_shade.text:
            driver.execute_script("arguments[0].click();", expand_shade)
            print("clicked more")
    except exceptions.NoSuchElementException:
        pass
    shades = []
    try:
        shade_elems = driver.find_elements(
            By.XPATH, '//*[@id="40b1ef54-01a7-4c3e-bc9c-8b8c0d3d1840"]/div[2]/div/ul/li'
        )
        for i in range(len(shade_elems) - 1):
            try:
                shade_elem = shade_elems[i].find_element(
                    By.XPATH, ".//span/button/span/img"
                )
                shade_name = shade_elem.get_attribute("alt")
                shade_link = shade_elem.get_attribute("src")
                shade_rgb = get_rgb(shade_link)
                shades.append([shade_name, shade_link, shade_rgb])
            except exceptions.StaleElementReferenceException:
                shade_elem = shade_elems[i].find_element(
                    By.XPATH, ".//span/button/span/img"
                )
                shade_name = shade_elem.get_attribute("alt")
                shade_rgb = get_rgb(shade_link)
                shades.append([shade_name, shade_link, shade_rgb])
                continue
    except exceptions.NoSuchElementException:
        pass
    return shades


# get ingredients
def get_ingreds(driver):
    try:
        try:
            ingreds = driver.find_element(
                By.XPATH,
                '//*[@id="bb5f7945-7101-402b-b8b3-1ad025315d50"]/div/div/details[3]/div/div/p[1]',
            ).get_attribute("textContent")
        except exceptions.StaleElementReferenceException:
            ingreds = driver.find_element(
                By.XPATH,
                '//*[@id="bb5f7945-7101-402b-b8b3-1ad025315d50"]/div/div/details[3]/div/div/p[1]',
            ).get_attribute("textContent")
    except exceptions.NoSuchElementException:
        return
    return ingreds


# get avg rating


def get_rating(driver):
    try:
        avg_rating = driver.find_element(
            By.XPATH,
            '//*[@id="pr-review-snapshot"]/header/section/div/div[1]/div/div[1]/div/div[2]',
        ).text
    except exceptions.StaleElementReferenceException:
        avg_rating = driver.find_element(
            By.XPATH,
            '//*[@id="pr-review-snapshot"]/header/section/div/div[1]/div/div[1]/div/div[2]',
        ).text
    return avg_rating


# get reviews


def get_reviews(driver):
    sort_by = Select(driver.find_element(By.XPATH, '//*[@id="pr-rd-sort-by"]'))
    sort_by.select_by_value("mosthelpful")
    driver.implicitly_wait(2)

    reviews = []

    for i in range(4):
        # try:
        try:
            for j in range(5):
                print("retrieving review", i * 5 + j)
                try:
                    review = driver.find_element(
                        By.XPATH,
                        '//*[@id="pr-review-display"]/div['
                        + str(j + 1)
                        + "]/section[1]/p",
                    ).text
                    reviews.append(review)
                except exceptions.StaleElementReferenceException:
                    review = driver.find_element(
                        By.XPATH,
                        '//*[@id="pr-review-display"]/div['
                        + str(j + 1)
                        + "]/section[1]/p",
                    ).text
                    reviews.append(review)
        except exceptions.NoSuchElementException:
            break
        try:
            is_next = driver.find_element(
                By.XPATH, '//*[@id="pr-review-display"]/footer/div/div/a[2]'
            )

        except exceptions.NoSuchElementException:
            is_next = driver.find_element(
                By.XPATH, '//*[@id="pr-review-display"]/footer/div/div/a'
            )

        if is_next.text != "Next »":
            print("end of reviews")
            return reviews

        is_next.click()
        driver.implicitly_wait(3)

    return reviews


def add_to_csv(details):
    with open("face_ulta_data.csv", "a", newline="", encoding="utf-8") as f:
        write = csv.writer(f)
        write.writerow(details)


def scrape_product(link_name, link, category):
    with open("face_ulta_data.csv", "rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if link_name == row[2]:
                return
    print(link)
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors-spki-list")
    options.add_argument("--ignore-ssl-errors")

    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=options)
    driver.maximize_window()
    driver.get(link)

    driver.implicitly_wait(5)
    try:
        pop = driver.find_element(
            By.XPATH, '//*[@id="onetrust-close-btn-container"]/button'
        ).click()
    except exceptions.NoSuchElementException:
        pass

    name = get_name(driver)
    brand = get_brand(driver)
    price = get_price(driver)
    img = get_img(driver)
    shades = get_shades(driver)
    ingreds = get_ingreds(driver)
    driver.implicitly_wait(2)

    try:
        elem = driver.find_element(
            By.XPATH, '//*[@id="92384e5c-2234-4e8f-bef7-e80391889cfc"]/div/a[1]/span'
        ).click()
        driver.implicitly_wait(5)

        rating = get_rating(driver)
        reviews = get_reviews(driver)
    except exceptions.NoSuchElementException:
        rating = -1
        reviews = []
    driver.quit()

    details = [
        name,
        category,
        link_name,
        link,
        brand,
        price,
        img,
        shades,
        ingreds,
        rating,
        reviews,
    ]
    add_to_csv(details)


def main():
    # already scraped: 'foundation', 'face-powder', 'concealer'
    categories = {"face": ["face-primer"]}
    #   'bb-cc-creams', 'blush', 'bronzer', 'contouring', 'highlighter']}

    # after installing all libraries, run "python3 ulta_scraper.py"
    # remaining products- must be in dictionary form, and change lines 244 and 250 to
    # the right csv file (lips_ulta_data.csv or eyes_ulta_data.csv)
    # i've been going one product type at a time to make it easier to restart (only face-primer, for example),
    # there are sometimes still problems but just rerun

    #   'lips': ['lipstick', 'lip-gloss', 'lip-oil', 'lip-liner', 'lip-stain', 'lip-balms-treatments'],
    #   'eyes': ['eyeshadow-palettes', 'mascara', 'eyeliner', 'eyebrows', 'eyeshadow']}
    product_links = get_links(categories)
    print(product_links)
    for c in product_links:
        for p in product_links[c]:
            try:
                scrape_product(p, product_links[c][p], c)
            except exceptions.StaleElementReferenceException:
                scrape_product(p, product_links[c][p], c)


if __name__ == "__main__":
    main()
