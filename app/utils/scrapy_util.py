from scrapy.parser import extract_from_html
import requests


response = requests.get("https://aclanthology.org/D19-1632/")

data = extract_from_html(response=response)

print(data['image_links'])