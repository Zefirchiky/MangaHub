class MangaChapter:
    def __init__(self, manga, chapter_number: int, chapter_name: str):
        self.number = chapter_number
        self.name = chapter_name
        self.images = []

    def add_image(self, image):
        self.images.append(image)

    def add_all_images(self, images):
        self.images = images

    def __iter__(self):
        return iter(self.images)