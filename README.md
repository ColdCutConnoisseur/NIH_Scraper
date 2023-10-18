# NIH Scrape
Take a filtered search query and scrape data about potential candidates.

## Current Procedure

#### Set Base Config File
Set project-wide config variables in *project_config.py* file first.

#### Getting Candidate Supplemental Info
1. Set configuration parameters in ```fetch_urls_for_candidate_supplemental_info.py```.  This includes the **filtered_url**, which is a url pointing to the filtered search query on NIH's website.  The second parameter is **CANDIDATE_CSV_PATH**, or the path to the csv file where the page urls containing the candidate emails will be written to (you can leave this to overwrite the current file in url_paths/candidate_supplemental_info.csv).  This is all handled by the main project_config.py file now.
    
2. Next, set first arg of the __build_email_dictionary__ call to match the above **CANDIDATE_CSV_PATH** in the **fetch_candidate_supplemental_info.py** file.  Also set the second argument to the output json  file that will house the dictionary containing the scraped supplemental candidate info.  Then run ```python fetch_candidate_supplemental_info.py``` to visit each of the urls pulled from step 1.

3.  Set internal parameters inside and then run ```combine_supp_dicts.py```.  This is a helper script that will combine the multiple json files containing supplemental candidate info.  Multiple files might exist because of errors when running the supplemental info scraping process.

#### Running 'Main' Scrape
4.  Run ```python run_nih_scrape_and_append_info_forked.py``` to run the main runner script which pulls data for each project in the filtered search and then appends info from the *final_supplemental_dict* file.


5. Run 'city_state_splitter.py'



Combine_all_output_files script added in event of combining output of multiple similar scrapes.  Will combine all individual scrapes and aggregate data for candidates.




## Scraping 'Similar Projects' subtable
