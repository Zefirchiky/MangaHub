from loguru import logger

from services.parsers import SitesParser


class SitesManager:
    sites_parser = SitesParser()

    def __init__(self, sites_parser=sites_parser):
        self.sites_parser = sites_parser
        
        logger.success('SitesManager initialized')

