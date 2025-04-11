from models.sites import Site

from .models_json_parser import ModelsJsonParser


class SitesParser(ModelsJsonParser):
    def __init__(self, file="data/sites.json"):
        super().__init__(file, Site)

    def get_site(self, name) -> Site | None:
        return self.get(name)

    def get_all_sites(self) -> dict[str, Site]:
        return self.get_all()
