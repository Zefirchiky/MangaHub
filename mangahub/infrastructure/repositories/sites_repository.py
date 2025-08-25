from pathlib import Path

from application.services.parsers import TagModelsJsonParser
from domain.models.sites import Site


class SitesRepository(TagModelsJsonParser[str, Site]):
    def __init__(self, file: Path | str):
        super().__init__(file, Site, str)