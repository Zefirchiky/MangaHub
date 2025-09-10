from __future__ import annotations
from pathlib import Path
import shutil

from PySide6.QtCore import QObject, Signal, Slot
from loguru import logger

from core.models.images import ImageCache, ImageMetadata
from core.models.manga import Manga, MangaChapter, ChapterImage
from core.models.sites_ import SiteModel
from core.repositories.manga import MangaChaptersRepository, ImagesDataRepository
from utils.id_from_name import get_id_from_name
from config import Config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class MangaManager(QObject):
    cover_downloaded = Signal(str, bytes)
    chapters_dict_downloaded = Signal(str)
    image_meta_loaded = Signal(int, ImageMetadata)  # image num, metadata
    image_loaded = Signal(int, ImageMetadata) # image num, name
    
    def __init__(self, app: App):
        super().__init__()
        self.repo = app.manga_repository
        self.sites_manager = app.sites_manager
        self.download_manager = app.download_manager
        
        self.images_cache = self.download_manager.images_cache
        
        self.sites_manager.manga_signals.chapters_list.connect(self._chapters_list_downloaded)
        self.sites_manager.manga_signals.cover_url_downloaded.connect(self._cover_url_downloaded)
        self.download_manager.cover_downloaded.connect(lambda manga_id, _: logger.success(f'Cover for {manga_id} was downloaded successfully'))
        self.download_manager.cover_downloaded.connect(self._cover_downloaded)
        self.download_manager.manga_details_downloaded.connect(lambda manga_id: self._downloading_manga.pop(manga_id))
        self.download_manager.chapter_images_urls_downloaded.connect(self._image_urls_downloaded)
        self.download_manager.image_metadata_downloaded.connect(self._image_metadata_downloaded)
        self.download_manager.image_downloaded.connect(self._image_downloaded)
        
        self._downloading_manga = []
        
    def get(self, id_: str) -> Manga | None:
        manga = self.repo.get(id_)
        if manga.id_ in self._downloading_manga:
            return manga
            
        if not self._ensure_cover(manga):
            self.download_manager.download_cover(manga)
        
        return manga
    
    def get_all(self) -> list[Manga]:
        result = []
        for name in self.repo.get_all():
            result.append(self.get(name))
        return result
    
    def load_chapter(self, manga: Manga, num: float):
        chapter = manga._chapters_repo.get(num)
        if not chapter:
            logger.error(f'Requested non-existed manga chapter: {manga} - {num}')
            return None
        
        if chapter.urls_cached:
            self.download_manager.download_manga_chapter_images(manga, chapter)
        else:
            self.download_manager.download_manga_chapter_details(manga, num)
        
    def create_empty(self, name: str, **kwargs):
        id_ = get_id_from_name(name)
        manga = Manga(
            name = name,
            id_  = id_,
            folder = Config.Dirs.DATA.MANGA / f'{id_}',
            **kwargs,
        ).set_changed()
        manga._chapters_repo = MangaChaptersRepository(manga.folder / 'chapters.json')
        return manga
        
    def create(self, name: str, site: SiteModel | str, overwrite: bool=False):
        id_ = get_id_from_name(name)
        if overwrite and self.repo.get(id_):
            manga = self.repo.pop(id_)
            shutil.rmtree(manga.folder)
        elif manga := self.repo.get(id_):
            return manga
        
        manga = self.create_empty(name)
        self.repo.add(manga.id_, manga)
        if isinstance(site, str):
            site_name = site
            site = self.sites_manager.get(site)
            if not site:
                logger.exception(f"No site with name '{site_name}', defaulting to MangaDex")
                site = 'MangaDex'
            
        if site != 'MangaDex':
            manga.add_site(site.name, 0)
            site.add_manga(manga.id_)
            
        self._downloading_manga.append(manga.id_)
        self.sites_manager.download_manga_details(manga)
        return manga
        
    def remove(self, manga: str | Manga) -> Manga:
        if not isinstance(manga, str):
            manga = manga.id_
        return self.repo.pop(manga)
        
    
    def _ensure_cover(self, manga: Manga) -> bool:
        return manga.cover and (manga.folder / 'cover.webp').exists()
    
    
    @Slot(str, list)
    def _chapters_list_downloaded(self, manga_id: str, chapters: list[str | tuple[str, str]]):
        if not chapters:
            logger.warning(f'Chapters list for {manga_id} is empty')
            return
        
        chapters_dict = {}
        for chapter in chapters:
            if isinstance(chapters[0], tuple):
                if chapter[0].isdigit():
                    chapters_dict[int(chapter[0])] = chapter[1]
                elif chapter[1].isdigit():
                    chapters_dict[int(chapter[1])] = chapter[0]
                else:
                    raise ValueError(f'Chapter `{chapter}` from `{manga_id}` does not have a number')
        else:
            chapters_dict = dict.fromkeys(map(int, chapters), '')
        
        manga = self.get(manga_id)
        chapters_dict = dict(sorted(chapters_dict.items()))
        for num, name in chapters_dict.items():
            chapter = MangaChapter(
                num=num,
                folder=Path(manga.folder / f'chapter{num}'),
                name=name
            ).set_changed()
            chapter._repo = ImagesDataRepository(chapter.folder / 'images.json')
            manga._chapters_repo.add(num, chapter)

        manga.current_chapter = manga._chapters_repo.get_i(0).num

        self.chapters_dict_downloaded.emit(manga_id)
    
    @Slot(str, str)
    def _cover_url_downloaded(self, manga_id: str, url: str):
        manga = self.repo.get(manga_id)
        manga.cover = url
        self.download_manager._download_cover(manga_id, url)
        
    @Slot(str, bytes)
    def _cover_downloaded(self, manga_id: str, image: bytes):
        manga = self.repo.get(manga_id)
        with (manga.folder / 'cover.webp').open('wb') as f:
            f.write(image)
        self.cover_downloaded.emit(manga_id, image)
        
    @Slot(str, float, list)
    def _image_urls_downloaded(self, manga_id: str, num: float, urls: list[str]):
        manga = self.get(manga_id)
        chapter = manga.get_chapter(num)
        if not chapter:
            logger.warning(f'No chapter {num} for {manga}')
            return
        repo = chapter._repo
        for i, url in enumerate(urls):
            repo.add(i, ChapterImage(
                number=i,
                metadata=ImageMetadata(
                    url=url
                )
            ))
        self.download_manager.download_manga_chapter_images(manga_id, chapter)

    @Slot(str, float, int, ImageMetadata) 
    def _image_metadata_downloaded(self, manga_id: str, chapter_num: float, image_num: int, metadata: ImageMetadata):
        self.image_meta_loaded.emit(image_num, metadata)
        
    @Slot(str, float, int, ImageMetadata)
    def _image_downloaded(self, manga_id: str, chapter_num: float, image_num: int, meta: ImageMetadata): # manga id, chapter num, image num, name
        self.image_loaded.emit(image_num, meta)

    
    def save(self):
        self.repo.save()