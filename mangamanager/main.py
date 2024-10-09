from parsers import SiteJsonParser
from gui import MainGui
from PySide6.QtWidgets import QApplication

import os

class App:
    def __init__(self):
        self.dir = os.path.dirname(__file__)

        self.gui = MainGui(self)

    def run(self):
        t = SiteJsonParser("AsuraScans")
        print(t.get_page_full_url("Boundless Necromancer", 1))
        self.gui.start()

if __name__ == "__main__":
    app = App()
    app.run()