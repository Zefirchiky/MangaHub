from pathlib import Path

from application.services.parsers import TagModelsJsonParser
from core.models.sites_ import SiteModel


class SitesRepository(TagModelsJsonParser[str, SiteModel]):
    def __init__(self, file: Path | str):
        super().__init__(file, SiteModel, str)