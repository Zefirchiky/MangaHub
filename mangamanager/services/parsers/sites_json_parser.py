from services.handlers import JsonHandler
from models import Site, Manga, MangaChapter

class SitesJsonParser:
    def __init__(self, file="mangamanager/data/sites.json"):
        self.file = file
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()

    def get_site(self, name):
        try:
            site = self.data[name]
            return Site(site['name'], 
                        site['url'], 
                        site['title_page'], 
                        site['chapter_page'], 
                        site['manga'])
        except KeyError:
            print(f"Site {name} not found")
            return None

    def get_all_sites(self):
        sites = []
        
        for site in self.data:
            sites.append(Site(self.data[site]['name'], 
                                     self.data[site]['url'], 
                                     self.data[site]['title_page'], 
                                     self.data[site]['chapter_page'], 
                                     self.data[site]['manga']))
        
        return sites
    
    def get_title_page_url(self, site: Site, manga: Manga):
        url = site.url + "/" + site.title_page['url_format'].replace(
                '$manga_id$', manga._id
            ).replace(
                '$num_identifier$', site.manga[manga.name]['num_identifier']
            )

        return url

    def get_chapter_page_url(self, site: Site, manga: Manga, chapter_num: int):
        url = site.url + "/" + site.chapter_page['url_format'] \
            .replace('$manga_id$', manga._id) \
            .replace('$num_identifier$', site.manga[manga.name]['num_identifier']) \
            .replace('$chapter_num$', str(chapter_num))

        return url

