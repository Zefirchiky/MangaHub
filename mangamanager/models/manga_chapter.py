class MangaChapter:
    def __init__(self, manga, chapter_number: int, chapter_name: str, images: list):
        self.manga = manga
        self.number = chapter_number
        self.name = chapter_name
        self.images = images

    def __iter__(self):
        return iter(self.images)