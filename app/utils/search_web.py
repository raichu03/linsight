import requests
import logging
import time

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Any, Optional

#--- Logging Setup ---#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/search.log'
)

#--- Configuration Management ----#
class VarSettings(BaseSettings):
    """
    Settings for Google Customs Search API.
    Uses pydantic-settings for robust configuration form environment variables or .env file.
    """
    search_key: str = Field(..., description="Key for Google Custom Search API")
    search_id: str = Field(..., description="Custom Search Engine ID (cx) for Google Search")
    
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    

#--- Constants and API Endpoint ---#
Search_API_URL = 'https://www.googleapis.com/customsearch/v1'
DEFAULT_MAX_RESULTS_PER_PAGE = 10
DEFAULT_TOTAL_RESULTS_TO_FETCH = 10
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DEALY_SECONDS = 5

#--- Core Search Functionlaity ---#
def make_custom_search(query: str,) -> List:
    """
    Search Google Custom SEarch API for the given query and retrieves links.
    
    Args:
        query: The search query string.
        
    Returns:
        A list of dictionaries, where each dictionary represents a searh results item.
    """
    
    all_results = []
    all_links = []
    start_index = 1
    
    secrets = VarSettings()
    
    logging.info(f"Starting search for query: '{query}")
    
    while start_index <= DEFAULT_TOTAL_RESULTS_TO_FETCH:
        parms = {
            'q': query,
            'key': secrets.search_key,
            'cx': secrets.search_id,
            'start': start_index,
            'num': DEFAULT_MAX_RESULTS_PER_PAGE
        }
        
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = requests.get(Search_API_URL, params=parms, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'items' in data:
                    current_page_results = data['items']
                    all_results.extend(current_page_results)
                    
                    for item in all_results:
                        all_links.append(item['link'])
                        
                    logging.info(f"Fetched {len(current_page_results)} results for start_index={start_index}")
                    
                    if len(current_page_results) < DEFAULT_MAX_RESULTS_PER_PAGE:
                        logging.info(f"Less than {DEFAULT_MAX_RESULTS_PER_PAGE} rsults returned, likely end of results.")
                        return all_links
                else:
                    logging.info(f"No 'items' found in response for start_index={start_index}.")
                    if 'error' in data:
                        logging.error(f"API Error: {data['error'].get('message', 'Unknown error')}")
                    return all_links
                
                break
            except requests.exceptions.Timeout:
                logging.warning(f"Request timed out (attempt {attempt + 1}/{DEFAULT_RETRY_ATTEMPTS}). Retrying in {DEFAULT_RETRY_DEALY_SECONDS} seconds...")
                time.sleep(DEFAULT_RETRY_DEALY_SECONDS)
            except requests.exceptions.ConnectionError as e:
                logging.error(f"Connection error (attempt {attempt + 1}/{DEFAULT_RETRY_ATTEMPTS}): {e}. Retrying in {DEFAULT_RETRY_DEALY_SECONDS} seconds...")
                time.sleep(DEFAULT_RETRY_DEALY_SECONDS)
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                logging.error(f"HTTP error {status_code} (attempt {attempt + 1}/{DEFAULT_RETRY_ATTEMPTS}): {e}")
                if status_code == 429:
                    logging.warning(f"Rate limit hit. Retrying in {DEFAULT_RETRY_DEALY_SECONDS * (attempt + 1)} seconds...")
                    time.sleep(DEFAULT_RETRY_DEALY_SECONDS * (attempt + 1))
                elif status_code == 400:
                    logging.critical(f"Bad Request error (status code 400). Check API key, CX ID, or query: {e}. Exiting.")
                    return []
                elif status_code == 403:
                    logging.critical(f"Forbidden error (status code 403). Check API key permissions or daily limits: {e}. Exiting.")
                    return []
                else:
                    time.sleep(DEFAULT_RETRY_DEALY_SECONDS)
            except requests.exceptions.RequestException as e:
                logging.error(f"An unexpected request error occurred (attempt {attempt + 1}/{DEFAULT_RETRY_ATTEMPTS}): {e}. Retrying...")
                time.sleep(DEFAULT_RETRY_DEALY_SECONDS)
            except ValueError as e:
                logging.error(f"Error parsing JSON response: {e}. Response content: {response.text}")
                break

        else:
            logging.error(f"All {DEFAULT_RETRY_ATTEMPTS} attempts failed for start_index={start_index}. Skipping this page.")
            break

        start_index += DEFAULT_MAX_RESULTS_PER_PAGE

    logging.info(f"Finished search. Total results fetched: {len(all_results)}")
    return all_links
            