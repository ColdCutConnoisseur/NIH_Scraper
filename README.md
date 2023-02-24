# NIH Scrape
Take a filtered search query and scrape data about potential candidates.

## Current Procedure

#### Getting Candidate Supplemental Info
1. Set configuration parameters in ```fetch_urls_for_candidate_supplemental_info.py```.  This includes the **filtered_url**, which
    is a url pointing to the filtered search query on NIH's website.  The second parameter is **CANDIDATE_CSV_PATH**, 
    or the path to the csv file where the page urls containing the candidate emails will be written to.
2. Next, run ```fetch_candidate_supplemental_info.py``` script to visit each of the urls pulled from above.










# TODO:
[] text_formatter.py
[] title_case_columns.py
[] add_grant_stats.py
