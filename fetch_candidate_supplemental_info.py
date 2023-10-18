"""Visit each email url and scrape email addresses / other supplemental info for candidate"""

import time
import json
import sys
import csv

import undetected_chromedriver as uc
#from zyte_smartproxy_selenium import webdriver # proxy driver
#import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from project_config import CHROME_USER_PROFILE_PATH, CHROME_PROFILE_NAME

class ReLoopError(Exception):
    pass

class PageLoadError(Exception):
    pass

class CaptchaError(Exception):
    pass


# From https://stackoverflow.com/questions/50456783/python-selenium-clear-the-cache-and-cookies-in-my-chrome-webdriver
# Author Zack Plauche'
def delete_cache(driver):
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    time.sleep(4)
    perform_actions(driver, Keys.ENTER)  # *This should default to the correct button now
    driver.close()  # Close that window
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

def perform_actions(driver, keys):
    actions = ActionChains(driver)
    actions.send_keys(keys)
    time.sleep(2)
    print('Performing Actions!')
    actions.perform()

# End StackOverflow code----------------------------------------------------------------

def return_supplemental_info(driver, url, on_refresh=False):    # project_id_filter_list=[]):
    # Find 'detailed-info' box
    short_wait = WebDriverWait(driver, 2)
    med_wait = WebDriverWait(driver, 15)

    driver.delete_all_cookies()

    if not on_refresh:
        driver.get(url)
        time.sleep(3)
        driver.refresh()
        time.sleep(3)
        page_loaded = med_wait.until(ec.url_to_be(url))

    else:
        driver.refresh()
    print("Page loaded!")
    
    """
    # Find 'Project Number'
    project_number = driver.find_element(By.XPATH, "//div[@id='project-basics']/div[2]/div[1]/div/span[2]").text

    print(f"Current Project Number: {project_number}")

    record_info = True

    if len(project_id_filter_list) > 0:

        record_info = False

        for project_id in project_id_filter_list:
            if project_id in project_number:
                record_info = True
                break

    """

    # Find 'Details' tab
    details_tab = med_wait.until(ec.element_to_be_clickable((By.XPATH, "//*[contains(@href, '#details')]")))
    print("Details tab found!  Clicking...")
    time.sleep(2)
    
    driver.execute_script("arguments[0].click();", details_tab)

    d_info_xpath = "//div[@class='row col-data']"

    try:
        detailed_info = med_wait.until(ec.visibility_of_element_located((By.XPATH, d_info_xpath)))

    except TimeoutException:
        print("Page Load Error--Can't find 'detailed info' box")
        raise PageLoadError

    print("DEBUG: 'detailed info' box found!")
    
    city_xpath = "//div[@class='project-description']/div/div[2]/div/div[4]"
    state_xpath = "//div[@class='project-description']/div/div[4]/div/div[2]"
    department_type_xpath = "//div[@class='project-description']/div/div[3]/div/div[2]"
    organization_type_xpath = "//div[@class='project-description']/div/div[3]/div/div[4]/div"
    
    name_attrib = (detailed_info.find_element(By.XPATH, ".//div[@class='data-info']/a").text).strip()
    title_attrib = (detailed_info.find_elements(By.XPATH, ".//*[@class='data-info']")[1].text).strip()
    city_attrib = (driver.find_element(By.XPATH, city_xpath).text).strip()
    state_attrib = (driver.find_element(By.XPATH, state_xpath).text).strip()
    department_type_attrib = (driver.find_element(By.XPATH, department_type_xpath).text).strip()

    try:
        organization_type_attrib = (driver.find_element(By.XPATH, organization_type_xpath).text).strip()

    except NoSuchElementException:
        print("No Org Type Found!")
        organization_type_attrib = ""

    email_button_exists = False

    try:
        show_email_button = med_wait.until(ec.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'View Email')]")))
        #show_email_button = driver.find_element(By.XPATH, "//button[contains(text(), 'View Email')]")
        print("DEBUG: 'view email' button found!")
        email_button_exists = True

    except NoSuchElementException:
        print("No Email listed")

    if email_button_exists:

        driver.execute_script("arguments[0].click();", show_email_button)

        sleep_time = 5
        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)
        print("Sleep exited!")

        try:
            email_attrib_parent = driver.find_elements(By.XPATH, ".//*[@class='data-info']")[2]
            print("'Email' attrib parent found!  Looking for email text...")

            email_attrib = (email_attrib_parent.find_element(By.TAG_NAME, "a").text).strip()

        except (TimeoutException, NoSuchElementException):
            print("Assuming ReCaptcha required...  Solve manually then continue...")

            # delete_cache(driver)
            
            user_in = input()

            email_attrib_parent = driver.find_elements(By.XPATH, ".//*[@class='data-info']")[2]
            email_attrib = (email_attrib_parent.find_element(By.XPATH, ".//a").text).strip()
            
            #time.sleep(60)
            #raise ReLoopError

    else:
        email_attrib = ''

    print(f"NAME ATTRIB: {name_attrib}")
    print(f"TITLE ATTRIB: {title_attrib}")
    print(f"EMAIL ATTRIB: {email_attrib}")
    print(f"CITY ATTRIB: {city_attrib}")
    print(f"STATE ATTRIB: {state_attrib}")
    print(f"D TYPE ATTRIB: {department_type_attrib}")
    print(f"ORG TYPE ATTRIB: {organization_type_attrib}")

    return [name_attrib, title_attrib, email_attrib, city_attrib, state_attrib, department_type_attrib, organization_type_attrib]

def build_email_dictionary(url_csv_path, json_dump_file, continue_index=None):
    supp_dict = {}
    urls_to_visit = []

    with open(url_csv_path, 'r') as csv_in:
        csv_reader = csv.reader(csv_in)
        for row in csv_reader:
            urls_to_visit.append(row[0])

    c_options = uc.ChromeOptions()
    c_options.add_argument(CHROME_USER_PROFILE_PATH)
    c_options.add_argument(CHROME_PROFILE_NAME)
    #c_options.add_argument("--ignore-certificate-errors")
    
    #proxy_options = {
    #    'proxy' : {
    #        "http": "http://ad0955fbef474e2b821512582d777ef9:@proxy.crawlera.com:8011/",
    #       "https": "http://ad0955fbef474e2b821512582d777ef9:@proxy.crawlera.com:8011/",
    #    }
    #}

    driver = uc.Chrome(options=c_options)

    driver.get("https://reporter.nih.gov")

    time.sleep(5)

    #user_in = input("Login to your NIH account then continue")

    # Main loop

    if not continue_index:
        continue_index = 0

    try:
        for ct, url in enumerate(urls_to_visit):

            if ct < continue_index:
                continue

            print(f"Current Url Index: {ct}")

            try:
                name_attrib, title_attrib, email_attrib, city_attrib, state_attrib, department_type_attrib, organization_type_attrib = \
                        return_supplemental_info(driver, url)
                
            except PageLoadError:
                data_returned = False

                while not data_returned:
                    try:
                        name_attrib, title_attrib, email_attrib, city_attrib, state_attrib, department_type_attrib, organization_type_attrib = \
                                return_supplemental_info(driver, url, on_refresh=True)
                        
                        data_returned = True

                    except PageLoadError:
                        time.sleep(10)
                        

            if name_attrib not in list(supp_dict.keys()):
                supp_dict[name_attrib] = {
                                        'title' : title_attrib,
                                        'email' : email_attrib,
                                        'city'  : city_attrib,
                                        'state' : state_attrib,
                                        'department_type'   : department_type_attrib,
                                        'organization_type' : organization_type_attrib
                }

            #time.sleep(50)

            

    except Exception as e:
        print(e)

    finally:
        print("Writing json...")
        with open(json_dump_file, 'w') as json_out:
            json.dump(supp_dict, json_out)

        print("Write complete!")

        driver.close()

if __name__ == "__main__":
    import project_config

    URL_CSV_PATH = project_config.SUPPLEMENTAL_INFO_URL_PATH
    CURRENT_OUTPUT_PATH = f"./supp_info/{project_config.SCRAPE_TITLE}_candidate_supplemental_info1.json"

    build_email_dictionary(URL_CSV_PATH, CURRENT_OUTPUT_PATH) #, continue_index=73)





