"""Main runner script.  Get candidates from NIH query and append their supplemental info"""

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

PROJECT_TITLE_XPATH = "//td[@data-label='Project Title']"
APPL_CODE_XPATH = "//td[@class=' column-appl_type_code']"
ACT_CODE_XPATH = "//td[@class=' column-activity_code']"
IC_SERIAL_NUMBER_XPATH = "//td[@class=' column-ic_serial_num']"
YEAR_XPATH = "//td[@class=' column-support_yr']"
SUB_ID_XPATH = "//td[@class=' column-subproject_id']"
PIPL_XPATH = "//td[@class=' column-pi_info']"
ORG_XPATH = "//td[@class=' column-org_name']"
FY_XPATH = "//td[@class=' column-fiscal_year']"
ADMIN_IC_XPATH = "//td[@class=' column-admin_icd_long_abbr']"
FUND_IC_XPATH = "//td[@class=' column-funding']"
FY_COST_XPATH = "//td[@class='rightAlign column-funding']"


def scrape_project_data(driver):
    project_titles_list = []
    project_titles = driver.find_elements(By.XPATH, PROJECT_TITLE_XPATH)
    print(len(project_titles)) #DEBUG

    for project in project_titles:
        #print(project.text)
        project_titles_list.append(project.text)

    #Appl code ('T')
    all_appl_codes = driver.find_elements(By.XPATH, APPL_CODE_XPATH)
    
    #Structure here is:
    #    <span name>5</span> <--This is the value attribute [*We only need this]
    #    <span name>T</span> <--This is the name attribute
    
    appl_codes = []
    for code in all_appl_codes:
        all_span_elements = code.find_elements(By.XPATH, './/span')
        assert len(all_span_elements) == 2, "Len of 'span' elements not 2!"
        appl_code = all_span_elements[0].text
        #print(appl_code)
        appl_codes.append(appl_code)

    #Activity code ('ACT')
    act_codes = []
    all_act_codes = driver.find_elements(By.XPATH, ACT_CODE_XPATH)
    for code in all_act_codes:
        all_span_elements = code.find_elements(By.XPATH, './/span')
        assert len(all_span_elements) == 2, "Len of 'span' elements not 2!"
        act_code = all_span_elements[0].text
        #print(act_code)
        act_codes.append(act_code)

    #IC Serial Number
    serial_nums = []
    all_serial_numbers = driver.find_elements(By.XPATH, IC_SERIAL_NUMBER_XPATH)
    for number in all_serial_numbers:
        all_span_elements = number.find_elements(By.XPATH, './/span')
        assert len(all_span_elements) == 2, "Len of 'span' elements not 2!"
        serial_number = all_span_elements[0].text
        #print(serial_number)
        serial_nums.append(serial_number)

    #Year
    years = []
    all_years = driver.find_elements(By.XPATH, YEAR_XPATH)
    for year in all_years:
        all_span_elements = year.find_elements(By.XPATH, './/span')
        assert len(all_span_elements) == 2, "Len of 'span' elements not 2!"
        pro_year = all_span_elements[0].text
        #print(pro_year)
        years.append(pro_year)

    #Sub ID  -- Not all projects will have Sub IDs
    sub_ids = []
    all_sub_ids = driver.find_elements(By.XPATH, SUB_ID_XPATH)
    for sub_id in all_sub_ids:
        all_span_elements = sub_id.find_elements(By.XPATH, './/span')
        try:
            assert len(all_span_elements) == 2, "Len of 'span' elements not 2!"
            sub_id = all_span_elements[1].text #NOTE: this is index 1
            #print(sub_id)

        except AssertionError:
            sub_id = 'N/A'
            #print(sub_id)

        sub_ids.append(sub_id)

    investigators = []
    #Principal Investigator(s) / Project Leader(s)
    all_pipls = driver.find_elements(By.XPATH, PIPL_XPATH)
    for pipl in all_pipls:
        #print(pipl.text)
        investigators.append(pipl.text)

    #Org
    orgs = []
    all_orgs = driver.find_elements(By.XPATH, ORG_XPATH)
    for org in all_orgs:
        #print(org.text)
        orgs.append(org.text)

    #Fiscal Year
    fys = []
    all_fys = driver.find_elements(By.XPATH, FY_XPATH)
    for fy in all_fys:
        #print(fy.text)
        fys.append(fy.text)

    #Admin IC
    admin_ics = []
    all_admin_ics = driver.find_elements(By.XPATH, ADMIN_IC_XPATH)
    for admin_ic in all_admin_ics:
        admin_ics.append(admin_ic.text)

    #Fund IC
    fund_ics = []
    all_fund_ics = driver.find_elements(By.XPATH, FUND_IC_XPATH)
    for fund_ic in all_fund_ics:
        fund_ics.append(fund_ic.text)

    #FY Cost
    fy_costs = []
    all_fy_costs = driver.find_elements(By.XPATH, FY_COST_XPATH)
    for fy_cost in all_fy_costs:
        fy_costs.append(fy_cost.text)

    #Piece it all together
    candidate_out_dict = {}
    act_codes_dict = {}

    debug_counter = 0

    for project_title, app_code, act_code, ser_num, yr, s_id, p_invest, org, fy, admin_ic, fund_ic, fy_cost \
            in zip(project_titles_list, appl_codes, act_codes,
                   serial_nums, years, sub_ids, investigators,
                   orgs, fys, admin_ics, fund_ics, fy_costs):

        #print(f"DEBUG INVESTIGATORS: {p_invest}")

        print(debug_counter)

        #Sort out PI
        
        replaced = p_invest.replace("Principal Investigator(s)/ Project Leader(s)", '$')
        recipients_split = replaced.split('$')

        recipients_split = [r.replace('\n', '') for r in recipients_split]
        principal_investigator = recipients_split[0]

        #print(f"PI: {principal_investigator}")

        all_recipients = '; '.join(recipients_split)

        #print(f"ALL: {all_recipients}")

        #print("-----------------~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_________________________~~~~~~_~----")

        out_dict = {
            'Project_title'                         : project_title,
            'Project_code'                          : app_code + act_code + ser_num + yr,
            'Project_sub_id'                        : s_id,
            'Principal_investigator/project_leader' : all_recipients,
            'Organization'                          : org,
            'Fiscal_year'                           : fy,
            'Admin_ic'                              : admin_ic,
            'Funding_ic'                            : fund_ic,
            'FY_total_cost'                         : fy_cost
            }

        
        #pretty_dict = json.dumps(out_dict, indent=4)
        
        #Main Dict
        if principal_investigator in candidate_out_dict.keys():
            nested_dict = candidate_out_dict[principal_investigator]
            nested_dict_keys = list(nested_dict.keys())
            highest_project_index = max(nested_dict_keys)
            next_index = highest_project_index + 1
            #print(next_index)

            nested_dict[next_index] = out_dict

        else:
            candidate_out_dict[principal_investigator] = {1 : out_dict}

        #ACT Codes Dict
        if principal_investigator in act_codes_dict.keys():
            act_codes_dict[principal_investigator] += [act_code]

        else:
            act_codes_dict[principal_investigator] = [act_code]


        debug_counter += 1



    return [candidate_out_dict, act_codes_dict]

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

def base_name_split_and_capitalize(name, split_join_char):
    name_split = name.split(split_join_char)
    capitalized = [name_chunk.capitalize() for name_chunk in name_split]
    formatted = split_join_char.join(capitalized)
    return formatted

def capitalize_name(name):
    """Split by ' ' then capitalize then join--think names like 'Al Shah'"""
    if name == '':
        formatted = ''

    #If name present...
    else:
        formatted = base_name_split_and_capitalize(name, ' ')

        #For hyphenated names
        if '-' in formatted:
            formatted = base_name_split_and_capitalize(formatted, '-')

    return formatted

def parse_name(candidate_full_name):
    middle_initial = ''

    split_by_comma = candidate_full_name.split(',')

    split_by_comma = [item.strip() for item in split_by_comma]

    if len(split_by_comma) > 2:
        print(f"ONE-OFF: {candidate_full_name}")
        user_in = input()

    last_name = split_by_comma[0]

    remainder = split_by_comma[1]

    remainder_split = remainder.split(' ')

    first_name = remainder_split[0]

    if len(remainder_split) == 2:
        middle_initial = remainder_split[1]

    elif len(remainder_split) > 2:
        #print(f"ONE_OFF: {candidate_full_name}")
        #sys.exit(0)
        middle_initial = ' '.join(remainder_split[1:])

    else:
        pass

    first_name = capitalize_name(first_name)
    middle_initial = capitalize_name(middle_initial)
    last_name = capitalize_name(last_name)

    return [first_name, middle_initial, last_name]

def format_and_output_to_csv(supplemental_lookup_dict, candidate_out_dict, act_codes_dict, csv_out_path):
    header_row = ["First Name", "Middle Initial", "Last Name", "Project Leader", "Title", "Email", "Organization", "Organization - City & State", "# of Grants", "Total Amount of Grants", "Project Type", "Project Data"]
    out_data = [header_row]
    
    for candidate_full_name, candidate_projects in candidate_out_dict.items():

        # Fetch data from email dict
        name_stripped = candidate_full_name.strip()

        dict_data = supplemental_lookup_dict[name_stripped]

        title = dict_data["title"]
        email = dict_data["email"]
        city = dict_data["city"]
        state = dict_data["state"]
        department_type = dict_data["department_type"]
        organization_type = dict_data["organization_type"]

        first_name, middle_initial, last_name = parse_name(candidate_full_name)     

        projects = candidate_projects.values()
        all_orgs = [project['Organization'] for project in projects]

        all_orgs = set(all_orgs)

        all_orgs = list(all_orgs)

        all_orgs = '; '.join(all_orgs)

        pulled_project_types = act_codes_dict[candidate_full_name]

        project_types = ', '.join(pulled_project_types)

        project_data = json.dumps(candidate_projects, indent=4)

        org_city_state_placeholder = 'N/A'

        dep_type =

        org_type =

        raw_grant_strings = [project['FY_total_cost'] for project in projects]

        grant_totals = 0

        for raw_grant_amount in raw_grant_strings:
            raw_grant_amount = raw_grant_amount.replace('$', '')
            raw_grant_amount = raw_grant_amount.replace(',', '')
            raw_grant_amount = float(raw_grant_amount)
            grant_totals += raw_grant_amount

        out_record = [first_name, middle_initial, last_name, name_stripped, title, email, all_orgs, org_city_state_placeholder, len(pulled_project_types), grant_totals, project_types, project_data]
        out_data.append(out_record)

    with open(csv_out_path, 'w') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerows(out_data)

def main(driver, supplemental_info_dict_path, filtered_url, csv_out_path):
    print("Loading supplemental info dict...")
    supp_info_dict = {}

    with open(supplemental_info_dict_path, 'r') as json_in:
        supp_info_dict = json.load(json_in)

    driver.get("https://reporter.nih.gov/")
    time.sleep(5)

    #Visit search results
    print(f"Visiting filtered url: {filtered_url}...")
    driver.get(filtered_url)

    wait = WebDriverWait(driver, 15)
    wait.until(ec.url_to_be(filtered_url))

    print("URL matches intended!")

    print("Scrolling to bottom...")
    scroll_to_bottom(driver)

    print("Scraping projects...")
    candidate_out_dict, act_codes_dict = scrape_project_data(driver)

    format_and_output_to_csv(supp_info_dict, candidate_out_dict, act_codes_dict, csv_out_path)


if __name__ == "__main__":
    DRIVER = uc.Chrome()
    SUPP_DICT_PATH = "final_supplemental_dict.json"
    FILTERED_URL = "https://reporter.nih.gov/search/y8yzHpL31UOOU0n03twRHw/projects"
    CANDIDATE_CSV_PATH = "./csvs/test_02_24_23_compile.csv"

    try:
        main(DRIVER, SUPP_DICT_PATH, FILTERED_URL, CANDIDATE_CSV_PATH)

    except:
        pass

    finally:
        DRIVER.quit()
