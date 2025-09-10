from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.interfaces import AbstractMedia

class UrlParser:
    @staticmethod
    def fill_chapter_url(url_format: str, media_id: str, num: int, **kwargs):
        m = {
            'media_id': media_id,
            'chapter_num': num,
            **kwargs
        }
        return url_format.format_map(m)
    
    @staticmethod
    def fill_media_url(url_format: str, media: AbstractMedia, **kwargs) -> str:
        m = {
            'media_id': media.id_,
            **kwargs
        }
        return url_format.format_map(m)