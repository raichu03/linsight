import re
import logging
from typing import Optional, Dict, Any

from scrapy.metadata import extract_metadata
from scrapy.textdata import extract_text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='../logs/parser.log'
)

def extract_from_html(response: str):
    """
    Extract metadata and texts from an HTML string.
    
    Assumes metadata is in a block delimited by '---' and '---'
    
    Args:
        respinse: The input HTML string, or None.
        
    Returns:
        A dictionary containing:
        - 'metadata': A dictionary of metadata key-value pairs, or None if
                        the metadata block was not found or extraction failed.
        - 'texts': The main text content with the metadata block removed,
                    or None if the input was Noneempty or text extraction failed.
                    Returns an empty string if the text block remains empty
                    after metadata removal.
    
    Raises:
        TypeError: If the input 'response' is not a string or None.
    """
    
    web_data: Dict[str, Any] = {
        'metadata': None,
        'texts': None
    }
    
    if response is None:
        logging.warning("Input response is None.")
        return web_data
    
    if not isinstance(response, str):
        logging.error(f"Invalid input type for response: {type(response)}. Expected str or None.")
        raise TypeError("Input 'response' must be a string or None.")
    
    metadata_block_pattern = re.compile(
        r"---\s*\n(.*?)\n\s*---\s*\n?",
        re.DOTALL | re.IGNORECASE
    )
    
    ### Extracting the metadata form the web page ###
    metadata_block_match = metadata_block_pattern.search(response)
    
    if metadata_block_match:
        try:
            web_data['metadata'] = extract_metadata(metadata_block=metadata_block_match)
            if web_data['metadata'] is None:
                logging.warning("Metadata extraction failed but was caught by extract_metadata.")
        
        except Exception as e:
            logging.error(f"Unexpected error during metadata extraction: {e}", exc_info=True)
            
            web_data['metadata'] = None
    else:
        logging.info("No metadata block found in the response.")
    
    ### Extracting the articles form the web page ###
    try:
        web_data['texts'] = extract_text(text_block=response)
        if web_data['texts'] is None and response.strip():
            logging.warning("The extraction returned None for a non-empty response.")
    
    except Exception as e:
        logging.error(f"Unexpected error during text extraction: {e}", exc_info=True)
        web_data['texts'] = None
    
    logging.info("Finished information extraction.")
    return web_data