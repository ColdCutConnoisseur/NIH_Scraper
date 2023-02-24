# NIH Scrape
Take a filtered search query and scrape data about potential candidates.

# Current Procedure
1. Set configuration parameters in ```fetch_urls_for_candidate_supplemental_info.py```.  This includes the **filtered_url**, which
    is a url pointing to the filtered search query on NIH's website.  The second parameter is **CANDIDATE_CSV_PATH**, 
    or the path to the csv file where the page urls containing the candidate emails will be written to.
