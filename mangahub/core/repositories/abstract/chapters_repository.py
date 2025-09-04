from __future__ import annotations
from pathlib import Path
from loguru import logger
from services.parsers import TagModelsJsonParser
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.models.abstract import AbstractChapter


class ChaptersRepository[CP: AbstractChapter](TagModelsJsonParser[float, CP]):
    def __init__(self, file: Path | str, model: CP):
        super().__init__(file, model, float)
        
    def save(self):
        for chapter in self._models_collection.values():
            if (repo := chapter.get_data_repo()) is not None:
                repo.save()
            else:
                logger.warning(f'ChapterRepository: {chapter} does not have a repo (from chapter.get_data_repo()) when trying to save')
        super().save()