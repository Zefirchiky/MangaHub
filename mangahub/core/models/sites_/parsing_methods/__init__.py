from .cover_parsing import CoverParsing
from .images_parsing import ImagesParsing
from .last_chapter_parsing import ChaptersListParsing
from .manga_chapter_parsing import MangaChapterParsing
from .manga_parsing import MangaParsing
from .name_parsing import NameParsing
from .novel_parsing import NovelParsing
from .parsing_method import ParsingMethod

__all__ = [
    'CoverParsing', 
	'ImagesParsing', 
	'ChaptersListParsing', 
	'MangaChapterParsing', 
	'MangaParsing', 
	'NameParsing', 
	'NovelParsing', 
	'ParsingMethod',
]