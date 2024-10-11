from handlers import JsonHandler

class SitesJsonParser:
    '''Parses sites data from sites.json'''
    def __init__(self, file="mangamanager/data/sites.json"):
        self.file = file

        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()

    # def get_title_page_url(self, site_name):
    #     format = self.data[site_name]["title_page"]["title_page_url_format"]
    #     return f"{self.url}/{self.parse_url(title, page_number)}"

    # def get_chapter_page_url(self):
    #     return f"{self.url}/{self.format_url()}"

    # def format_url(self, title, page_number: int):
    #     return self.chapter_url_format \
    #             .replace("$title$", self.mangas[title]["title"]) \
    #             .replace("$num_identifier$", self.mangas[title]["num_identifier"]) \
    #             .replace("$chapter$", str(page_number))

