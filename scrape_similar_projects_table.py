
import time
import csv

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec



def create_driver():
    driver = uc.Chrome()
    return driver

def visit_base_url(driver, url_to_visit):
    driver.get(url_to_visit)
    time.sleep(8)

def click_similar_projects_tab(driver):
    # Find 'Similar Projects' tab
    wdw = WebDriverWait(driver, 15)
    sp_tab = wdw.until(ec.element_to_be_clickable((By.XPATH, "//*[contains(@href, '#similar-Projects')]")))
    print("'Similar Projects' tab found!  Clicking...")
    time.sleep(2)
    
    driver.execute_script("arguments[0].click();", sp_tab)
    time.sleep(5)

def locate_similar_projects_table(driver, table_xpath):
    wdw = WebDriverWait(driver, 15)
    sp_table = wdw.until(ec.visibility_of_element_located((By.XPATH, table_xpath)))
    return sp_table

def scroll_to_bottom_of_window(driver, table_element):
    last_page_height = None
    bottom_found = False

    while not bottom_found:
        new_page_height = driver.execute_script("return arguments[0].scrollHeight;", table_element)

        print(f"New page Height: {new_page_height}")

        if new_page_height == last_page_height:
            print("Bottom of page found!")
            bottom_found = True

        else:
            driver.execute_script(f"arguments[0].scrollTo(0, {new_page_height});", table_element)
            last_page_height = new_page_height
            time.sleep(3)

    time.sleep(4)

def fetch_urls_to_visit(driver, table_to_scrape):
    urls_to_visit = []

    def_wait = WebDriverWait(driver, 15)

    all_links_in_table = table_to_scrape.find_elements(By.XPATH, ".//tr[contains(@id, 'data-row')]/td/a")

    print(f"DEBUG: Number of links located: {len(all_links_in_table)}")

    for found_link in all_links_in_table:
        url_address = found_link.get_attribute('href')
        urls_to_visit.append(url_address)

    urls_to_visit = list(set(urls_to_visit))
    print(f"Num urls recorded: {len(urls_to_visit)}")
    return urls_to_visit

def write_urls_to_csv(urls_to_visit, csv_out_path):
    formatted_urls_to_visit = [[item] for item in urls_to_visit]

    print("Writing urls to csv...")

    with open(csv_out_path, 'w') as csv_out:
        csv_writer = csv.writer(csv_out)
        csv_writer.writerows(formatted_urls_to_visit)

    print("Write complete!")

if __name__ == "__main__":
    import project_config as pc
    LANDING_URL = "https://reporter.nih.gov/search/twcKpAFxMEi7nIaWoCg2iQ/project-details/10735282" ##similar-Projects"
    SIMILAR_PROJECTS_TABLE_XPATH = "//div[@id='similarProjectsDataTableContainer']"

    try:
        driver = create_driver()
        visit_base_url(driver, LANDING_URL)
        click_similar_projects_tab(driver)
        similar_projects_table = locate_similar_projects_table(driver, SIMILAR_PROJECTS_TABLE_XPATH)
        scroll_to_bottom_of_window(driver, similar_projects_table)
        urls_list = fetch_urls_to_visit(driver, similar_projects_table)
        
        write_urls_to_csv(urls_list, pc.SUPPLEMENTAL_INFO_URL_PATH)
        
    except:
        pass

    finally:
        driver.quit()

