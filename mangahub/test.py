from models.novels import NovelFormatter
from services.scrapers import NovelsSiteScraper
# import re


# novel = NovelFormatter(NovelsSiteScraper.get_temp_novel_text())
# novel.get_novel_chapter()


import re
from pydantic import BaseModel
from typing import List, Union, Optional, Pattern

class Paragraph(BaseModel):
    parts: List[Union['Speech', 'Thought', 'UnclearReference', 'Sound', 'SystemSpeech', 'Narration']]

class Speech(BaseModel):
    content: str
    parts: List[Union['UnclearReference', 'Sound']] = []

class Thought(BaseModel):
    content: str

class UnclearReference(BaseModel):
    content: str

class Sound(BaseModel):
    content: str

class SystemSpeech(BaseModel):
    content: str

class Narration(BaseModel):
    content: str
    parts: List[Union[UnclearReference, Sound]] = []

class NovelChapter(BaseModel):
    paragraphs: List[Paragraph] = []

Paragraph.model_rebuild()
Speech.model_rebuild()
Narration.model_rebuild()

class ChapterFormatter:
    def __init__(self):
        self.symbol_replacements = {
            '…': '...',
            '‖': '||'
        }
        self.paragraph_break_re = re.compile(r'\n\s*\n')
        self.element_patterns = [
            (SystemSpeech, re.compile(r'\[(.*?)\]', re.DOTALL)),
            (Sound, re.compile(r'\*\*(.*?)\*\*')),
            (Speech, re.compile(r'"((?:[^"\\]|\\.)*)"', re.DOTALL)),
        ]
        self.special_patterns = [
            (Sound, re.compile(r'\*\*(.*?)\*\*')),
            (UnclearReference, re.compile(r'\'(.*?)\''))
        ]

    def format(self, raw_text: str) -> NovelChapter:
        raw_text = self._replace_symbols(raw_text)
        raw_paragraphs = self._split_into_paragraphs(raw_text)
        novel_chapter = NovelChapter()
        for raw_para in raw_paragraphs:
            paragraph = Paragraph(parts=[])
            remaining_text = raw_para.strip()
            while remaining_text:
                found = False
                for elem_type, pattern in self.element_patterns:
                    match = pattern.search(remaining_text)
                    if match and match.start() == 0:
                        content = self._clean_content(match.group(1))
                        if elem_type == Speech:
                            nested = self._parse_special(content)
                            elem = Speech(content=content, parts=nested)
                        elif elem_type == SystemSpeech:
                            elem = SystemSpeech(content=content)
                        elif elem_type == Sound:
                            elem = Sound(content=content)
                        else:
                            elem = elem_type(content=content)
                        paragraph.parts.append(elem)
                        remaining_text = remaining_text[match.end():].lstrip()
                        found = True
                        break
                if not found:
                    thought_match = re.search(r'\'(.*?)\'', remaining_text)
                    if thought_match:
                        before_text = remaining_text[:thought_match.start()].strip()
                        if before_text:
                            narration = self._create_narration(before_text)
                            paragraph.parts.append(narration)
                        thought_content = self._clean_content(thought_match.group(1))
                        paragraph.parts.append(Thought(content=thought_content))
                        remaining_text = remaining_text[thought_match.end():].lstrip()
                        found = True
                    else:
                        narration = self._create_narration(remaining_text)
                        paragraph.parts.append(narration)
                        remaining_text = ''
            novel_chapter.paragraphs.append(paragraph)
        return novel_chapter

    def _create_narration(self, text: str) -> Narration:
        content = self._clean_content(text)
        parts = []
        remaining = content
        while remaining:
            found = False
            for elem_type, pattern in self.special_patterns:
                match = pattern.search(remaining)
                if match:
                    before = remaining[:match.start()].strip()
                    if before:
                        parts.append(Narration(content=before))
                    parts.append(elem_type(content=self._clean_content(match.group(1))))
                    remaining = remaining[match.end():].lstrip()
                    found = True
                    break
            if not found:
                if remaining.strip():
                    parts.append(Narration(content=remaining.strip()))
                remaining = ''
        return Narration(content=content, parts=parts)

    def _parse_special(self, content: str) -> list:
        parts = []
        remaining = content
        while remaining:
            found = False
            for elem_type, pattern in self.special_patterns:
                match = pattern.search(remaining)
                if match:
                    before = remaining[:match.start()]
                    if before:
                        parts.append(Narration(content=before))
                    parts.append(elem_type(content=self._clean_content(match.group(1))))
                    remaining = remaining[match.end():]
                    found = True
                    break
            if not found:
                if remaining:
                    parts.append(Narration(content=remaining))
                remaining = ''
        return parts

    def _split_into_paragraphs(self, text: str) -> List[str]:
        lines = text.split('\n')
        paragraphs = []
        current_para = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_para:
                    paragraphs.append('\n'.join(current_para))
                    current_para = []
            else:
                if current_para and self._should_merge(current_para[-1], stripped):
                    current_para.append(stripped)
                else:
                    if current_para:
                        paragraphs.append('\n'.join(current_para))
                    current_para = [stripped]
        if current_para:
            paragraphs.append('\n'.join(current_para))
        return paragraphs

    def _should_merge(self, last_line: str, current_line: str) -> bool:
        if not last_line:
            return False
        if re.match(r'^[a-z]', current_line):
            return True
        if last_line.endswith(('"', "'")) and current_line.startswith(('"', "'")):
            return True
        return False

    def _replace_symbols(self, text: str) -> str:
        for old, new in self.symbol_replacements.items():
            text = text.replace(old, new)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _clean_content(self, content: str) -> str:
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    

with open('test.txt', 'r', encoding='utf-8') as f:
    text = f.read()
formatter = ChapterFormatter()
print(formatter.format(text))