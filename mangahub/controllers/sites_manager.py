from services.parsers import SitesJsonParser


class SitesManager:
    sites_parser = SitesJsonParser()

    def __init__(self, sites_parser=sites_parser):
        self.sites_parser = sites_parser

