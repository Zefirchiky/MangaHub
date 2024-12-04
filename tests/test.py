import requests
from rich import print
from bs4 import BeautifulSoup
import re

url = 'https://asuracomic.net/series/bad-born-blood-ffffffff'  # Replace with your target URL
regex = re.compile('bad-born-blood-\\w+/chapter/$chapter_num$'.replace('$chapter_num$', r'(?P<chapter_num>[0-9]+)'))
print('bad-born-blood-\\w+/chapter/$chapter_num$'.replace('$chapter_num$', r'(?P<chapter_num>[0-9]+)'))
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html_content = response.text

# bad-born-blood-\w+/chapter/(?P<chapter_num>[0-9]+)
# bad-born-blood-\w+/chapter/(?P<chapter_num>[0-9]+)

soup = BeautifulSoup(html_content, 'html.parser')

links = regex.findall(soup.)
print(max([int(i) for i in links]))