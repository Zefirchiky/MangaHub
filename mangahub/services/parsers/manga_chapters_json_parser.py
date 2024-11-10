from models import Manga, MangaChapter
from .model_json_parser import ModelJsonParser
from .chapter_images_json_parser import ChapterImagesJsonParser


class MangaChaptersJsonParser(ModelJsonParser):
    def __init__(self, manga: Manga):
        super().__init__(f"{manga.folder}/chapters.json", MangaChapter)
        self.manga = manga
        self.chapters_collection = self.models_collection

    def get_chapter(self, num: float) -> MangaChapter | None:
        images_parser = ChapterImagesJsonParser(f"{self.manga.folder}/chapter{num}/images.json")
        chapter = super().get_model(num)
        chapter._images = images_parser.get_all_images()
        return chapter
    
    def get_model(self, name) -> MangaChapter | None:
        return self.get_chapter(name)   # so get_all_chapters() uses custom get_chapter()
    
    def get_all_chapters(self) -> dict[float, MangaChapter]:
        return self.get_all_models()
    
    def save(self, chapters_dict: dict[float, MangaChapter]):
        for chapter in chapters_dict.values():
            if chapter._images:
                folder = f"{self.manga.folder}/chapter{int(chapter.number) if chapter.number.is_integer() else str(chapter.number).replace('.', '_')}"  # 1 or 1_2
                images_parser = ChapterImagesJsonParser(f"{folder}/images.json")
                images_parser.save(chapter._images)
        super().save(chapters_dict)