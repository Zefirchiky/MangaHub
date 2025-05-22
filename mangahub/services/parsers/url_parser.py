from __future__ import annotations
import re

from loguru import logger
from models import URL
from ..repositories.sites_repository import SitesRepository
from utils import MM

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.abstract import AbstractMedia, AbstractChapter
    from models.manga import Manga
    from models.sites import Site


class UrlParser:
    
    @staticmethod
    def get_chapter_url(url_format: str, media_id: str, num: int):
        m = {
            'media_id': media_id,
            'chapter_num': num,
        }
        return url_format.format_map(m)
    
    @staticmethod
    def fill_media_url(url_format: str, media: AbstractMedia, **kwargs) -> str:
        m = {
            'media_id': media.id_,
            **kwargs
        }
        return url_format.format_map(m)