from PySide6.QtCore import Qt, QStringListModel, Signal
from PySide6.QtGui import QTextCursor, QKeyEvent, QTextCharFormat, QColor, QTextBlockUserData
from PySide6.QtWidgets import QTextEdit, QCompleter, QToolTip
import enchant

from domain.models.novels import NovelChapter, NovelParagraph


class NovelBlockData(QTextBlockUserData):
    def __init__(self, paragraph_id: int, novel_paragraph: NovelParagraph, tags: list=None):
        super().__init__()
        self.paragraph_id = paragraph_id
        self.paragraph = novel_paragraph
        self.tags = tags

class NovelTextEdit(QTextEdit):
    words_dict = enchant.Dict('en_US')
    current_word_ended = Signal(str, int, int)
    new_word_started = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        
        self.word_list = QStringListModel()
        self.word_list.setStringList(["mana", "lol", "manager"])

        self.completer = None
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setModel(self.word_list)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.replace_current_word)
        
        self._error_format = QTextCharFormat()
        self._error_format.setUnderlineColor(QColor("red"))
        self._error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)

        self.annotations = {}
        
        self.words = []
        self._current_word = ''
        self._previous_word = ''
        self._previous_word_start = 0
        self._previous_word_end = 0
        
        self._last_word_start = 0
        self._last_key_pressed = None
        self._current_word_escaped = False
        self._empty_word = True
        
        self._prev_cursor_pos = 0
        
        self._chapter = None

        self.textChanged.connect(self._text_changed)
        self.current_word_ended.connect(self._current_word_ended)
        self.new_word_started.connect(self._new_word_started)
        self.document().contentsChange.connect(self._content_document_changed)
        # self.document().blockCountChanged.connect(self._block_count_document_changed)

    def replace_current_word(self, word: str):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.insertText(
            word.capitalize()
            if cursor.selectedText() == cursor.selectedText().capitalize()
            else word
        )
        self.completer.popup().hide()
        
    def _content_document_changed(self, pos: int, chars_removed: int, chars_added: int):
        # print(f"\n--- Document changed at pos {pos}: removed {chars_removed} chars, added {chars_added} chars ---")
        if self.document().isEmpty():
            return
        
        if chars_added == chars_removed:
            # print('Formatting is done')
            # return
            pass
        
        removed_cursor = QTextCursor(self.textCursor())
        removed_cursor.setPosition(pos)
        if chars_removed:
            removed_cursor.setPosition(pos + chars_removed, QTextCursor.MoveMode.KeepAnchor)
        
        added_cursor = QTextCursor(self.textCursor())
        added_cursor.setPosition(pos)
        if chars_added:
            added_cursor.setPosition(pos + chars_added, QTextCursor.MoveMode.KeepAnchor)
        
        block = self.document().findBlock(pos)
        # print(block.blockNumber(), pos - block.position(), repr(removed_cursor.selectedText()), repr(added_cursor.selectedText()))
        if (block_data := block.userData()) and block_data.paragraph is not None:
            para: NovelParagraph = block_data.paragraph
            para.add_chars(pos, added_cursor.selectedText())
        else:
            para = self._chapter.get_data_repo().add(block.blockNumber(), NovelParagraph().add_chars(pos, added_cursor.selectedText()))
            block.setUserData(NovelBlockData(block.blockNumber(), para))
        # print(para)

    def _text_changed(self):
        cursor = self.textCursor()
        if self._prev_cursor_pos == cursor.position():
            return
        self._prev_cursor_pos = cursor.position()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        if (word := cursor.selectedText()):
            self._current_word = word
            if self._empty_word:
                self.new_word_started.emit(cursor.selectionStart())
                self._empty_word = False
                
            if len(word) >= 2 and not self._current_word_escaped:
                self.completer.setCompletionPrefix(word)
                cr = self.cursorRect()
                cr.setWidth(200)
                self.completer.complete(cr)
            else:
                self._current_word_escaped = False
                self.completer.popup().hide()
        
        else:
            if self._current_word:
                self._previous_word = self._current_word
                self._previous_word_start = cursor.position() - len(self._previous_word)
                self._previous_word_end = cursor.position()
                self.current_word_ended.emit(self._previous_word, self._previous_word_start, self._previous_word_end)
            self._empty_word = True
        
    def _new_word_started(self, start: int):
        pass
        
    def _current_word_ended(self, word: str, start: int, end: int):
        if not self.words_dict.check(word):
            cursor = QTextCursor(self.textCursor())
            cursor.setPosition(start - 1)
            cursor.setPosition(end - 1, QTextCursor.MoveMode.KeepAnchor)
            error = QTextCharFormat(self._error_format)
            cursor.mergeCharFormat(error)
            
    def load_chapter(self, chapter: NovelChapter):
        self._chapter = chapter
        self.setPlainText(chapter.text)
        for i in range(self.document().blockCount()):
            block = self.document().findBlockByNumber(i)
            block.setUserData(NovelBlockData(i, chapter.get_data_repo().get(i)))
    
    def keyPressEvent(self, event: QKeyEvent):
        if self.completer and self.completer.popup().isVisible():
            i = self.completer.popup().currentIndex()
            self._last_key_pressed = event.key()
            
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
                if i.isValid():
                    completion = self.completer.completionModel().data(i)
                    self.replace_current_word(completion)

                self.completer.popup().hide()
                event.accept()
                return True

            elif event.key() == Qt.Key.Key_Escape:
                self._current_word_escaped = True
                self.completer.popup().hide()
                event.accept()
                return True

            elif event.key() == Qt.Key.Key_Tab:
                down_event = QKeyEvent(
                    QKeyEvent.Type.KeyPress,
                    Qt.Key.Key_Down,
                    Qt.KeyboardModifier.NoModifier,
                )
                self.completer.popup().keyPressEvent(down_event)
                event.accept()
                return True

            elif event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                self.completer.popup().keyPressEvent()
                event.accept()
                return True

        return super().keyPressEvent(event)
