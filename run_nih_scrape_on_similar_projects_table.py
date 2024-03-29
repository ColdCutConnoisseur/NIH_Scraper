"""Altered script for scraping data from a 'Similar Projects' table"""

import time
import json
import sys
import csv

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from text_formatter import title_case_text
from scrape_similar_projects_table import (visit_base_url,
                                            click_similar_projects_tab,
                                            locate_similar_projects_table,
                                            scroll_to_bottom_of_window)

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


def scrape_project_data(driver, table_element):
    project_titles_list = []
    project_titles = table_element.find_elements(By.XPATH, ".." + PROJECT_TITLE_XPATH)
    print(len(project_titles)) #DEBUG

    for project in project_titles:
        print(f"Project Text: {project.text}")
        project_titles_list.append(project.text)

    # Full codes --> Appl (T), Act (next 3), and Serial Number (remainder)
    all_full_codes = table_element.find_elements(By.XPATH, "..//td[@class=' column-full_project_num']/a/span[1]")
    all_full_codes = [e.text for e in all_full_codes]
    
    appl_codes = [t[0] for t in all_full_codes]
    act_codes = [t[1:4] for t in all_full_codes]
    serial_nums = [t[4:t.index('-')] for t in all_full_codes]

    #Sub ID  -- Not all projects will have Sub IDs
    sub_ids = []
    all_sub_ids = table_element.find_elements(By.XPATH, ".." + SUB_ID_XPATH)

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
    all_pipls = table_element.find_elements(By.XPATH, ".." + PIPL_XPATH)

    for pipl in all_pipls:
        #print(pipl.text)
        investigators.append(pipl.text)

    #Org
    orgs = []
    all_orgs = table_element.find_elements(By.XPATH, ".." + ORG_XPATH)
    for org in all_orgs:
        #print(org.text)
        orgs.append(org.text)

    #Fiscal Year
    fys = []
    all_fys = table_element.find_elements(By.XPATH, ".." + FY_XPATH)
    for fy in all_fys:
        #print(fy.text)
        fys.append(fy.text)

    #Admin IC
    admin_ics = []
    all_admin_ics = table_element.find_elements(By.XPATH, ".." + ADMIN_IC_XPATH)
    for admin_ic in all_admin_ics:
        admin_ics.append(admin_ic.text)

    #Fund IC
    fund_ics = []
    all_fund_ics = table_element.find_elements(By.XPATH, ".." + FUND_IC_XPATH)
    for fund_ic in all_fund_ics:
        fund_ics.append(fund_ic.text)

    #FY Cost
    fy_costs = []
    all_fy_costs = table_element.find_elements(By.XPATH, ".." + FY_COST_XPATH)
    for fy_cost in all_fy_costs:
        fy_costs.append(fy_cost.text)

    #Piece it all together
    candidate_out_dict = {}
    act_codes_dict = {}

    debug_counter = 0

    #print(project_titles_list) # Good
    #print(appl_codes) # Good
    #print(act_codes) # Good
    #print(serial_nums) # Good
    #print(f"Years: {years}") # Bad
    #print(sub_ids) # Good
    #print(investigators) # Semi Good
    #print(orgs) # Good
    #print(fys) # Good
    #print(admin_ics) # Good
    #print(fund_ics) # Good
    #print(fy_costs) # Good

    # Year Fix
    years = ['N/A' for item in project_titles_list]

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
            'Project_code'                          : app_code + act_code + ser_num, # + yr,
            'Project_sub_id'                        : s_id,
            'Principal_investigator/project_leader' : all_recipients,
            'Organization'                          : org,
            'Fiscal_year'                           : fy,
            'Admin_ic'                              : admin_ic,
            'Funding_ic'                            : fund_ic,
            'FY_total_cost'                         : fy_cost
            }

        
        pretty_dict = json.dumps(out_dict, indent=4)

        print(pretty_dict)
        
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
    header_row = ["First Name", "Middle Initial", "Last Name", "Project Leader", "Title", "Email", "Organization", "Organization - City & State", "Department Type", "Organization Type", "# of Grants", "Total Amount of Grant(s)", "Project Type", "Project Data"]
    out_data = [header_row]

    print(candidate_out_dict)
    
    for candidate_full_name, candidate_projects in candidate_out_dict.items():

        # Fetch data from email dict
        name_stripped = candidate_full_name.strip()

        try:
            dict_data = supplemental_lookup_dict[name_stripped]

            print(dict_data)

            title = title_case_text(dict_data["title"])
            email = dict_data["email"]
            city = title_case_text(dict_data["city"])
            state = dict_data["state"]
            department_type = title_case_text(dict_data["department_type"])
            organization_type = title_case_text(dict_data["organization_type"])

        except KeyError:
            print(f"KeyError: {candidate_full_name}")
            continue
            # inp = input("Ok?")

            #title = ""
            #email = ""
            #city = ""
            #state = ""
            #department_type = ""
            #organization_type = ""

        first_name, middle_initial, last_name = parse_name(candidate_full_name)     

        projects = candidate_projects.values()
        all_orgs = [project['Organization'] for project in projects]

        all_orgs = set(all_orgs)

        all_orgs = list(all_orgs)

        all_orgs = [title_case_text(org) for org in all_orgs]

        all_orgs = '; '.join(all_orgs)

        pulled_project_types = act_codes_dict[candidate_full_name]

        project_types = ', '.join(pulled_project_types)

        project_data = json.dumps(candidate_projects, indent=4)

        org_city_state = city + ", " + state

        raw_grant_strings = [project['FY_total_cost'] for project in projects]

        grant_totals = 0

        for raw_grant_amount in raw_grant_strings:
            raw_grant_amount = raw_grant_amount.replace('$', '')
            raw_grant_amount = raw_grant_amount.replace(',', '')

            # Handle newline characters
            if '\n' in raw_grant_amount:
                print("Warning: Newline char found in raw_grant_amount!")
                raw_grant_amounts = raw_grant_amount.split('\n')
                as_floats = [float(amount) for amount in raw_grant_amounts]
                sum_floats = sum(as_floats)
                grant_totals += sum_floats

            else:
                try:
                    raw_grant_amount = float(raw_grant_amount)

                except ValueError:
                    raw_grant_amount = 0
                    
                grant_totals += raw_grant_amount

        out_record = [first_name,
                      middle_initial,
                      last_name,
                      name_stripped,
                      title,
                      email,
                      all_orgs,
                      org_city_state,
                      department_type,
                      organization_type,
                      len(pulled_project_types),
                      grant_totals,
                      project_types,
                      project_data]

        out_data.append(out_record)

    print("OUT_DATA:")
    print(out_data) # DEBUG

    with open(csv_out_path, 'w') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerows(out_data)

def main(driver, supplemental_info_dict_path, base_url, csv_out_path):
    print("Loading supplemental info dict...")
    supp_info_dict = {}

    with open(supplemental_info_dict_path, 'r') as json_in:
        supp_info_dict = json.load(json_in)

    print(supp_info_dict)

    table_xpath = "//div[@id='similarProjectsDataTableContainer']"

    visit_base_url(driver, base_url)
    click_similar_projects_tab(driver)
    similar_projects_table = locate_similar_projects_table(driver, table_xpath)
    scroll_to_bottom_of_window(driver, similar_projects_table)

    print("Scraping projects...")
    candidate_out_dict, act_codes_dict = scrape_project_data(driver, similar_projects_table)

    format_and_output_to_csv(supp_info_dict, candidate_out_dict, act_codes_dict, csv_out_path)


if __name__ == "__main__":
    import project_config as cf

    DRIVER = uc.Chrome()

    SUPP_DICT_PATH = cf.FULL_SUPP_DICT_PATH
    BASE_URL = "https://reporter.nih.gov/search/twcKpAFxMEi7nIaWoCg2iQ/project-details/10735282"
    CANDIDATE_CSV_PATH = cf.PRE_SPLIT_FINAL_FILE_NAME

    main(DRIVER, SUPP_DICT_PATH, BASE_URL, CANDIDATE_CSV_PATH)
        
    DRIVER.quit()
