from dataclasses import dataclass, field

@dataclass
class Site:
    name: str
    url: str
    title_page: dict = field(default_factory=dict)
    chapter_page: dict = field(default_factory=dict)
    manga: dict = field(default_factory=dict)

    def add_manga(self, manga, num_identifier=None):
        self.manga[manga.name] = {
            'name': manga.name,
            'num_identifier': num_identifier
            }

    def set_manga_identifier(self, manga, num_identifier):
        if manga.name in self.manga:
            self.manga[manga.name]['num_identifier'] = num_identifier
        else:
            self.add_manga(manga, num_identifier)
        