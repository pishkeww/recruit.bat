from PyQt6.QtWidgets import QPushButton, QFileDialog


class FileUploadButton(QPushButton):
    def __init__(self, callback):
        super().__init__("Upload Resume (PDF)")
        self.callback = callback
        self.clicked.connect(self.open_file)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume",
            "",
            "PDF Files (*.pdf)"
        )

        if file_path:
            self.callback(file_path)