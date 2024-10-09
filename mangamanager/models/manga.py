from .manga_chapter import MangaChapter

class Manga:
    def __init__(self, title, cover):
        self.title = title
        self.cover = cover
        self.chapters = {}

    def add_chapter(self, chapter_number: int) -> None:
        """Add a chapter to the manga."""
        self.chapters[chapter_number] = MangaChapter(
            self,
            chapter_number,
            self.get_chapter_name(chapter_number),
            self.get_chapter_images(chapter_number),
        )