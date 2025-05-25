from __future__ import annotations
from pydantic import PrivateAttr

from ..abstract.abstract_chapter import AbstractChapter
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from services.repositories.manga import ImagesDataRepository


class MangaChapter(AbstractChapter):
    id_dex: str = ""
    url: str = ""
    urls_cached: bool = False
    total_bytes: int = 0
    _images = PrivateAttr(default=None)
    
    def get_data_repo(self) -> ImagesDataRepository:
        return self._images
    
    def set_data_repo(self, repo):
        self._images = repo
