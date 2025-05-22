from __future__ import annotations

from loguru import logger

from models.manga import Manga
from models.sites import Site
from config import Config
from services.downloaders.download_manager import DownloadManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class MangaManager:
    def __init__(self, app: App):
        super().__init__()
        self.repo = app.manga_repository
        self.sites_manager = app.sites_manager
        self.download_manager = DownloadManager()
        
        self.sites_manager.manga_signals.cover_url_downloaded.connect(self._cover_url_downloaded)
        self.download_manager.cover_downloaded.connect(self._cover_downloaded)
        
        self.cover_downloaded = self.download_manager.cover_downloaded
        
    def get(self, name: str) -> Manga | None:
        manga = self.repo.get(name)
        # if not self._ensure_cover(manga):
        #     self.download_manager.download_cover(manga)
            
        # if not self._ensure_first_chapter(name):
        #     self.download_manager.download_manga_chapters_list(name)
        # if manga.current_chapter != manga.first_chapter and not self._ensure_current_chapter(name):
        #     self.download_manager.download_manga_chapters_list(name)
        # if manga.last_chapter == -1:
        #     self.download_manager.download_manga_chapters_list(name)
        # elif not self._ensure_last_chapter(manga):
        #     self.download_manager.download_manga_chapters_list(name)
        
        # self.download_manager.start(name)
        
        return manga
    
        
    def create_empty(self, name: str, **kwargs):
        id_ = name.lower().replace(' ', '-')
        manga = Manga(
            name = name,
            id_  = id_,
            folder = Config.Dirs.MANGA / f'{id_}.json',
            **kwargs,
        ).set_changed()
        self.repo.add(manga.name, manga)
        return self.repo.get(name)
        
    def create(self, name: str, site: Site | str):
        manga = self.create_empty(name)
        if isinstance(site, str):
            site_name = site
            site = self.sites_manager.get(site)
            if not site:
                logger.exception(f"No site with name '{site_name}', defaulting to MangaDex")
                site = 'MangaDex'
            
        if site != 'MangaDex':
            manga.add_site(site.name, 0)
            
        self.sites_manager.download_manga_details(manga)
        return manga
        
    def remove(self, manga: str | Manga) -> Manga:
        if not isinstance(manga, str):
            manga = manga.name
        return self.repo.pop(manga)
        
    def _ensure_cover(self, manga: Manga) -> bool:
        return manga.cover and (manga.folder / manga.cover).exists()
    
    def _ensure_last_chapter(self, manga: Manga):
        return manga.last_chapter != -1
    
    
    def _cover_url_downloaded(self, manga_name: str, url: str):
        self.download_manager.download_cover(manga_name, url)
        
    def _cover_downloaded(self, manga_name: str, image: bytes):
        manga = self.repo.get(manga_name)
        with (manga.folder / 'cover.webp').open('wb') as f:
            f.write(image)
        manga.cover = 'cover.webp'
    
    
    def save(self):
        self.repo.save()