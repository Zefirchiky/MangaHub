import requests
import io

from PIL import Image

from gui.gui_utils import MM
from utils import BatchWorker, convert_to_format


class MangaDexScraper:
    def __init__(self):
        self.base_api_url = "https://api.mangadex.org"
        self.base_upload_url = "https://uploads.mangadex.org"
        
        self.manga_url = f"{self.base_api_url}/manga"
        self.cover_id_url = f"{self.base_api_url}/cover"
        self.cover_url = f"{self.base_upload_url}/covers"
        self.chapter_url = f"{self.base_api_url}/chapter"
        self.chapter_images_url = f"{self.base_api_url}/at-home/server"
        
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
        data = response.json()["data"]
        if data:
            manga = data[0]
            self.manga_data[name] = manga
            return manga
        
        MM.show_message('warning', f"Manga {name} not found on MangaDex")
        return None
    
    def get_manga_id(self, name):
        data = self.get_manga_data(name)
        if not data:
            return None
        return data["id"]
    
    def get_manga_cover_filename(self, manga_id):
        response = requests.get(f"{self.cover_id_url}", params={"manga[]": manga_id})
        data = response.json()["data"]
        if not data:
            MM.show_message('error', f"Manga {manga_id} not found")
            return None
        return data[0]["attributes"]["fileName"]
    
    def get_manga_cover(self, name):
        manga_id = self.get_manga_id(name)
        manga_cover_id = self.get_manga_cover_filename(manga_id)
        response = requests.get(f"{self.cover_url}/{manga_id}/{manga_cover_id}")
        response.raise_for_status()
        return convert_to_format(response.content)
    
    def get_all_chapters(self, manga_id, language="en"):
        params = {
            "translatedLanguage[]": language
        }
        
        response = requests.get(f"{self.manga_url}/{manga_id}/feed", params=params)
        response.raise_for_status()
        data = response.json()["data"]
        return data
    
    def get_last_chapter_num(self, manga_id, language="en"):
        if not self.chapters_data.get(manga_id):
            self.chapters_data[manga_id] = {}
            
        params = {
            "manga": manga_id,
            "translatedLanguage[]": language,
            "order[chapter]": "desc",
            "limit": 1
        }
        
        response = requests.get(self.chapter_url, params=params)
        response.raise_for_status()
        data = response.json()["data"][0]
        num = int(data['attributes']['chapter'])
        
        self.chapters_data[manga_id][num] = data
        
        return num
                
    def get_chapter_data(self, manga_id, num, limit=1, language="en"):
        if not self.chapters_data.get(manga_id):
            self.chapters_data[manga_id] = {}
            
        if manga_id in self.chapters_data.keys():
            if num in self.chapters_data[manga_id].keys():
                return self.chapters_data[manga_id][num]
            
        params = {
            "manga": manga_id,
            "translatedLanguage[]": language,
            "chapter": num,
            "limit": limit
        }
        
        response = requests.get(self.chapter_url, params=params)
        response.raise_for_status()
        data = response.json()["data"]
        if data:
            data = data[0]
            return data
        self.chapters_data[manga_id][num] = data
        
        MM.show_message('error', f"Chapter {manga_id} {num} not found on MangaDex")
        return None
    
    def get_chapter_name(self, manga_id, num):
        data = self.get_chapter_data(manga_id, num)
        return data["attributes"]["title"] if data else None
    
    def get_chapter_id(self, manga_id, num, limit=1, language="en"):
        data = self.get_chapter_data(manga_id, num, limit=limit, language=language)
        return data["id"] if data else None
    
    def get_chapter_upload_date(self, manga_id, num):
        data = self.get_chapter_data(manga_id, num)
        return data["attributes"]["publishAt"] if data else None
    
    def get_chapter_image_urls(self, chapter_id, data_saver=1) -> list[str]:
        response = requests.get(f"{self.chapter_images_url}/{chapter_id}")
        response.raise_for_status()
        data = response.json()
        if not data:
            MM.show_message('error', f"Chapter {chapter_id} not found")
            return []
        chapter_data = data["chapter"]
        
        base_url = data["baseUrl"]
        _hash = chapter_data["hash"]
        image_ids = chapter_data["dataSaver" if data_saver else "data"]
        
        worker = BatchWorker()
        image_urls = worker.process_batch(lambda x: f"{base_url}/data-saver/{_hash}/{x}", image_ids, blocking=True)
                    
        return image_urls
    
    def get_image_size(self, url):
        headers = {"Range": "bytes=0-1023"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        image = Image.open(io.BytesIO(response.content))
        return image.size

    def get_chapter_placeholders(self, chapter_id, data_saver=1):
        image_urls = self.get_chapter_image_urls(chapter_id, data_saver)
        placeholders_worker = BatchWorker()
        placeholders_worker.signals.all_completed.connect(lambda _: MM.show_message('success', "Image sizes downloaded"))
        return list(placeholders_worker.process_batch(self.get_image_size, image_urls, blocking=True))
    
    def start_chapter_images_download(self, chapter_id, data_saver=1):
        image_urls = self.get_chapter_image_urls(chapter_id, data_saver)
        images_worker = BatchWorker()
        images_worker.signals.all_completed.connect(lambda _: MM.show_message('success', "Images downloaded"))
        images_worker.process_batch(requests.get, image_urls, blocking=False)
        return images_worker
