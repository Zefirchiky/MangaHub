from abc import ABC, abstractmethod
from pathlib import Path
from loguru import logger


class FileHandler[LV, SV](ABC):
    def __init__(self, file: Path | str, ext: str=''):
        """
        Initialize the FileHandler with a file and an extension.

        If the file does not exist, create it and call the `_create_empty` method to populate it.

        If the file is a string and does not end with the extension, add the extension to the file name.

        :param file: The file to use.
        :type file: Path or str
        :param ext: The file extension to use.
        :type ext: str
        """
        
        if isinstance(file, str):
            if ext and not file.endswith(ext):
                logger.warning(f"File '{file}' is not a '{ext}'. '{file}{ext}' will be handled instead")
                file += ext
            file = Path(file)
        else:
            if file.suffix != ext:
                logger.warning(f"File '{file}' is not a '{ext}'. '{file}{ext}' will be handled instead")
                file = Path(str(file) + ext)
            
        if not file.exists():
            path = file.parent
            path.mkdir(exist_ok=True)
            self._create_empty(file)
            
        self.file = file
        self.data = None

    def _create_empty(self, file: Path):
        """
        Create an empty file.

        This method is called if the file does not exist.
        
        It is not recommended to use `super()._create_empty(file)`.

        :param file: The file to create.
        :type file: Path
        """
        with file.open('w'):
            pass

    @abstractmethod
    def load(self) -> LV:
        """
        Abstract method to load data from the file.

        This method should be implemented by subclasses to define the logic
        for reading data from the file. The implementation should read the
        contents of the file and return it in the appropriate form defined
        by the `LoadValue` type.

        :return: Data loaded from the file.
        :rtype: LoadValue
        """

        pass
    
    def get(self) -> LV:
        """
        Get the data from the file.

        If the data is not loaded, load it first.

        :return: Data loaded from the file.
        :rtype: LoadValue
        """
        if not self.data:
            self.data = self.load()
        return self.data

    @abstractmethod
    def save(self, data: SV):
        """
        Abstract method to save data to the file.

        This method should be implemented by subclasses to define the logic
        for writing data to the file. The implementation should take the
        `data` parameter and write it to the file in the appropriate form
        defined by the `SaveValue` type.

        :param data: Data to be saved to the file.
        :type data: SaveValue
        """
        pass
    
    @classmethod
    def fast_load(cls, file: Path | str) -> LV:
        """
        Load data from a file using a single call.

        This method provides a quick way to load data from a file without
        needing to instantiate the class explicitly. It creates an instance
        of the class with the provided file and calls the `load` method to
        retrieve the data.

        :param file: The file from which to load data.
        :type file: Path or str
        :return: Data loaded from the file.
        :rtype: LoadValue
        """
        
        return cls(file).load()
    
    @classmethod
    def fast_save(cls, file: Path | str, data: SV):
        """
        Save data to a file using a single call.

        This method provides a quick way to save data to a file without
        needing to instantiate the class explicitly. It creates an instance
        of the class with the provided file and calls the `save` method to
        write the data.

        :param file: The file to which data will be saved.
        :type file: Path or str
        :param data: The data to be saved to the file.
        :type data: SaveValue
        """
        
        cls(file).save(data)
        
    
    def __len__(self) -> int:
        return len(self.get())