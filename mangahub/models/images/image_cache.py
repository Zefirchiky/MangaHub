import os
from pathlib import Path
from queue import SimpleQueue
from resources.enums import SU, StorageSize
from config import Config


class ImageCache:  # TODO: SAVE/LOAD
    def __init__(
        self,
        cache_path: Path,
        max_ram: int | StorageSize = 100 * SU.MB,
        max_disc: int | StorageSize = 500 * SU.MB,
    ):
        self.cache_path = cache_path

        self.max_ram = StorageSize(max_ram)
        self.max_disc = StorageSize(max_disc)

        self.cur_ram = StorageSize()
        self.cur_disc = StorageSize()

        self._ram_name_history = SimpleQueue()
        self._disc_name_history = SimpleQueue()
        self._freed_from_ram = {}
        self._ram_cache = {}
        self._disc_cache = {}
        self._freed_ram_data_bytes = StorageSize()

    def _free_ram(self, bytes_to_free: StorageSize) -> None:
        while self.free_ram < bytes_to_free:  # While free ram is less that requested
            old_item = self._ram_name_history.get()
            self._freed_from_ram[old_item] = self._ram_cache.pop(old_item)
            self._freed_ram_data_bytes += bytes_to_free
            self.cur_ram -= self._freed_from_ram[old_item][1]  # Free oldest image

    def _free_disc(self, bytes_to_free: StorageSize):
        while self.max_disc - self.cur_disc < bytes_to_free:
            file, size = self._disc_cache.pop(self._disc_name_history.get())
            self.cur_disc -= size
            os.remove(file)

    def add(self, name: str, image: bytes, size_: int):
        size: StorageSize = StorageSize(size_)
        if self.max_ram < size:  # If image larger that maximum ram available
            self._free_ram(self.max_ram)  # Free all ram
            self._freed_from_ram[name] = [image, size]
            self._freed_ram_data_bytes += size
        else:
            if (
                self.cur_ram + size >= self.max_ram
            ):  # If image takes more that ram available
                self._free_ram(size)
            self._ram_cache[name] = [image, size]
            self._ram_name_history.put(name)
            self.cur_ram += size

        if self._freed_from_ram:  # If files where moved from ram
            if (
                self.cur_disc + self._freed_ram_data_bytes >= self.max_disc
                and self.max_disc >= self._freed_ram_data_bytes
            ):  # If file takes more that disc space available
                self._free_disc(self._freed_ram_data_bytes)

            for name, (bytes, size) in self._freed_from_ram.items():
                cached_image_path = self.cache_path / name
                with open(cached_image_path, "wb") as f:
                    f.write(bytes)

                self._disc_cache[name] = [cached_image_path, size]
                self._disc_name_history.put(name)
                self.cur_disc += size

            self._freed_ram_data_bytes = 0
            self._freed_from_ram = {}

    def get(self, name: str, default=None) -> bytes:  # TODO: Set image as recently used
        if image := self._ram_cache.get(name, default):
            return image[0]
        elif image := self._disc_cache.get(name, default):
            with open(image[0], "rb") as f:
                return f.read()  # Possibility of async chunk loading
        else:
            raise Exception(f"{name} was not found in cache")
        
    def pop(self, name: str, default=None) -> bytes:
        if image := self._ram_cache.pop(name, default):
            self.cur_ram -= image[1]
            return image[0]
        elif image := self._disc_cache.pop(name, default):
            self.cur_disc -= image[1]
            with open(image[0], 'rb') as f:
                return f.read()
        else:
            raise Exception(f"{name} was not found in cache")

    @property
    def free_ram(self) -> StorageSize:
        return self.max_ram - self.cur_ram

    @property
    def free_disc(self) -> StorageSize:
        return self.max_disc - self.cur_disc

    def save_image(self, name: str, path: Path = Config.Dirs.IMAGES_CACHE):
        path.mkdir(exist_ok=True)
        with open(path / name, "wb") as f:
            f.write(self.get(name))
