"""Visit each email url and scrape email addresses / other supplemental info for candidate"""

import time
import json
import sys
import csv

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def return_name_title_email(driver, url):
    # Find 'detailed-info' box
    short_wait = WebDriverWait(driver, 2)
    med_wait = WebDriverWait(driver, 15)

    driver.get(url)
    page_loaded = med_wait.until(ec.url_to_be(url))
    print("Page loaded!")

    # Find 'Details' tab
    details_tab = med_wait.until(ec.element_to_be_clickable((By.XPATH, "//*[contains(@href, '#details')]")))
    print("Details tab found!  Clicking...")
    time.sleep(2)
    
    driver.execute_script("arguments[0].click();", details_tab)

    d_info_xpath = "//div[@class='row col-data']"
    detailed_info = med_wait.until(ec.visibility_of_element_located((By.XPATH, d_info_xpath)))

    print("DEBUG: 'detailed info' box found!")

    name_attrib = (detailed_info.find_element(By.XPATH, ".//div[@class='data-info']/a").text).strip()
    title_attrib = (detailed_info.find_elements(By.XPATH, ".//*[@class='data-info']")[1].text).strip()

    show_email_button = driver.find_element(By.XPATH, "//button[contains(text(), 'View Email')]")
    print("DEBUG: 'view email' button found!")

    #show_email_button.click()
    driver.execute_script("arguments[0].click();", show_email_button)

    print("Sleeping for 7 seconds...")
    time.sleep(7)
    print("Sleep exited!")

    try:
        email_attrib_parent = driver.find_elements(By.XPATH, ".//*[@class='data-info']")[2]
        print("'Email' attrib parent found!  Looking for email text...")
        
        #email_attrib = (email_attrib_parent.find_element(By.XPATH, ".//a").text).strip()

        email_attrib = (email_attrib_parent.find_element(By.TAG_NAME, "a").text).strip()

    except (TimeoutException, NoSuchElementException):
        # captcha_check = driver.find_element(By.XPATH, "//div[@class='rc-imageselect-payload']")

        print("Assuming ReCaptcha required...  Solve manually then continue...")
        user_in = input()

        email_attrib_parent = driver.find_elements(By.XPATH, ".//*[@class='data-info']")[2]
        email_attrib = (email_attrib_parent.find_element(By.XPATH, ".//a").text).strip()

    print(f"NAME ATTRIB: {name_attrib}")
    print(f"TITLE ATTRIB: {title_attrib}")
    print(f"EMAIL ATTRIB: {email_attrib}")

    return [name_attrib, title_attrib, email_attrib]


def build_email_dictionary(url_csv_path, json_dump_file, continue_index=None):
    email_dict = {}
    urls_to_visit = []

    with open(url_csv_path, 'r') as csv_in:
        csv_reader = csv.reader(csv_in)
        for row in csv_reader:
            urls_to_visit.append(row[0])

    driver = uc.Chrome()

    driver.get("https://reporter.nih.gov")

    time.sleep(5)

    # Main loop

    if not continue_index:
        continue_index = 0

    try:
        for ct, url in enumerate(urls_to_visit):

            if ct < continue_index:
                continue

            print(f"Current Url Index: {ct}")

            name_attrib, title_attrib, email_attrib = return_name_title_email(driver, url)

            if name_attrib not in list(email_dict.keys()):
                email_dict[name_attrib] = {
                                        'title' : title_attrib,
                                        'email' : email_attrib
                }

    except:
        pass

    finally:
        print("Writing json...")
        with open(json_dump_file, 'w') as json_out:
            json.dump(email_dict, json_out)

        print("Write complete!")

        driver.close()

if __name__ == "__main__":
    build_email_dictionary("./url_paths/email_urls1.csv", "emails6.json", continue_index=1101)





