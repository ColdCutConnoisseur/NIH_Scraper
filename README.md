# NIH Scrape
Take a filtered NIH search query and scrape data about potential candidates.

## Current Procedure

#### Set Base Config File
Set project-wide config variables in *project_config.py* file first.

#### Getting Candidate Supplemental Info
1. Run ```fetch_urls_for_candidate_supplemental_info.py```.  This will visit the NIH site and collect url paths for all of the destination pages containing candidate emails. These paths are saved within the 'url_paths' folder.
    
2. Next, run the **fetch_candidate_supplemental_info.py** file. This is the bulk of the process--the script will iterate all candidate urls found within the 'url_paths' folder (with respect to the current scrape), and create a mapping of all candidates and their email addresses.

Improvements here now include using Assembly AI for captcha solving.

Due to the nature of this being a web scrape.  Errors can be hit due to timeouts, internet connectivity problems, etc.  ```fetch_candidate_supplemental_info.py``` has a manual process where these supplemental info json files can be incremented and continued from a set index.

3.  Set internal parameters inside and then run ```combine_supp_dicts.py```.  This is a helper script that will combine the multiple json files containing supplemental candidate info as noted in the above step--> again,multiple files might exist because of errors when running the supplemental info scraping process.

#### Running 'Main' Scrape
4.  Run ```python run_nih_scrape_and_append_info_forked.py``` to run the main runner script which pulls data for each project in the filtered search and then appends info from the *final_supplemental_dict* file.

Update: New script to run (xpath changes) is ```run_current_nih_scrape.py```.

5. Run 'city_state_splitter.py'.  This script takes 'Organization - City & State' and breaks it up into separate 'City' and 'State' columns for final output.


*Combine_all_output_files* script added in event of combining output of multiple similar scrapes.  Will combine all individual scrapes and aggregate data for candidates.



## Considerations
[ ] Auto date files in config file


## Scraping 'Similar Projects' subtable
*run_nih_scrape_on_similar_projects_table.py* added. Notes to come...
