from abc import ABC
from application.services.parsers import TagModelsJsonParser


class ChapterDataRepository[KeyType, DataType](ABC, TagModelsJsonParser[KeyType, DataType]):
    pass