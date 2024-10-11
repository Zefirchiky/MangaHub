from gui import MainGui
from scrapers import MangaTitlePageScraper

import os

class App:
    def __init__(self):
        self.dir = os.path.dirname(__file__)

        # self.scraper = MangaTitlePageScraper("https://asuracomic.net/series/nano-machine-b6b7f63d")
        # self.scraper.get_title_page()

        self.gui = MainGui(self)

    def run(self):
        self.gui.start()

if __name__ == "__main__":
    app = App()
    app.run()