from models import Site
from bs4 import BeautifulSoup
import requests # type: ignore


class MangaSiteScraper:
    def __init__(self, site: Site):
        self.site = site

    def get_title_page(self):
        path = "mangamanager/data/manga/boundless_necromancer/title_page.jpg"
        html = requests.get(self.url)
        soup = BeautifulSoup(html.text, 'html.parser')
        for i in soup.find_all('img', class_='rounded mx-auto md:mx-0'):
            print(i.get('src'))
            with open(path, 'wb') as f:
                f.write(requests.get(i.get('src')).content)
        return path
    
    def get_chapter_page(self) -> bytes:
        path = "mangamanager/data/manga/boundless_necromancer/chapters/chapter1-name/1_1.webp"
        html = requests.get(self.url)
        soup = BeautifulSoup(html.text, 'html.parser')
        i = soup.find_all('img', class_='object-cover mx-auto')[1]
        with open(path, 'wb') as f:
            f.write(requests.get(i.get('src')).content)
        return requests.get(i.get('src')).content