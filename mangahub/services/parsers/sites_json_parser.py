from services.handlers import JsonHandler
from models import Site
from gui.gui_utils import MM

class SitesJsonParser:
    def __init__(self, file="data/sites.json"):
        self.file = file
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        self.sites = {}

    def get_site(self, name) -> Site | None:
        if name in self.sites.keys():
            return self.sites[name]
        else:
            try:
                site = Site(**self.data[name])
                self.sites[name] = site
                return site
            except KeyError:
                MM.show_message('error', f"Site {name} not found")
                return None

    def get_all_sites(self) -> dict:
        for site_name in self.data.keys():
            if site_name not in self.sites.keys():
                self.get_site(site_name)
        
        return self.sites
