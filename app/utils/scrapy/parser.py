from bs4 import BeautifulSoup
import re

def extract_metadata(metadata_block: str):
    """
    Extracts the metadata data and returns it, returns None if no metadata found
    """
    if metadata_block:
        metadata_text = metadata_block.group(1)
        matches = re.findall(r"(\w+):\s*(.+)", metadata_text)
        
        metadata = {key: value for key, value in matches}
        return metadata
    else:
        return None

def extract_text(text_block: str):
    """
    Extracts the texts data and returns it, returns None if empty string
    """
    if text_block:
        cleaned_text = re.sub(r"---\n(.*?)\n---\n?", "", text_block, flags=re.DOTALL)
        return cleaned_text
    else:
        return None

def extract_from_html(response: str):
    """
    Extracts the valuable informations from the string and
    stores them in the structured manner.
    
    Args:
        accepts 
    
    Returns:
        returns the dictionary containing main article and the
        metadata regarding the the each article
    """
    try:
        ### Extracting metadata from the web page ###
        metadata_block = re.search(r"---\n(.*?)\n---", response, re.DOTALL)
        content_metadata = extract_metadata(metadata_block=metadata_block)
        
        ### Extracting the articles from the web page ###
        content_text = extract_text(text_block=response)
        web_data = {
            'metadata': content_metadata,
            'texts': content_text
        }
        return web_data
        
    except:
        content_metadata = None
        content_text = None
        
        web_data = {
            'metadata': content_metadata,
            'texts': content_text
        }
        return web_data