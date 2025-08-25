import re

from .novel_chapter import NovelChapter
from .novel_paragraph import NovelParagraph
# from .novel_sentence import Dialog, Narration, Thought, UnclearReference

MULTILINE_PLACEHOLDER = "⏎"


class NovelFormatter:
    global_replaces = {}

    def __init__(self, text: str) -> None:
        self.text = text

        self.is_dialog = False
        self.dialog = None

        self.regex = (
            r'(".*?")|'  # Double quotes
            r"((?:^|(?<=[^a-zA-Z0-9] ))'.*?'(?= |$))|"  # Single quotes
            r"((?<= )'.*?'(?= ))"  # Single quotes inside a sentence
        )

    def get_novel_chapter(self) -> NovelChapter:
        self.text = self._chapter_symbols_replaces(self.text)
        raw_paragraphs = self.text.split("\n")
        self.text = self._fix_new_lines(raw_paragraphs)

        paragraphs: list[NovelParagraph] = []
        for paragraph in raw_paragraphs:
            paragraph = self.format_paragraph("\n" + paragraph + "\n")

            paragraphs.append(paragraph)

    def format(self, raw_text: str) -> NovelParagraph:
        text = self._chapter_symbols_replaces(raw_text)
        text, _ = self._preserve_line_breaks(text)
        return text

    def _fix_new_lines(self, text: list[str]) -> str:
        prev = ""
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
                    merge = True
                elif p[0].isspace():
                    merge = True
                elif p[0].islower():  # if it's not the start of the sentence
                    p = " " + p
                    merge = True

                elif prev and prev[-1] in [".", "?", "!", ":", '"', "'"]:
                    if prev[-1] in [","]:
                        p = " " + p
                        merge = True
                    elif p[0].isalnum():
                        p = " " + p[0].lower() + p[1:]
                        merge = True

            if merge and prev:
                prev += p
                text[i - 1] = prev
                text.pop(i)
            else:
                i += 1
                prev = p

        return text

    def _preserve_line_breaks(self, text: str) -> str | list[int]:
        """Replace newlines in quotes with placeholder"""
        in_quote = None
        result = []
        line_break_positions = []
        current_line_length = 0

        for c in text:
            if c in ('"', "'"):
                if in_quote == c:
                    in_quote = None
                else:
                    in_quote = c
                result.append(c)
            elif c == "\n" and in_quote:
                result.append(MULTILINE_PLACEHOLDER)
                line_break_positions.append(current_line_length)
            else:
                result.append(c)
                current_line_length += 1

        return "".join(result), line_break_positions

    def _chapter_symbols_replaces(self, text: str) -> str:
        text = text.translate(self.global_replaces)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)  # remove spaces before punctuation
        return text
