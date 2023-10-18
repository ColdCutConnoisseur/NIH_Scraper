"""Given a filtered projects list, find all urls that link to candidate email addresses"""

import time
import json
import sys
import csv

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from fuzzywuzzy import fuzz

#CONSTANTS
NIH_SEARCH_URL = "https://reporter.nih.gov/"
QUICK_SEARCH_INPUT_XPATH = "//input[@id='smartSearch']"
QUICK_SEARCH_BUTTON_XPATH = "//button[@id='button-addon2']"
ACTIVE_PARAM_ADDON = "?projects=Active"
RESULTS_TABLE_XPATH = "//table[@class='data-table']"

def fetch_urls_to_visit(driver, project_titles_filter_list):
    urls_to_visit = []

    def_wait = WebDriverWait(driver, 15)

    results_table = def_wait.until(ec.visibility_of_element_located((By.XPATH, RESULTS_TABLE_XPATH)))

    print("Results table found!")

    if len(project_titles_filter_list) > 0:

        project_elements = results_table.find_elements(By.XPATH, ".//tr[contains(@id, 'data-row')]/td/a")

        for project_element in project_elements:
            project_name = (project_element.text).strip().lower()

            """
            for title in project_titles_filter_list:
                match_pct = fuzz.ratio(project_name, title)

                if match_pct > 95:
                    print("Project name found in filter list!")
                    print(f"Per NIH site: {project_name}")
                    print(f"Per filter list: {title}")
            """
            if project_name in project_titles_filter_list:
                urls_to_visit.append(project_element.get_attribute('href'))

    else:
        all_links_in_table = results_table.find_elements(By.XPATH, ".//tr[contains(@id, 'data-row')]/td/a")

        print(f"DEBUG: Number of links located: {len(all_links_in_table)}")

        for found_link in all_links_in_table:
            url_address = found_link.get_attribute('href')
            urls_to_visit.append(url_address)

    urls_to_visit = list(set(urls_to_visit))
    print(f"Num urls recorded: {len(urls_to_visit)}")
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
            time.sleep(3)

def write_urls_to_csv(urls_to_visit, csv_out_path):
    formatted_urls_to_visit = [[item] for item in urls_to_visit]

    with open(csv_out_path, 'w') as csv_out:
        csv_writer = csv.writer(csv_out)
        csv_writer.writerows(formatted_urls_to_visit)

def main(driver, filtered_url, csv_out_path, project_filter_list=[]):
    """If a project_id_list is provided (not empty) it will only return urls 
       for projects with an id that exists in the project_id_list
    """
    #Visit search results
    print(f"Visiting filtered url: {filtered_url}...")
    driver.get(filtered_url)

    wait = WebDriverWait(driver, 15)
    wait.until(ec.url_to_be(filtered_url))

    print("URL matches intended!")

    print("Scrolling to bottom...")
    scroll_to_bottom(driver)

    print("Fetching all email urls...")
    if len(project_filter_list) > 0:
        project_filter_list = [p.strip().lower() for p in project_filter_list]

    urls_to_visit = fetch_urls_to_visit(driver, project_filter_list)
    print("All urls found!")

    print("Writing urls to csv...")
    write_urls_to_csv(urls_to_visit, csv_out_path)
    print("Write complete!")


if __name__ == "__main__":
    import project_config

    DRIVER = uc.Chrome()
    FILTERED_URL = project_config.NIH_QUERY_URL
    CANDIDATE_CSV_PATH = project_config.SUPPLEMENTAL_INFO_URL_PATH

    # ADD-IN
    PROJECT_TITLES_FILTER_LIST = []
    """
    
    with open("./csvs/metzger_project_titles.csv", 'r') as csv_in:
        csv_reader = csv.reader(csv_in)

        for row in csv_reader:
            PROJECT_TITLES_FILTER_LIST.append(row[0])

    print(f"{len(PROJECT_TITLES_FILTER_LIST)} project(s) to find...")
    """

    try:
        main(DRIVER, FILTERED_URL, CANDIDATE_CSV_PATH, project_filter_list=PROJECT_TITLES_FILTER_LIST)

    except:
        pass

    finally:
        DRIVER.quit()
