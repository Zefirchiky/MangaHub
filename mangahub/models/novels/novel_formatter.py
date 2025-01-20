import re

from .novel_chapter import NovelChapter
from .novel_paragraph import NovelParagraph
from .paragraph import Dialog, Thought, UnclearReference, Narration


class NovelFormatter:
    def __init__(self, text: str) -> None:
        self.text = text
        
        self.is_dialog = False
        self.dialog = None
        
        self.regex = (
            r'(".*?")|'                                     # Double quotes
            r"((?:^|(?<=[^a-zA-Z0-9] ))'.*?'(?= |$))|"      # Single quotes
            r"((?<= )'.*?'(?= ))"                           # Single quotes inside a sentence
        )
        
    def get_novel_chapter(self) -> NovelChapter:
        self.text = self._chapter_symbols_replaces(self.text)
        raw_paragraphs = self.text.split("\n")
        self.text = self._fix_new_lines(raw_paragraphs)
        
        paragraphs: list[NovelParagraph] = []
        for paragraph in raw_paragraphs:            
            paragraph = self.format_paragraph("\n" + paragraph + "\n")
            
            paragraphs.append(paragraph)
            
    def format_paragraph(self, raw_paragraph: str) -> NovelParagraph:        
        paragraph = NovelParagraph()
        prev_end = 0
        
        for m in re.finditer(self.regex, raw_paragraph, re.MULTILINE):
            if m.start() > prev_end + 1:
                paragraph.elements.append(Narration(text=raw_paragraph[prev_end+1:m.start()-1]))
            if m.group(1):
                paragraph.elements.append(Dialog(text=m.group(1)))
            elif m.group(2):
                paragraph.elements.append(Thought(text=m.group(2)))
            elif m.group(3):
                paragraph.elements.append(UnclearReference(text=m.group(3)))
            prev_end = m.end()
        
        if prev_end + 1 < len(raw_paragraph):
            paragraph.elements.append(Narration(text=raw_paragraph[prev_end:]))
        
        paragraph.validate_elements()
        return paragraph
    
    def _fix_new_lines(self, text: list[str]) -> str:
        prev = ''
        i = 0
        while i < len(text):
            p = text[i]
            if not p or p.isspace() or p == "\n":
                text.pop(i)
                continue
            
            not_merge = False
            # if p[0] in ['"', "'"] and p[-1] in ['"', "'"] and len(p) >= 1:
            #     not_merge = True
            
            merge = False
            if not not_merge:
                if (p == '"' or p == "'") and len(p) == 1:
                    print(f'Merging "{p}" with "{prev}"')
                    merge = True
                elif p[0].isspace():
                    merge = True
                elif p[0].islower():      # if it's not the start of the sentence
                    p = ' ' + p
                    merge = True
                    
                elif prev and prev[-1] in ['.', '?', '!', ':', '"', "'"]:
                    if prev[-1] in [',']:
                        p = ' ' + p
                        merge = True
                    elif p[0].isalnum():
                        p = ' ' + p[0].lower() + p[1:]
                        merge = True
                
            if merge and prev:
                prev += p
                text[i-1] = prev
                text.pop(i)
            else:
                i += 1
                prev = p
                
        return text
    
    def _chapter_symbols_replaces(self, text: str) -> str:
        return text.replace(
            '…', '...'
        )