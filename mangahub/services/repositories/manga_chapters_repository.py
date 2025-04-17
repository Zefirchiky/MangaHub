from loguru import logger

from models.manga import Manga, MangaChapter

from ..parsers.chapter_images_parser import ChapterImagesParser
from ..parsers.models_json_parser import ModelsJsonParser


class MangaChaptersRepository(ModelsJsonParser[int, MangaChapter]):
    def __init__(self, manga: Manga):
        super().__init__(f"{manga.folder}/chapters.json", MangaChapter, int)
        self.manga = manga
        # from icecream import ic
        # ic(manga._chapters_data[1]._images)
        self.chapters_collection = self._models_collection

    def get(self, num: int | float) -> MangaChapter | None:
        images_parser = ChapterImagesParser(f"{self.manga.folder}/chapter{num}/images.json")
        try:
            chapter = super().get(num)
        except Exception as e:
            logger.warning(f"Chapter {num} not found with error: {e}. Returning None")
            return None
        
        chapter._images = images_parser.get_all()
        return chapter
    
    def save(self, chapters_dict: dict[float, MangaChapter]):
        for chapter in chapters_dict.values():
            if chapter._images:
                folder = f"{self.manga.folder}/chapter{int(chapter.number) if chapter.number.is_integer() else str(chapter.number).replace('.', '_')}"  # 1 or 1_2
                images_parser = ChapterImagesParser(f"{folder}/images.json")
                images_parser.save(chapter._images)
        super().save(chapters_dict)