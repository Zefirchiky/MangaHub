from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot
from loguru import logger

from models.manga import Manga, MangaChapter
from models.sites import Site
from services.repositories.manga import MangaChaptersRepository, ImagesDataRepository
from config import Config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class MangaManager(QObject):
    cover_downloaded = Signal(str, bytes)
    chapters_dict_downloaded = Signal(str, object)
    
    def __init__(self, app: App):
        super().__init__()
        self.repo = app.manga_repository
        self.sites_manager = app.sites_manager
        self.download_manager = app.download_manager
        
        self.sites_manager.manga_signals.chapters_list.connect(self._chapters_list_downloaded)
        self.sites_manager.manga_signals.cover_url_downloaded.connect(self._cover_url_downloaded)
        self.download_manager.cover_downloaded.connect(lambda manga_name, _: logger.success(f'Cover for {manga_name} was downloaded successfully'))
        self.download_manager.cover_downloaded.connect(self._cover_downloaded)
        self.download_manager.manga_details_downloaded.connect(lambda manga_name: self._downloading_manga.pop(manga_name))
        
        self._downloading_manga = []
        
    def get(self, name: str) -> Manga | None:
        manga = self.repo.get(name)
        if manga.name in self._downloading_manga:
            return manga
            
        if not self._ensure_cover(manga):
            self.download_manager.download_cover(manga)
            
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
    
    def get_all(self) -> list[Manga]:
        result = []
        for name in self.repo.get_all():
            result.append(self.get(name))
        return result
    
        
    def create_empty(self, name: str, **kwargs):
        id_ = name.lower()
        for s1, s2 in Config.UrlParsing.replace_symbols().items():
            id_ = id_.replace(s1, s2)
            
        manga = Manga(
            name = name,
            id_  = id_,
            folder = Config.Dirs.MANGA / f'{id_}',
            **kwargs,
        ).set_changed()
        manga._chapters_repo = MangaChaptersRepository(manga.folder / 'chapters.json')
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
            site.add_manga(name, manga.id_)
            
        self._downloading_manga.append(manga.name)
        self.sites_manager.download_manga_details(manga)
        return manga
        
    def remove(self, manga: str | Manga) -> Manga:
        if not isinstance(manga, str):
            manga = manga.name
        return self.repo.pop(manga)
        
    def _ensure_cover(self, manga: Manga) -> bool:
        return manga.cover and (manga.folder / manga.cover).exists()
    
    
    @Slot(str, list)
    def _chapters_list_downloaded(self, manga_name: str, chapters: list[str | tuple[str, str]]):
        if not chapters:
            logger.warning(f'Chapters list for {manga_name} is empty')
            return
        
        chapters_dict = {}
        for chapter in chapters:
            if isinstance(chapters[0], tuple):
                if chapter[0].isdigit():
                    chapters_dict[int(chapter[0])] = chapter[1]
                elif chapter[1].isdigit():
                    chapters_dict[int(chapter[1])] = chapter[0]
                else:
                    raise ValueError(f'Chapter `{chapter}` from `{manga_name}` does not have a number')
        else:
            chapters_dict = dict.fromkeys(map(int, chapters), '')
        
        chapters_dict = dict(sorted(chapters_dict.items()))
        manga = self.get(manga_name)
        manga.chapters = chapters_dict
        
        for num, name in manga.chapters.items():
            chapter = MangaChapter(
                num=num,
                folder=Path(manga.folder / f'chapter{num}'),
                name=name
            ).set_changed()
            chapter.set_data_repo(ImagesDataRepository(chapter.folder / 'images.json'))
            manga._chapters_repo.add(num, chapter)

        manga.current_chapter = manga._chapters_repo.get_i(0).num

        self.chapters_dict_downloaded.emit(manga_name, manga.chapters)
    
    @Slot(str, str)
    def _cover_url_downloaded(self, manga_name: str, url: str):
        manga = self.repo.get(manga_name)
        manga.cover = url
        self.download_manager._download_cover(manga_name, url)
        
    @Slot(str, bytes)
    def _cover_downloaded(self, manga_name: str, image: bytes):
        manga = self.repo.get(manga_name)
        with (manga.folder / 'cover.webp').open('wb') as f:
            f.write(image)
        self.cover_downloaded.emit(manga_name, image)
    
    
    def save(self):
        self.repo.save()