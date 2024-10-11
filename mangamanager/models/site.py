class Site:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.title_page = {}
        self.chapter_page = {}
        self.manga = {}

    def set_title_page(self, title_page):
        self.title_page = title_page

    def set_cover_url(self, cover_url):
        self.title_page['cover'] = cover_url

    def set_name_url(self, name_url):
        self.title_page['name'] = name_url

    def set_chapter_page(self, chapter_page):
        self.chapter_page_page = chapter_page

    def set_chapter_images_url(self, images_url):
        self.chapter_page['images'] = images_url

    def set_chapter_name_url(self, name_url):
        self.chapter_page['name'] = name_url

    def add_manga(self, manga, num_identifier=None):
        self.manga[manga.name] = {
            'name': manga.name,
            'num_identifier': num_identifier
            }

    def set_manga_identifier(self, manga, num_identifier):
        self.manga[manga.name]['num_identifier'] = num_identifier
    