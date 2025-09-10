from __future__ import annotations
from loguru import logger

from core.repositories.novels import NovelChaptersRepository, ParagraphsRepository
from core.models.novels import Novel, NovelChapter, NovelParagraph
from core.repositories.novels import NovelsRepository
from application.services.scrapers import NovelsSiteScraper
from config import Config
from utils import MM
from utils.id_from_name import get_id_from_name

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mangahub.main import App


class NovelsManager:
    def __init__(self, app: App):
        self.app = app
        self.repository: NovelsRepository = self.app.novels_repository
        self.repository.get_all()
        self.scraper = NovelsSiteScraper(self.app.sites_manager)
        self.sites_manager = self.app.sites_manager

        logger.success("NovelsManager initialized")

    def get_novel(self, name: str) -> Novel:
        novel = self.repository.get(name)
        if not novel:
            MM.show_warning(f"Novel {name} not found")

        return self._ensure_novels_essential_data({novel.name: novel})

    def get_all_novels(self) -> dict[str, Novel]:
        return self._ensure_novels_essential_data(self.repository.get_all())

    def get_chapter(self, novel: Novel, num: int) -> NovelChapter | None:
        return novel._chapters_data.get(num)
    
    def create_empty(self, name: str, **kwargs) -> Novel:
        id_ = get_id_from_name(name)
        novel = Novel(
            name = name,
            id_  = id_,
            folder = Config.Dirs.DATA.NOVELS / f'{id_}',
            **kwargs,
        ).set_changed()
        novel._chapters_repo = NovelChaptersRepository(novel.folder / 'chapters.json')
        return novel
    
    def create_empty_chapter(self, novel: Novel, num: float=0, **kwargs) -> NovelChapter:
        chapter = NovelChapter(
            num=num,
            folder = novel.folder / str(num),
            **kwargs,
        ).set_changed()
        chapter._repo = ParagraphsRepository(chapter.folder / 'paragraphs.json').add(0, NovelParagraph())
        return chapter

    def create_novel(self, name: str) -> Novel:
        novel = Novel(
            name=name,
        )

    def create_novel_from_text(self, text: str):
        text = self.scraper.get_temp_novel_text()

    @classmethod
    def _ensure_novels_essential_data(
        cls, novels: dict[str, Novel]
    ) -> dict[str, Novel]:
        for novel in novels.values():
            if not novel._chapters_data.get(1):
                novel.add_chapter(cls.get_chapter(novel, 1))
            if not novel._chapters_data.get(novel.last_chapter):
                novel.add_chapter(cls.get_chapter(novel, novel.last_chapter))
            if (
                novel.current_chapter != 1
                and novel.current_chapter != novel.last_chapter
                and novel.current_chapter
                and not novel._chapters_data.get(novel.current_chapter)
            ):
                novel.add_chapter(cls.get_chapter(novel, novel.current_chapter))

        return novels
