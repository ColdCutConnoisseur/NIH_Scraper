"""Hold config variables for project"""

NIH_QUERY_URL = "https://reporter.nih.gov/search/JzzVTxwso06w8k_59qATSA/projects"

# fetch_urls_for_candidate_supplemental_info.py
SCRAPE_TITLE = "anesthesiology"
SUPPLEMENTAL_INFO_URL_PATH = f"./url_paths/{SCRAPE_TITLE}_candidate_supplemental_info_urls.csv"

FULL_SUPP_DICT_PATH = f"./supp_info/final_{SCRAPE_TITLE}_supplemental_dict.json"

PRE_SPLIT_FINAL_FILE_NAME = f"./acmed_12_07_23_{SCRAPE_TITLE}_compile.csv"
POST_SPLIT_FINAL_FILE_NAME = f"./acmed_12_07_23_{SCRAPE_TITLE}_compile_split.csv"

CHROME_USER_PROFILE_PATH = r'--user-data-dir=/Users/robertmaynard/Library/Application Support/Google/Chrome'
CHROME_PROFILE_NAME = r'--profile-directory=Profile 7'
