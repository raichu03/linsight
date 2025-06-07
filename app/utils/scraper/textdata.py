import re
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/textdata.log'
)

def extract_text(text_block: Optional[str]) -> Optional[str]:
    """
    Extract the main text content from a string, removing the metadata block.
    
    The metadata blcok is assumed to be delomited by '---' and '---' markers,
    each on its own line. The function handles variations in the number of
    hypehns and optional trailing newlines.
    
    Args:
        text_block: The input string potentially containing a metadata block.
                    Can be None.
    
    Returns:
        The strig with the metadata block removed, or None if the input is None
        or an empty string. Returns an empty string if the input string contains
        only the metadata block.
        
    Raises:
        TypeError: If text_block is not None and not a string.
    """
    
    if text_block is None:
        logging.info("No text block provided.")
        return None
    
    if not isinstance(text_block, str):
        logging.error(f"Invalid input type: {type(text_block)}. Expected str or None.")
        raise TypeError("Input 'text_block' must be a string or None." )
    
    if not text_block.strip():
        logging.info("Text block is empty or contains only whitespace.")
        return None
    
    metadata_start_marker = r"---"
    metadata_end_marker = r"---"
    
    pattern = re.compile(
        rf"{metadata_start_marker}\s*\n(.*?)\n\s*{metadata_end_marker}\s*\n?",
        re.DOTALL | re.IGNORECASE
    )
    
    cleaned_text = pattern.sub("", text_block).strip()
    
    return cleaned_text