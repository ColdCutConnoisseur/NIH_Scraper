"""Hold config variables for project"""

NIH_QUERY_URL = "https://reporter.nih.gov/search/rzso2WnHAke6InWrwEcxiw/projects"

# fetch_urls_for_candidate_supplemental_info.py
SCRAPE_TITLE = "peripheral_nerve_and_neurology"
SUPPLEMENTAL_INFO_URL_PATH = f"./url_paths/{SCRAPE_TITLE}_candidate_supplemental_info_urls.csv"

FULL_SUPP_DICT_PATH = f"./supp_info/final_{SCRAPE_TITLE}_supplemental_dict.json"

PRE_SPLIT_FINAL_FILE_NAME = f"./acmed_10_17_23_{SCRAPE_TITLE}_compile.csv"
POST_SPLIT_FINAL_FILE_NAME = f"./acmed_10_17_23_{SCRAPE_TITLE}_compile_split.csv"

CHROME_USER_PROFILE_PATH = r'--user-data-dir=/Users/nickmichael/Library/Application Support/Google/Chrome'
CHROME_PROFILE_NAME = r'--profile-directory=Profile 7'  # 7, 9, or 10