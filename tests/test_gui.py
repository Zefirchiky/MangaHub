import sys
from PySide6.QtWidgets import (
    QApplication, QTextEdit, QVBoxLayout, QWidget, QCompleter, QToolTip
)
from PySide6.QtGui import (
    QTextCursor, QTextCharFormat, QColor, QFont, QStringListModel, QKeyEvent
)
from PySide6.QtCore import (
    Qt, Signal, QRect, QEvent
)
import re # For robust word extraction

# Define user properties for different annotation types
USER_PROPERTY_NAME = QTextFormat.UserProperty + 1
USER_PROPERTY_DEFINITION_WORD = QTextFormat.UserProperty + 2
USER_PROPERTY_DEFINITION_TEXT = QTextFormat.UserProperty + 3
USER_PROPERTY_SENTENCE_TYPE = QTextFormat.UserProperty + 4
USER_PROPERTY_SPELL_ERROR_SUGGESTIONS = QTextFormat.UserProperty + 5

class CustomTextEditor(QTextEdit):
    nameClicked = Signal(str)
    wordDefinedClicked = Signal(str, str) # Emits (word, definition)
    sentenceTypeClicked = Signal(str, str) # Emits (sentence_text, type)
    spellErrorClicked = Signal(str, list) # Emits (word, suggestions)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.textChanged.connect(self._process_document_annotations)

        # --- Formats ---
        self._hover_format = QTextCharFormat()
        self._hover_format.setBackground(QColor("#e0e0ff"))
        self._hover_format.setFontUnderline(True)

        self._name_format = QTextCharFormat()
        self._name_format.setForeground(QColor("blue"))
        self._name_format.setFontWeight(QFont.Bold)

        self._defined_word_format = QTextCharFormat()
        self._defined_word_format.setForeground(QColor("purple"))
        self._defined_word_format.setFontUnderline(True)
        self._defined_word_format.setUnderlineStyle(QTextCharFormat.DashUnderline)

        self._error_format = QTextCharFormat()
        self._error_format.setUnderlineColor(QColor("red"))
        self._error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)

        # --- Data stores ---
        self.annotations = []
        self.user_dictionary = {
            "mana": "A supernatural energy or life force often associated with magic or spiritual power.",
            "quest": "A long or arduous search for something.",
            "dragon": "A mythical monster resembling a giant reptile, typically winged and scaly, with a crest and claws.",
            "hero": "A person who is admired or idealized for courage, outstanding achievements, or noble qualities.",
            "magic": "The power of apparently influencing the course of events by using mysterious or supernatural forces."
        }
        self.sentence_types = []

        self._current_hover_data = None
        self.viewport().setToolTip("")

        # --- QCompleter Setup ---
        self._completer = None
        self._setup_completer()

    def _setup_completer(self):
        # Create a model for the completer
        self._completion_model = QStringListModel(self)
        
        # Populate the model with words from your user_dictionary and potentially common words
        # For simplicity, let's use user_dictionary keys for now
        completion_words = sorted(list(self.user_dictionary.keys()) + ["story", "adventure", "ancient", "fantasy", "kingdom"])
        self._completion_model.setStringList(completion_words)

        self._completer = QCompleter(self)
        self._completer.setModel(self._completion_model)
        self._completer.setWidget(self) # The QCompleter needs to know which widget it's completing for
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        # Connect the completer's activated signal to a slot that inserts the text
        self._completer.activated.connect(self._insert_completion)

    def _insert_completion(self, completion_text: str):
        if self._completer.widget() is not self:
            return # Ensure the completer is for THIS text edit

        tc = self.textCursor()
        extra = len(completion_text) - len(self._completer.completionPrefix())
        
        # Move cursor back to the start of the completion prefix
        # This is crucial for replacing the partial word
        for _ in range(len(self._completer.completionPrefix())):
            tc.deletePreviousChar()
        
        tc.insertText(completion_text)
        self.setTextCursor(tc) # Update the text cursor in the editor

    def event(self, event: QEvent) -> bool:
        # This is a key event filter to handle completer interactions
        if event.type() == QEvent.Type.KeyPress and self._completer and self._completer.popup().isVisible():
            # If the completer popup is visible and certain keys are pressed,
            # let the completer handle them (e.g., Up/Down arrows, Enter, Tab)
            key = event.key()
            if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                event.ignore() # Let completer handle these directly
                return True # Event handled

        return super().event(event) # Pass other events to base class

    def keyPressEvent(self, event: QKeyEvent):
        # If completer popup is visible, and it's a key that completer should handle,
        # pass it to the completer directly.
        if self._completer and self._completer.popup().isVisible() and \
           event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, Qt.Key.Key_Tab, Qt.Key.Key_Backtab, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self._completer.eventFilter(self, event) # Let completer process the event
            return # Don't process in QTextEdit

        # If it's a normal key press, let the base class handle it first
        super().keyPressEvent(event)

        # After the key is processed, check for autocompletion
        completion_prefix = self._get_current_word_prefix()
        if self._completer and len(completion_prefix) >= 2: # Trigger after 2 or more characters
            self._completer.setCompletionPrefix(completion_prefix)
            popup = self._completer.popup()
            if popup.isHidden():
                # Position the popup
                cr = self.cursorRect() # Rectangle of the cursor
                cr.setWidth(self._completer.popup().sizeHint().width()) # Make it wide enough for suggestions
                self._completer.complete(cr) # Show the completer popup
            elif not popup.isHidden() and self._completer.completionModel().rowCount() == 0:
                self._completer.popup().hide() # Hide if no completions
        else:
            self._completer.popup().hide() # Hide if prefix is too short or no completer

    def _get_current_word_prefix(self) -> str:
        """
        Extracts the word prefix directly before the cursor.
        This is crucial for the completer.
        """
        tc = self.textCursor()
        original_pos = tc.position()

        # Move to the start of the current word
        tc.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        start_of_word_pos = tc.position()

        # Move cursor back to original position, then select to the left to get the prefix
        tc.setPosition(original_pos)
        tc.setPosition(start_of_word_pos, QTextCursor.KeepAnchor)
        
        # Get the selected text, which is the prefix
        prefix = tc.selectedText()
        
        # Restore cursor
        tc.setPosition(original_pos)
        self.setTextCursor(tc)

        # Only alphanumeric characters for a word prefix, handle punctuation
        # Use regex to get only the word part
        match = re.search(r'([\w\']+)?$', prefix) # Matches word chars or apostrophe at the end
        if match:
            return match.group(1) or ""
        return ""

    # (Rest of your CustomTextEditor class methods: _process_document_annotations,
    # _detect_names, _detect_sentences, _check_spelling, mouseMoveEvent,
    # mousePressEvent, _get_annotation_at_position, etc. - copy from previous example)

    def _process_document_annotations(self):
        # Your existing annotation processing logic
        doc = self.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()

        self.annotations = []
        entire_doc_cursor = QTextCursor(doc)
        entire_doc_cursor.select(QTextCursor.Document)
        entire_doc_cursor.setCharFormat(QTextCharFormat())

        text = self.toPlainText()

        detected_names = self._detect_names(text)
        for name_text, start_index, end_index in detected_names:
            cursor.setPosition(start_index)
            cursor.setPosition(end_index, QTextCursor.KeepAnchor)
            name_format = QTextCharFormat(self._name_format)
            name_format.setProperty(USER_PROPERTY_NAME, name_text)
            cursor.mergeCharFormat(name_format)
            self.annotations.append({
                "type": "name", "text": name_text, "start": start_index, "end": end_index, "data": {"name": name_text}
            })

        for word, definition in self.user_dictionary.items():
            start_pos = 0
            while True:
                start = text.find(word, start_pos)
                if start == -1: break
                end = start + len(word)
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                defined_word_format = QTextCharFormat(self._defined_word_format)
                defined_word_format.setProperty(USER_PROPERTY_DEFINITION_WORD, word)
                defined_word_format.setProperty(USER_PROPERTY_DEFINITION_TEXT, definition)
                cursor.mergeCharFormat(defined_word_format)
                self.annotations.append({
                    "type": "defined_word", "text": word, "start": start, "end": end, "data": {"word": word, "definition": definition}
                })
                start_pos = end

        sentences = self._detect_sentences(text)
        for sentence_text, sent_type, start, end in sentences:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            sentence_format = QTextCharFormat()
            if sent_type == "speech": sentence_format.setForeground(QColor("darkgreen")); sentence_format.setFontItalic(True)
            elif sent_type == "thought": sentence_format.setForeground(QColor("gray"))
            else: sentence_format.setForeground(QColor("black"))
            sentence_format.setProperty(USER_PROPERTY_SENTENCE_TYPE, sent_type)
            cursor.mergeCharFormat(sentence_format)
            self.annotations.append({
                "type": "sentence_type", "text": sentence_text, "start": start, "end": end, "data": {"type": sent_type}
            })

        errors = self._check_spelling(text)
        for word_text, start_index, end_index, suggestions in errors:
            cursor.setPosition(start_index)
            cursor.setPosition(end_index, QTextCursor.KeepAnchor)
            error_format = QTextCharFormat(self._error_format)
            error_format.setProperty(USER_PROPERTY_SPELL_ERROR_SUGGESTIONS, suggestions)
            cursor.mergeCharFormat(error_format)
            self.annotations.append({
                "type": "spell_error", "text": word_text, "start": start_index, "end": end_index, "data": {"suggestions": suggestions}
            })

        cursor.endEditBlock()
    
    def _detect_names(self, text):
        names = []
        if "John Doe" in text:
            start = text.find("John Doe")
            names.append(("John Doe", start, start + len("John Doe")))
        if "Jane Smith" in text:
            start = text.find("Jane Smith")
            names.append(("Jane Smith", start, start + len("Jane Smith")))
        return names

    def _detect_sentences(self, text):
        sentences = []
        import re
        sentence_regex = re.compile(r'([.?!])\s*')
        parts = sentence_regex.split(text)
        
        current_pos = 0
        for i in range(0, len(parts), 2):
            sentence_fragment = parts[i]
            if i + 1 < len(parts):
                terminator = parts[i+1]
            else:
                terminator = ""
            
            full_sentence = sentence_fragment + terminator
            
            sent_type = "narration"
            if "“" in sentence_fragment or "\"" in sentence_fragment:
                sent_type = "speech"
            elif "..." in sentence_fragment:
                sent_type = "thought"

            start_index = current_pos
            end_index = start_index + len(full_sentence)
            sentences.append((full_sentence.strip(), sent_type, start_index, end_index))
            current_pos = end_index + len(terminator.strip())
        return sentences

    def _check_spelling(self, text):
        try:
            import enchant
            d = enchant.Dict("en_US")
            errors = []
            words = re.findall(r'\b\w+\b', text) # More robust word split
            current_idx = 0
            for word in words:
                start = text.find(word, current_idx)
                end = start + len(word)
                if not d.check(word):
                    suggestions = d.suggest(word)
                    errors.append((word, start, end, suggestions))
                current_idx = end
            return errors
        except ImportError:
            print("PyEnchant not installed. Spell checking disabled.")
            return []

    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())

        if self._current_hover_data and \
            (not self._get_annotation_at_position(cursor.position()) or \
            self._get_annotation_at_position(cursor.position())["start"] != self._current_hover_data["start"]):
            doc = self.document()
            temp_cursor = QTextCursor(doc)
            temp_cursor.setPosition(self._current_hover_data["start"])
            temp_cursor.setPosition(self._current_hover_data["end"], QTextCursor.KeepAnchor)
            
            original_format = QTextCharFormat()
            if self._current_hover_data["type"] == "name":
                original_format = QTextCharFormat(self._name_format)
            elif self._current_hover_data["type"] == "defined_word":
                original_format = QTextCharFormat(self._defined_word_format)
            elif self._current_hover_data["type"] == "spell_error":
                original_format = QTextCharFormat(self._error_format)
            
            temp_cursor.mergeCharFormat(original_format)
            self._current_hover_data = None
            QToolTip.hideText()

        annotation_data = self._get_annotation_at_position(cursor.position())

        if annotation_data:
            doc = self.document()
            temp_cursor = QTextCursor(doc)
            temp_cursor.setPosition(annotation_data["start"])
            temp_cursor.setPosition(annotation_data["end"], QTextCursor.KeepAnchor)
            temp_cursor.mergeCharFormat(self._hover_format)
            self._current_hover_data = annotation_data

            self.setCursor(Qt.PointingHandCursor)

            if annotation_data["type"] == "defined_word":
                QToolTip.showText(event.globalPos(), annotation_data["data"]["definition"], self)
            elif annotation_data["type"] == "spell_error":
                suggestions_str = ", ".join(annotation_data["data"]["suggestions"])
                QToolTip.showText(event.globalPos(), f"Possible corrections: {suggestions_str}", self)
            return

        self.unsetCursor()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            annotation_data = self._get_annotation_at_position(cursor.position())

            if annotation_data:
                if annotation_data["type"] == "name":
                    self.nameClicked.emit(annotation_data["text"])
                elif annotation_data["type"] == "defined_word":
                    self.wordDefinedClicked.emit(annotation_data["text"], annotation_data["data"]["definition"])
                elif annotation_data["type"] == "sentence_type":
                    self.sentenceTypeClicked.emit(annotation_data["text"], annotation_data["data"]["type"])
                elif annotation_data["type"] == "spell_error":
                    self.spellErrorClicked.emit(annotation_data["text"], annotation_data["data"]["suggestions"])
                event.accept()
                return

        super().mousePressEvent(event)

    def _get_annotation_at_position(self, position):
        for annotation in self.annotations:
            if annotation["start"] <= position < annotation["end"]:
                return annotation
        return None

# Example usage in MainWindow (same as before)
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Novel Editor with Auto-completion")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.text_editor = CustomTextEditor()
        self.text_editor.setPlainText(
            "Hello, my name is John Doe. This is a quest for ancient mana. "
            "“Are you ready?” she said. It was a long journey... "
            "I wonder what comes next... I can't belive this is happening! "
            "The ancient dragn waited. This is an eror word. Let's talk about magic."
        )

        self.text_editor.nameClicked.connect(self.handle_name_click)
        self.text_editor.wordDefinedClicked.connect(self.handle_defined_word_click)
        self.text_editor.sentenceTypeClicked.connect(self.handle_sentence_type_click)
        self.text_editor.spellErrorClicked.connect(self.handle_spell_error_click)

        layout.addWidget(self.text_editor)
        self.setLayout(layout)

    def handle_name_click(self, name):
        print(f"Clicked on name: {name}")

    def handle_defined_word_click(self, word, definition):
        print(f"Clicked on defined word '{word}': {definition}")

    def handle_sentence_type_click(self, sentence, sent_type):
        print(f"Clicked on sentence ('{sentence}') of type: {sent_type}")

    def handle_spell_error_click(self, word, suggestions):
        print(f"Clicked on misspelled word '{word}'. Suggestions: {suggestions}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())