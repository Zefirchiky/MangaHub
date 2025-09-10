from __future__ import annotations
from pathlib import Path
from loguru import logger
from application.services.parsers import TagModelsJsonParser
from .chapters_repository import ChaptersRepository
from core.interfaces import AbstractMedia, AbstractChapter


class MediaNotFoundError(Exception): ...

class MediaRepository[MT: AbstractMedia, CT: AbstractChapter, CRT: ChaptersRepository[CT]](
    TagModelsJsonParser[str, MT]
):
    def __init__(self, file: Path | str, model: MT, chapter_model: CT, chapter_repository_model: CRT):
        super().__init__(file, model, str)
        self.chapter_model = chapter_model
        self.chapter_repository_model = chapter_repository_model

    def get(self, name, default='err') -> MT:
        media = super().get(name)
        
        if not media:
            if default == 'err':
                raise MediaNotFoundError(f'Media {name} was not found')
            else:
                return default
            
        if not media._chapters_repo:
            media._chapters_repo = self.chapter_repository_model(Path(media.folder) / 'chapters.json')
            
        return media
    
    def save(self):
        for model in self._models_collection.values():
            if model._chapters_repo:
                model._chapters_repo.save()
            else:
                logger.warning(f'{model} does not have a _chapters_repo attribute when trying to save')
        super().save()
