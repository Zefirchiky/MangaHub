from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, Slot
import sys
import json

class MangaDexApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MangaDex API with PySide6")
        self.setGeometry(300, 300, 400, 200)

        # Set up the main label to display the results
        self.result_label = QLabel("Fetching manga data...", self)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.result_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize the QNetworkAccessManager
        self.network_manager = QNetworkAccessManager()
        
        self.network_manager.finished.connect(self.handle_response)

        self.fetch_manga("nano machine")

    def fetch_manga(self, title):
        # Construct the URL for MangaDex API search
        url = f"https://api.mangadex.org/manga?title={title}"
        request = QNetworkRequest(QUrl(url))

        # Set a User-Agent header to prevent the server from rejecting the request
        request.setRawHeader(b"User-Agent", b"PySide6 MangaDex Client")

        # Send the GET request
        self.network_manager.get(request)


    @Slot("QNetworkReply*")
    def handle_response(self, reply: QNetworkReply):
        # Check for network errors and log details
        if not reply.error():
            error_code = reply.error()
            error_string = reply.errorString()
            print(reply)
            print(f"Error Code: {error_code}, Error Message: {error_string}")
            self.result_label.setText(f"Error: {error_string}")
            return

        # Parse JSON data if no errors
        data = reply.readAll().data()
        try:
            json_data = json.loads(data)
            if "data" in json_data:
                manga_title = json_data["data"][0]["attributes"]["title"]["en"]
                self.result_label.setText(f"Manga title: {manga_title}")
            else:
                self.result_label.setText("No results found.")
        except json.JSONDecodeError:
            self.result_label.setText("Error decoding JSON.")


# Running the application
app = QApplication(sys.argv)
window = MangaDexApp()
window.show()
sys.exit(app.exec())
