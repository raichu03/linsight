import logging
from trafilatura import fetch_url, extract
from trafilatura.downloads import add_to_compressed_dict, buffered_downloads, load_download_buffer

from .parser import extract_from_html

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/scrapy_util.log'
)

def scrape_web(urls: list):
    """
    Scrapes content from a list of URLs using trafilatura with 
    enhanced error handing.
    
    Args:
        urls: A list of URLs (string) to scrape.
    
    Returns:
        A list of dictionaries containing the scraped and parsed data for successful URLs.
        Return on empty list if input is invalid or a major error occurs during setup.
    """
    
    scraped_data = []
    
    if not urls:
        logging.warning("Input URL list is empty.")
        return scraped_data
    
    try:
        cpu_threads = 4
        url_store = add_to_compressed_dict(urls)
        
        while url_store.done is False:
            try:
                buffer_list, url_list = load_download_buffer(url_store, sleep_time=3)
                
                for url, result in buffered_downloads(buffer_list, cpu_threads):
                    
                    if result is None:
                        logging.warning(f"Failed to download content for URL: {url}")
                        continue
                    
                    try:
                        html_respone = extract(result, with_metadata=True)
                        
                        if html_respone is None:
                            logging.warning(f"Trafilatura extraction failed or returned empty for URL: {url}")
                            continue
                        
                        try:
                            formated_data = extract_from_html(html_respone)
                            
                            if formated_data is None:
                                logging.warning(f"Custom parsing failed or returned empty for URL: {url}")
                                continue
                            
                            scraped_data.append(formated_data)
                        
                        except Exception as e:
                            logging.error(f"Error during custom parsing for URL {url}: {e}", exc_info=True)
                            continue
                        
                    except Exception as e:
                        logging.error(f"Error during custom parsing for URL{url}: {e}", exc_info=True)
                        continue
                    
            except Exception as e:
                logging.error(f"Error during trafilatura buffer precessing: {e}", exc_info=True)
                continue
        
        return scraped_data
    
    except Exception as e:
        logging.critical(f"A critical error occured during the scraping process: {e}", exc_info=True)
        return scraped_data