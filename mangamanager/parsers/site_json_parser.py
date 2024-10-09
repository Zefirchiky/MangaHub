from handlers import JsonHandler

class SiteJsonParser:
    '''Parses site data from sites.json'''
    def __init__(self, site_name: str, file="mangamanager/data/sites.json"):
        self.site_name = site_name
        self.file = file

        self.json_parser = JsonHandler(self.file)
        self.site_data = self.json_parser.get_data()[self.site_name]

        self.url = self.site_data["url"]
        self.chapter_url_format = self.site_data["chapter_page"]["chapter_url_format"]
        self.mangas = self.site_data["mangas"]

    def get_title_page_url(self, title, page_number: int):
        return f"{self.url}/{self.parse_url(title, page_number)}"

    def get_chapter_page_url(self):
        return

    def parse_url(self, title, page_number: int):
        return self.chapter_url_format \
                .replace("$title$", self.mangas[title]["title"]) \
                .replace("$num_identifier$", self.mangas[title]["num_identifier"]) \
                .replace("$chapter$", str(page_number))

