from pathlib import Path

from models.sites import Site

from .models_json_parser import ModelsJsonParser


class SitesParser(ModelsJsonParser[str, Site]):
    def __init__(self, file: Path | str="data/sites.json"):
        super().__init__(file, Site, str)

    def get_site(self, name) -> Site | None:
        return self.get(name)

    def get_all_sites(self) -> dict[str, Site]:
        return self.get_all()
