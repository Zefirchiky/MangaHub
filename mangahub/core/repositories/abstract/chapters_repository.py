from __future__ import annotations
from pathlib import Path
from loguru import logger
from application.services.parsers import TagModelsJsonParser
from ..abstract.chapter_data_repository import ChapterDataRepository
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.interfaces import AbstractChapter


class ChapterNotFoundError(Exception): ...

class ChaptersRepository[CP: AbstractChapter, CDR: ChapterDataRepository](TagModelsJsonParser[float, CP]):
    def __init__(self, file: Path | str, model: CP, chapter_data_repo: CDR):
        super().__init__(file, model, float)
        self.chapter_data_repo = chapter_data_repo
        
    def get(self, name, default='err') -> CP:
        chapter = super().get(name)
        
        if not chapter:
            if default == 'err':
                raise ChapterNotFoundError(f'Chapter {name} was not found')
            else:
                return default
        
        if chapter._repo is None:
            chapter._repo = self.chapter_data_repo(chapter.folder / "images.json")

        return chapter
        
    def save(self):
        for chapter in self._models_collection.values():
            if (repo := chapter._repo) is not None:
                repo.save()
            else:
                logger.warning(f'ChapterRepository: {chapter} does not have a repo (from chapter._repo) when trying to save')
        super().save()