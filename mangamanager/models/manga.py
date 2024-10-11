from .manga_chapter import MangaChapter

class Manga:
    def __init__(self, name, cover):
        self.name = name
        self.cover = cover
        self.chapters = {}
        self.sites = []

    def add_chapter(self, chapter_number: int, chapter_name: str) -> None:
        """Add a chapter to the manga."""
        self.chapters[chapter_number] = MangaChapter(
            self,
            chapter_number,
            chapter_name,
        )

    def set_chapter_images(self, chapter_number: int, images: list) -> None:
        self.chapters[chapter_number].add_all_images(images)

    def get_chapter(self, chapter_number: int) -> str:
        return self.chapters[chapter_number]

    def add_site(self, site):
        self.sites.append(site.name)

    def to_dict(self):
        return {
            'name': self.name,
            'cover': self.cover,
            'chapters': self.chapters,
            'sites': self.sites
        }