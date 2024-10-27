from gui.gui_utils import MM
from utils import BatchWorker
from typing import Any
from utils import convert_to_format
import requests


class MangaDexScraper:
    def __init__(self):
        self.base_api_url = "https://api.mangadex.org"
        self.base_upload_url = "https://uploads.mangadex.org"
        
        self.manga_url = f"{self.base_api_url}/manga"
        self.cover_url = f"{self.base_upload_url}/covers"
        self.chapter_url = f"{self.base_api_url}/chapter"
        self.chapters_url = f"{self.base_api_url}/at-home/server"
        
        self.manga_data = {}
        self.chapters_data = {}
    
    def get_manga_data(self, name):
        if name in self.manga_data.keys():
            return self.manga_data[name]
        
        params = {
            "title": name,
            "limit": 1
        }

        response = requests.get(self.manga_url, params=params)
        response.raise_for_status()
        data = response.json()["data"][0]
        if not data:
            MM.show_message('error', f"Manga {name} not found")
            raise Exception(f"Manga {name} not found")
            
        self.manga_data[name] = data
        
        return data
    
    def get_manga_id(self, name):
        data = self.get_manga_data(name)
        return data["id"]
        
    def get_chapter_data(self, manga_id, num, limit=1, language="en"):
        if not self.chapters_data.get(manga_id):
            self.chapters_data[manga_id] = {}
            
        if manga_id in self.chapters_data.keys():
            if num in self.chapters_data[manga_id].keys():
                return self.chapters_data[manga_id][num]
            
        params = {
            "manga": manga_id,
            "translatedLanguage[]": language,
            "offset": num - 1,
            "limit": limit
        }
        
        response = requests.get(self.chapter_url, params=params)
        response.raise_for_status()
        data = response.json()["data"][0]
        if not data:
            MM.show_message('error', f"Chapter {manga_id} {num} not found")
            raise Exception(f"Chapter {manga_id} {num} not found")
        
        self.chapters_data[manga_id][num] = data
        
        return data
    
    def get_chapter_id(self, manga_name, num, limit=1, language="en"):
        manga_id = self.get_manga_id(manga_name)
        data = self.get_chapter_data(manga_id, num, limit=limit, language=language)
        return data["id"]
    
    def get_chapter_image_urls(self, chapter_id, data_saver=1) -> list[str]:
        response = requests.get(f"{self.chapters_url}/{chapter_id}")
        response.raise_for_status()
        data = response.json()
        if not data:
            MM.show_message('error', f"Chapter {chapter_id} not found")
            raise Exception(f"Chapter {chapter_id} not found")
        chapter_data = data["chapter"]
        
        base_url = data["baseUrl"]
        _hash = chapter_data["hash"]
        image_ids = chapter_data["dataSaver" if data_saver else "data"]
            
        images_url = [f"{base_url}/{"data-saver" if data_saver else "data"}/{_hash}/{image_id}" for image_id in image_ids]
        
        return images_url
    
    def get_chapter_images(self, chapter_id, data_saver=1) -> list[bytes]:
        image_urls = self.get_chapter_image_urls(chapter_id, data_saver)
        images = []
        
        worker = BatchWorker()
        worker.signals.all_completed.connect(lambda _: MM.show_message('success', 'Images downloaded'))
        
        for image in worker.process_batch(requests.get, image_urls):
            images.append(image.content)
            
        return images
    
    def get_manga_chapter_images(self, manga_name, num, limit=1, data_saver=1, language="en") -> list[bytes]:
        manga_id = self.get_manga_id(manga_name)
        chapter_id = self.get_chapter_id(manga_id, num, limit=limit, language=language)
        return self.get_chapter_images(chapter_id, data_saver=data_saver)