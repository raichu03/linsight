import logging
import os
from typing import Dict, Any, Optional

import ollama

#--- Logging Setup ---#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/generate_query.log'
)

WEB_SEARCH_PROMPT_TEMPLATE = """
User has given this query to make a web search. Can you expand the query to make it more suitable for the web search.

** Additional Guidelines: **
- Answer with only the expanded query and nothing else.
- The query should be good for web search in the related topic.
- Don't make it long, keep it concise.

** Query to Expand **
'{query}'
"""

def gen_query(query: str) -> Optional[str]:
    """
    Expands a given query using an Ollama language model to make it more suitable for web search.

    Args:
        query (str): The initial query provided by the user.

    Returns:
        Optional[str]: The expanded query string, or None if an error occurred.
    """
    if not query or not isinstance(query, str):
        logging.error("Invalid input: Query must be a non-empty string.")
        return None
    
    prompt_message = WEB_SEARCH_PROMPT_TEMPLATE.format(query=query)
    
    try:
        logging.info(f"Attempting to expand query: '{query}' using model 'llama3.2'")
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'user', 'content': prompt_message}
            ],
            options={
                'temperature': 0.1,
            },
            stream=False,
        )
        message_content: str = response.get('message', {}).get('content', '').strip()
        
        if not message_content:
            logging.warning(f"Ollama returned an empty message for query: '{query}'")
            return None

        logging.info(f"Successfully expanded query: '{query}' to '{message_content}'")
        return message_content
    except ollama.ResponseError as e:
        logging.error(f"Ollama API error for query '{query}': {e}")
        return None
    except ollama.RequestError as e:
        logging.error(f"Ollama request error (e.g., connection issue) for query '{query}': {e}")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred during query expansion for '{query}': {e}")
        return None