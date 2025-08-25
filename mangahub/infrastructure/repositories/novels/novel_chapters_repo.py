from ..abstract.chapters_repository import ChaptersRepository
from domain.models.novels import NovelChapter
from .paragraphs_repository import ParagraphsRepository


class NovelChaptersRepository(ChaptersRepository[NovelChapter]):
    def __init__(self, file):
        super().__init__(file, NovelChapter)

    def get(self, name) -> NovelChapter | None:
        chapter = super().get(name)
        if chapter and chapter.get_data_repo() is None:
            chapter.set_data_repo(ParagraphsRepository(
                chapter.folder / 'text.json'
            ))
            
        return chapter
