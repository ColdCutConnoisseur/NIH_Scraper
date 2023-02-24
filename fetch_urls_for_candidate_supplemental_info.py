"""Given a filtered projects list, find all urls that link to candidate email addresses"""

import time
import json
import sys
import csv

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


#CONSTANTS
NIH_SEARCH_URL = "https://reporter.nih.gov/"
QUICK_SEARCH_INPUT_XPATH = "//input[@id='smartSearch']"
QUICK_SEARCH_BUTTON_XPATH = "//button[@id='button-addon2']"
ACTIVE_PARAM_ADDON = "?projects=Active"
RESULTS_TABLE_XPATH = "//table[@class='data-table']"

def fetch_urls_to_visit(driver):
    urls_to_visit = []

    def_wait = WebDriverWait(driver, 15)

    results_table = def_wait.until(ec.visibility_of_element_located((By.XPATH, RESULTS_TABLE_XPATH)))

    print("Results table found!")

    all_links_in_table = results_table.find_elements(By.XPATH, ".//tr[contains(@id, 'data-row')]/td/a")

    print(f"DEBUG: Number of links located: {len(all_links_in_table)}")

    for found_link in all_links_in_table:
        url_address = found_link.get_attribute('href')
        urls_to_visit.append(url_address)

    return urls_to_visit

def scroll_to_bottom(driver):
    last_page_height = None
    bottom_found = False

    while not bottom_found:
        new_page_height = driver.execute_script("return document.body.scrollHeight;")

        print(f"New page Height: {new_page_height}")

        if new_page_height == last_page_height:
            print("Bottom of page found!")
            bottom_found = True

        else:
            driver.execute_script(f"window.scrollTo(0, {new_page_height});")
            last_page_height = new_page_height
            time.sleep(1)

def write_urls_to_csv(urls_to_visit, csv_out_path):
    formatted_urls_to_visit = [[item] for item in urls_to_visit]

    with open(csv_out_path, 'w') as csv_out:
        csv_writer = csv.writer(csv_out)
        csv_writer.writerows(formatted_urls_to_visit)

def main(driver, filtered_url, csv_out_path):
    #Visit search results
    print(f"Visiting filtered url: {filtered_url}...")
    driver.get(filtered_url)

    wait = WebDriverWait(driver, 15)
    wait.until(ec.url_to_be(filtered_url))

    print("URL matches intended!")

    print("Scrolling to bottom...")
    scroll_to_bottom(driver)

    print("Fetching all email urls...")
    urls_to_visit = fetch_urls_to_visit(driver)
    print("All urls found!")

    print("Writing urls to csv...")
    write_urls_to_csv(urls_to_visit, csv_out_path)
    print("Write complete!")


if __name__ == "__main__":
    DRIVER = uc.Chrome()
    FILTERED_URL = "https://reporter.nih.gov/search/y8yzHpL31UOOU0n03twRHw/projects"
    CANDIDATE_CSV_PATH = "./url_paths/candidate_supplemental_info.csv"

    try:
        main(DRIVER, FILTERED_URL, CANDIDATE_CSV_PATH)

    except:
        pass

    finally:
        DRIVER.quit()
