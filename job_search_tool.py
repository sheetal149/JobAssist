import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

def find_jobs(keywords: str, location: str) -> str:
    """
    Find jobs using Apify based on keywords and location.
    
    Args:
        keywords: Search keywords for the job (mapped to title).
        location: Location to search for jobs.
        
    Returns:
        A JSON string containing a list of jobs with Title, Company, and URL.
    """
    # Clean inputs
    keywords = keywords.strip('"\'')
    location = location.strip('"\'')
    
    print(f"DEBUG: Searching for keywords='{keywords}', location='{location}'")

    api_token = os.getenv("APIFY_TOKEN")
    if not api_token:
        return "Error: APIFY_TOKEN environment variable not set."

    # Initialize the ApifyClient
    client = ApifyClient(api_token)

    # --- LinkedIn Scraper ---
    print("DEBUG: Starting LinkedIn scraper...")
    linkedin_results = []
    try:
        linkedin_run_input = {
            "title": keywords,
            "location": location,
            "publishedAt": "",
            "rows": 10, # Reduced to 10 to balance with Naukri
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            },
        }
        
        # Actor ID from raw_apify_code.py: BHzefUZlZRKWxkTck
        run = client.actor("BHzefUZlZRKWxkTck").call(run_input=linkedin_run_input)

        if run:
            dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()
            for item in dataset_items:
                simplified_item = {
                    "Source": "LinkedIn",
                    "Title": item.get("title") or item.get("positionName"),
                    "Company": item.get("companyName"),
                    "URL": item.get("url") or item.get("jobUrl"),
                    "Salary": item.get("salary") or "Not specified",
                    "Description": (item.get("text") or item.get("description") or "")[:200] + "...", # Truncate for brevity
                    "Experience": item.get("experienceLevel") or "Not specified"
                }
                linkedin_results.append(simplified_item)
    except Exception as e:
        print(f"Error in LinkedIn scraper: {e}")

    # --- Naukri Scraper ---
    print("DEBUG: Starting Naukri scraper...")
    naukri_results = []
    try:
        # Construct Naukri URL: https://www.naukri.com/{keywords}-jobs-in-{location}
        # Replace spaces with hyphens for URL
        fmt_keywords = keywords.replace(" ", "-")
        fmt_location = location.replace(" ", "-")
        naukri_url = f"https://www.naukri.com/{fmt_keywords}-jobs-in-{fmt_location}"
        
        print(f"DEBUG: Naukri URL: {naukri_url}")

        naukri_run_input = {
            "searchUrls": [naukri_url],
            "maxItems": 20,
            "proxyConfiguration": { "useApifyProxy": False },
        }

        # Actor ID for Naukri: wsrn5gy5C4EDeYCcD
        run = client.actor("wsrn5gy5C4EDeYCcD").call(run_input=naukri_run_input)

        if run:
            dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()
            for item in dataset_items:
                # Naukri URL fix: check multiple keys
                url = item.get("url") or item.get("jobUrl") or item.get("canonicalUrl")
                
                # Salary handling
                salary = item.get("salary")
                if not salary:
                    sal_detail = item.get("salaryDetail", {})
                    if sal_detail:
                        min_sal = sal_detail.get("minimumSalary")
                        max_sal = sal_detail.get("maximumSalary")
                        if min_sal and max_sal:
                            salary = f"{min_sal}-{max_sal} {sal_detail.get('currency', '')}"
                
                simplified_item = {
                    "Source": "Naukri",
                    "Title": item.get("title"),
                    "Company": item.get("companyName"),
                    "URL": url,
                    "Salary": salary or "Not specified",
                    "Description": (item.get("jobDescription") or item.get("description") or "")[:200] + "...",
                    "Experience": item.get("experienceText") or item.get("experience") or "Not specified"
                }
                naukri_results.append(simplified_item)
    except Exception as e:
        print(f"Error in Naukri scraper: {e}")

    # Combine results
    results = linkedin_results + naukri_results

    if not results:
        return f"No jobs found for keywords='{keywords}' in location='{location}'. Try broader keywords."

    return json.dumps(results, indent=2)
