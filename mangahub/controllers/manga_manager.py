from __future__ import annotations
import os
import shutil
from pathlib import Path

from PySide6.QtGui import QPixmap

from loguru import logger

from .placeholder_generator import PlaceholderGenerator
from models import URL
from models.manga import ChapterImage, Manga, MangaChapter
from models.images import ImageCache, ImageMetadata
from services.parsers import UrlParser
from services.repositories.manga import MangaChaptersRepository, MangaRepository, ImagesDataRepository
from services.scrapers import MangaDexScraper, MangaSiteScraper
from services.downloaders import ImageDownloader

from config import AppConfig
from utils import MM

from .sites_manager import SitesManager
from .chapter_image_loader import ChapterImageLoader

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mangahub.main import App


# TODO: reimplement


class MangaManager:
    def __init__(self, app: App):
        self.app = app
        self.repo: MangaRepository = self.app.manga_repository
        self.sites_manager: SitesManager = self.app.sites_manager
        self.dex_scraper = MangaDexScraper()
        self.sites_scraper = MangaSiteScraper(self.sites_manager)

        self.image_cache = ImageCache(
            AppConfig.Dirs.IMAGES_CACHE,
            max_ram=AppConfig.Caching.Image.max_ram(),
            max_disc=AppConfig.Caching.Image.max_disc(),
        )  # TODO: give sizes
        self.image_downloader = ImageDownloader(
            self.image_cache, AppConfig.ImageDownloading.max_threads()
        )
        self.chapter_loader = ChapterImageLoader(
            self.image_downloader, self.image_cache
        )

        logger.success("MangaManager initialized")

    def get_manga(self, name) -> Manga | None:
        manga = self.repo.get(name)
        if not manga:
            MM.show_warning(f"Manga {name} not found")
        return manga

    def get_all_manga(self) -> dict[str, Manga]:
        for manga in self.repo.get_all().values():
            if not manga._chapters_repo.get(1):
                manga.add_chapter(self.get_chapter(manga, 1))

            if not manga._chapters_repo.get(manga.last_chapter):
                manga.add_chapter(self.get_chapter(manga, manga.last_chapter))

            if (
                manga.current_chapter != 1
                and manga.current_chapter != manga.last_chapter
                and manga.current_chapter
                and not manga._chapters_repo.get(manga.current_chapter)
            ):
                manga.add_chapter(self.get_chapter(manga, manga.current_chapter))

        return self.repo.get_all()

    def add_new_manga(self, manga: Manga):
        self.repo.add(manga.name, manga)

    def create_manga(
        self, name: str, url: str | URL = "", site="MangaDex", backup_sites=[], overwrite=False, **kwargs
    ):
        if overwrite:
            if self.get_manga(name):
                self.remove_manga(name)
            
        elif self.get_manga(name):
            MM.show_warning(f"Manga {name} already exists")
            return

        if url:
            url = URL(url)
            site = self.sites_manager.get(url=url)
            if site:
                site = site.name
            else:
                raise Exception("Site not found")

        id_ = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "")
            .replace(".", "")
            .replace("?", "")
            .replace("!", "")
        )
        folder=Path(AppConfig.Dirs.MANGA) / id_
        folder.mkdir(exist_ok=True)
        id_dex = self.dex_scraper.get_manga_id(name)
        if id_dex:
            last = self.dex_scraper.get_last_chapter_num(id_dex)

        if site != "MangaDex":
            backup_sites = list(backup_sites)
            backup_sites.insert(0, "MangaDex")

        if site in backup_sites:
            backup_sites.remove(site)

        manga = Manga(
            name=name,
            id_=id_,
            folder=folder,
            id_dex=id_dex,
            
            first_chapter=1,    # TODO: Dynamic first chap
            current_chapter=1,
            last_read_chapter=1,
            last_chapter=last,
            site=site,
            backup_sites=backup_sites,
            
            **kwargs,
        ).set_changed()
        manga._chapters_repo = MangaChaptersRepository(folder / 'chapters.json')

        if not id_dex or not last:
            last = self.sites_scraper.get_last_chapter_num(
                self.sites_manager.get(site), manga
            )
            if last:
                manga.last_chapter = last

        cover = self.ensure_cover(manga)
        manga.cover = cover

        self.add_new_manga(manga)
        if site != "MangaDex":
            self.sites_manager.get(name=manga.site).add_manga(manga)  # type: ignore
        for site in manga.backup_sites:
            if site != "MangaDex":
                site_ = self.sites_manager.get(manga.site)
                if site_:
                    site_.add_manga(manga)

        logger.success(f"{manga} was created")
        return manga

    def remove_manga(self, manga: Manga | str) -> Manga:
        if isinstance(manga, str):
            manga = self.repo.get(manga)
        if manga:
            shutil.rmtree(manga.folder)
            mg = self.repo.pop(manga.name)
            site = self.sites_manager.get(manga.site)
            if site:
                site.remove_manga(manga)
            else:
                MM.show_warning(
                    f"Site {manga.site} of manga '{manga.name}' not found while removing"
                )
                raise Exception(
                    f"Site {manga.site} of manga '{manga.name}' not found while removing"
                )
            MM.show_success(f"Manga '{manga.name}' successfully removed")
            return mg

        MM.show_warning(
            f"Site {manga.site} of manga '{manga.name}' not found while removing"
        )
        return

    def create_chapter(self, manga: Manga, num: float):
        if chapter := manga._chapters_repo.get(num):
            return chapter

        id_dex = self.dex_scraper.get_chapter_id(manga.id_dex, num)
        name = ""
        if manga.site == "MangaDex":
            if id_dex:
                name = self.dex_scraper.get_chapter_name(manga.id_dex, num)
            else:
                logger.warning(f"No id_dex for chapter {num} of '{manga.name}'")
        else:
            name = self.sites_scraper.get_chapter_name(
                self.sites_manager.get(manga.site), manga, num
            )

        upload_date = self.dex_scraper.get_chapter_upload_date(manga.id_dex, num)

        chapter = MangaChapter(
            num=num, folder=manga.folder / f'chapter{num}', name=name, id_dex=id_dex, upload_date=upload_date
        ).set_changed()
        chapter._images = ImagesDataRepository(chapter.folder / 'images.json')
        return chapter

    def get_chapter(self, manga: Manga, num: int) -> MangaChapter:
        if chapter := manga.get_chapter(num):
            return chapter

        chapter = self.create_chapter(manga, num)
        if not chapter.urls_cached:
            urls = self.download_chapter_urls(manga, chapter)
            for i, url in enumerate(urls):
                chapter._images.add(
                    i,
                    ChapterImage(
                        number=i, name=f"{manga.id_}_{chapter.num}_{i}", metadata=ImageMetadata(url=url)
                    ).set_changed()
                )
            chapter.urls_cached = True
        return chapter

    def get_image(self, name: str) -> bytes:
        return self.image_cache.get_image(name)

    def get_placeholder(self, manga: Manga, chapter: MangaChapter, i: int) -> QPixmap:
        if not chapter._images:  # TODO
            pass
        elif not chapter._images.get(i):
            pass
        elif not chapter._images.get(i).metadata:
            pass
        else:
            return PlaceholderGenerator.static(
                chapter._images.get(i).metadata.width,  # type: ignore
                chapter._images.get(i).metadata.height,  # type: ignore
                f"#{i}",
            )

    def get_images(self, manga: Manga, chapter: MangaChapter):
        images: list[ChapterImage] = []

        if chapter._images:  # TODO: there MIGHT be missing images
            for image in chapter._images.get_all().values():
                images.append(image)
            return images

    def download_chapter_urls(self, manga: Manga, chapter: MangaChapter):
        logger.info(
            f"Downloading urls for '{manga.name}' chapter {chapter.num}'s images"
        )

        for site in manga.get_all_sites():
            if site == "MangaDex":
                if not chapter.id_dex:
                    chapter.id_dex = self.dex_scraper.get_chapter_id(
                        manga.id_dex, chapter.num
                    )
                    if not chapter.id_dex:
                        logger.warning(
                            f"No id_dex for chapter {chapter.num} of '{manga.name}'"
                        )
                        continue
                    logger.success(
                        f"Got id_dex for '{manga.name}' chapter {chapter.num}"
                    )

                urls = self.dex_scraper.get_chapter_image_urls(chapter.id_dex)
            else:
                urls = self.sites_scraper.get_chapter_image_urls(
                    self.sites_manager.get(site), manga, chapter.num
                )

        return urls

    def get_chapter_images(self, manga: Manga, chapter: MangaChapter):
        logger.info(f"Getting images for '{manga.name}' chapter {chapter.num}")

        images = []
        for site in manga.get_all_sites():
            if site == "MangaDex":
                if not chapter.id_dex:
                    chapter.id_dex = self.dex_scraper.get_chapter_id(
                        manga.id_dex, chapter.num
                    )
                    if not chapter.id_dex:
                        logger.warning(
                            f"No id_dex for chapter {chapter.num} of '{manga.name}'"
                        )
                        continue
                    logger.success(
                        f"Got id_dex for '{manga.name}' chapter {chapter.num}"
                    )

                images = self.dex_scraper.get_chapter_image_urls(chapter.id_dex)
            else:
                images = self.sites_scraper.get_chapter_image_urls(
                    self.sites_manager.get(site), manga, chapter.num
                )

            if images:
                break
            if site == manga.site:
                MM.show_warning(
                    f"Images wasn't parsed successfully for main site {site} of manga '{manga.name}'"
                )

        if not images:
            MM.show_warning(
                f"Images wasn't parsed successfully for manga '{manga.name}'"
            )
            return

        logger.success(f"Got images for '{manga.name}' chapter {chapter.num}")
        return images

    def get_chapter_placeholders(self, manga: Manga, chapter: MangaChapter):
        placeholders = []
        if chapter._images:
            for image in chapter._images.get_all().values():
                placeholders.append((image.metadata.width, image.metadata.height))
            logger.success(
                f"Got placeholders for '{manga.name}' chapter {chapter.num} from cache"
            )
            return placeholders

        logger.info(
            f"Downloading placeholders for '{manga.name}' chapter {chapter.num}"
        )
        sites = list(manga.backup_sites)
        sites.insert(0, manga.site)
        for site in sites:
            if site == "MangaDex":
                if not chapter.id_dex:
                    logger.warning(
                        f"No id_dex for chapter {chapter.num} of '{manga.name}'"
                    )
                    continue
                placeholders = self.dex_scraper.get_chapter_placeholders(chapter.id_dex)
            else:
                placeholders = self.sites_scraper.get_chapter_placeholders(
                    self.sites_manager.get(site), manga, chapter.num
                )

            if placeholders:
                break
            if site == manga.site:
                MM.show_warning(
                    f"Placeholders wasn't parsed successfully for main site {site} of manga '{manga.name}'"
                )

        if not placeholders:
            MM.show_warning(
                f"Placeholders wasn't parsed successfully for '{manga.name}'"
            )
            return

        logger.success(f"Got placeholders for '{manga.name}' chapter {chapter.num}")
        chapter.add_images(
            [
                ChapterImage(number=num, width=placeholder[0], height=placeholder[1])
                for num, placeholder in enumerate(placeholders)
            ]
        )
        return placeholders

    def get_manga_from_url(self, url):
        url_parser = UrlParser(url)
        site = url_parser.site
        _id = url_parser.manga_id
        name = _id.title().replace("-", " ")

        if not os.path.exists(f"{AppConfig.Dirs.MANGA}/{_id}"):
            os.makedirs(f"{AppConfig.Dirs.MANGA}/{_id}")

        cover = self.ensure_cover(_id, url_parser)

        return Manga(name, _id, cover, [site.name])

    def ensure_cover(self, manga: Manga):
        if os.path.exists(f"{manga.folder}/cover.jpg"):
            return "cover.jpg"

        if manga.id_dex:
            cover = self.dex_scraper.get_manga_cover(manga.id_dex)
        elif manga.backup_sites:
            scraper = MangaSiteScraper(self.sites_manager, sites=manga.backup_sites)
            cover = scraper.get_manga_cover(manga)  # TODO
        else:
            MM.show_error(f"No available site for {manga.id_} was found")
            return None

        if cover:
            with open(f"{manga.folder}/cover.jpg", "wb") as f:
                f.write(cover)

            return "cover.jpg"
        return None

    def add_chapter(self, manga: Manga, chapter: MangaChapter):
        manga.add_chapter(chapter)

    def save(self):
        self.repo.save()
