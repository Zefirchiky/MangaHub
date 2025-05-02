from __future__ import annotations
from pathlib import Path
from loguru import logger
from services.parsers import TagModelsJsonParser
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.abstract import AbstractChapter


class ChaptersRepository[ChapterType: AbstractChapter](TagModelsJsonParser[int, ChapterType]):
    def __init__(self, file: Path | str, model: ChapterType):
        super().__init__(file, model, int)
        
    def save(self):
        for chapter in self._models_collection.values():
            if repo := chapter.get_data_repo():
                repo.save()
            else:
                logger.warning(f'{chapter} does not have a repo (from chapter.get_data_repo()) when trying to save')
        super().save()