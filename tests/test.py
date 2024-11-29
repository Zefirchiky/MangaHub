import requests
from rich import print
from bs4 import BeautifulSoup
import re

url = 'https://asuracomic.net/series/nano-machine-b0c4445b/chapter/1'  # Replace with your target URL
regex = re.compile('https://gg\\.asuracomic\\.net/storage/media/\\d{6}/conversions/\\d{2}-optimized\\.webp')
regex = re.compile(r'https://gg\.asuracomic\.net/storage/media/\d{6}/conversions/\d{2}-optimized\.webp')
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

scripts = soup.find_all('script')

urls = {}
for script in scripts:
    if script.string:
        urls_ = re.findall(regex, script.string)
        if urls_:
            for i, url in enumerate(urls_, 1):
                if not i in urls.keys():
                    urls[i] = url
                
print(urls)