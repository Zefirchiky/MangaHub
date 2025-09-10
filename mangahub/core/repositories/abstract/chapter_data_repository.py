from abc import ABC
from application.services.parsers import TagModelsJsonParser


class ChapterDataRepository[KT, DT](ABC, TagModelsJsonParser[KT, DT]):
    pass