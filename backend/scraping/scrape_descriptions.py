import csv
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common import exceptions


def update_file(file):
    # with open(file, "rt", encoding="utf-8") as f:
    #     reader = csv.reader(f, delimiter=",")
    df = pd.read_csv(file, encoding='latin-1')
    links = df['link']
    summaries = []
    for link in links:
        summary = scrape_link(link)
        print(summary)
        # print(detail)
        summaries.append(summary)
    df.insert(11, 'summary', summaries)
    return df


def scrape_link(link):
    summary = ''
    # details = {}
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors-spki-list")
    options.add_argument("--ignore-ssl-errors")

    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=options)
    driver.maximize_window()
    driver.get(link)
    driver.implicitly_wait(5)
    try:
        try:
            summary = driver.find_element(
                By.XPATH, '//*[@id="b46bc3ad-9907-43a6-9a95-88c160f02d7f"]/p').text
        except exceptions.StaleElementReferenceException:
            summary = driver.find_element(
                By.XPATH, '//*[@id="b46bc3ad-9907-43a6-9a95-88c160f02d7f"]/p').text
    except exceptions.NoSuchElementException:
        driver.quit()
        return ''
    driver.quit()
    return summary


def main():
    # , "face_ulta_data.csv", "lips_ulta_data.csv"]
    files = ["eyes_ulta_data.csv"]
    for file in files:
        updated = update_file(file)
        updated.to_csv(file, index=False)


if __name__ == "__main__":
    main()
