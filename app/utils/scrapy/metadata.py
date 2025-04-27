import re
import logging
from typing import Optional, Dict, Match

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='../logs/metadata.log'
)

def extract_metadata(metadata_block: Optional[Match[str]]) -> Optional[Dict[str, str]]:
    """
    Extracts key-value metadata from a regex match object containing a metadata block string.
    
    The expected format within the metadata block is "key: balue", one pair per line.
    
    Args:
        metadata_block: A regex match object where group 1 contains the
                        string of meatadata, or None if no metadata block
                        was found by the initial regex.
                        
    Returns:
        A dictionary containing the extracted metadata key-value pairs,
        or None if the input metadata_block is None or empty.
        Returns an empty dictionary if a metadata block is found contains no
        valid key-value pairs.
        
    Raises:
        TypeError: If metadata_block is not None and not a regex match object.
        ValueError: If metadata_block is a regex match object but does not
                    contain the expected group 1.
        RuntimeError: If a key-value pair extracted by the regex is malformed
                    (should not happen with the current regex but added for robustness).
    """
    
    if metadata_block is None:
        logging.info("No metadata block provided.")
        return None
    
    ### Validate if input is a regex match object ###
    if not isinstance(metadata_block, Match):
        logging.error(f"Invalid input type for metadata_block: {type(metadata_block)}. Expected re.Match or None.")
        raise TypeError("Input 'metadata_block' must be a regex match object or None.")
    
    ### Ensure group 1 exists and contains the metadata text ###
    try:
        metadata_text = metadata_block.group(1)
        if not isinstance(metadata_text, str):
            logging.error(f"Unexpected type for metadata_block,group(1): {type(metadata_text)}, Expected string.")
            return {}
    except IndexError:
        logging.error("Metadata block matchh object does not contain group 1.")
        raise ValueError("Input 'metadata_block' is missing the expected capture group 1.")
    
    ### If metadata_text is empty after extraction, return empty dict
    if not metadata_text.strip():
        logging.info("Metadata block found but is empty or contains only whitespace.")
        return {}
    
    metadata_pattern = re.compile(r"^\s*([\w.-]+)\s*:\s*(.*?)\s*$", re.MULTILINE)
    
    matches = metadata_pattern.findall(metadata_text)
    
    metadata = {}
    for match in matches:
        if len(match) == 2:
            key, value = match
            metadata[key] = value.strip()
        else:
            logging.warning(f"Skipping malformed metadata line match: {match}")
    
    if not metadata:
        logging.info("Metadata block but no key-value pairs were extracted.")
        
    return metadata
    
    