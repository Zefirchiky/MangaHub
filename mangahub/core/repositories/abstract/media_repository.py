from __future__ import annotations
from pathlib import Path
from loguru import logger
from application.services.parsers import TagModelsJsonParser
from .chapters_repository import ChaptersRepository
from core.models.abstract import AbstractMedia, AbstractChapter
    

class MediaRepository[MediaType: AbstractMedia, ChapterType: AbstractChapter, ChapterRepoType: ChaptersRepository[ChapterType]](
    TagModelsJsonParser[str, MediaType]
):
    def __init__(self, file: Path | str, model: MediaType, chapter_model: ChapterType, chapter_repository_model: ChapterRepoType):
        super().__init__(file, model, str)
        self.chapter_model = chapter_model
        self.chapter_repository_model = chapter_repository_model

    def get(self, name):
        media = super().get(name)
        if media and not media._chapters_repo:
            media._chapters_repo = self.chapter_repository_model(Path(media.folder) / 'chapters.json')
            
        return media
    
    def save(self):
        for model in self._models_collection.values():
            if model._chapters_repo:
                model._chapters_repo.save()
            else:
                logger.warning(f'{model} does not have a _chapters_repo attribute when trying to save')
        super().save()
