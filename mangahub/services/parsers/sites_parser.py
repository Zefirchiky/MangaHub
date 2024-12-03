from .models_json_parser import ModelsJsonParser
from models import Site


class SitesParser(ModelsJsonParser):
    def __init__(self, file="data/sites.json"):
        super().__init__(file, Site)

    def get_site(self, name) -> Site | None:
        return self.get_model(name)

    def get_all_sites(self) -> dict[str, Site]:
        return self.get_all_models()
