from bs4 import BeautifulSoup
import re

TEXT_TAG = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
            'span', 'li', 'div']
VIDEO_TAG = ['iframe']
IMG_TAG = ['img']

def extract_from_html(response: str):
    """
    Extract text, image and video content form the HTMl page.
    
    Returns:
        dict: A dictionary containing lists of 'text', 
            'video_links' and 'image_links'. Returns 
            None if there's an issue fetching the page.
    """
    
    try:
        html_content = BeautifulSoup(response.content, 'html.parser')
        
        text_content = []
        for element in html_content.find_all(TEXT_TAG):
            if element.name not in ['script', 'style']:
                text = element.get_text(separator='n', strip=True)
                if text:
                    text_content.append(text)
                    
        return {
            'text': list(set(text_content))
        }
    except Exception as e:
        return None
    
    
    